"""Authoritative scene transactions shared by the UI, MCP and WebMCP.

Recipes contain data only. No code, expressions, callbacks or filesystem paths
are accepted by any public command. This module has no web/protocol dependency.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from geometry.choreography import sample_parameters, validate_keyframes
from studio.transforms import resolve_islands, transformed_islands
from studio.layout import laid_out_islands
from studio.retiming import RetimeError, retimed_islands, scaled_islands


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)


class PatchModel(StrictModel):
    """Omission means unchanged; explicit null is never a valid patch value."""

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, values):
        if isinstance(values, dict) and any(value is None for value in values.values()):
            raise ValueError("Patch values cannot be null; omit unchanged fields")
        return values

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        for prop in schema.get("properties", {}).values():
            choices = prop.get("anyOf", [])
            non_null = [choice for choice in choices if choice.get("type") != "null"]
            if len(non_null) == 1 and len(non_null) != len(choices):
                prop.pop("anyOf")
                prop.update(non_null[0])
            if prop.get("default", False) is None:
                prop.pop("default")
        return schema


class Parameters(StrictModel):
    x: float = Field(500, ge=-1000, le=2000)
    y: float = Field(350, ge=-700, le=1400)
    radius: float = Field(190, ge=80, le=400)
    elongation: float = Field(1, ge=0.4, le=2.5)
    rotation: float = Field(0, ge=-360, le=360)
    lobes: int = Field(3, ge=2, le=9, strict=True)
    warp: float = Field(0.5, ge=0, le=1)
    phase: float = Field(0, ge=0, le=math.tau)


class ParameterPatch(PatchModel):
    x: float | None = Field(None, ge=-1000, le=2000)
    y: float | None = Field(None, ge=-700, le=1400)
    radius: float | None = Field(None, ge=80, le=400)
    elongation: float | None = Field(None, ge=0.4, le=2.5)
    rotation: float | None = Field(None, ge=-360, le=360)
    lobes: int | None = Field(None, ge=2, le=9, strict=True)
    warp: float | None = Field(None, ge=0, le=1)
    phase: float | None = Field(None, ge=0, le=math.tau)


Palette = Literal["ember", "lagoon", "aurora", "mono"]


class Style(StrictModel):
    palette: Palette = "ember"
    opacity: float = Field(1, ge=0.05, le=1)
    visible: bool = True


class StylePatch(PatchModel):
    palette: Palette | None = None
    opacity: float | None = Field(None, ge=0.05, le=1)
    visible: bool | None = None


class View(StrictModel):
    zoom: float = Field(1, ge=0.25, le=4)
    pan_x: float = Field(0, ge=-2000, le=2000)
    pan_y: float = Field(0, ge=-1400, le=1400)
    grid: bool = False
    contours: int = Field(26, ge=8, le=64, strict=True)


class ViewPatch(PatchModel):
    zoom: float | None = Field(None, ge=0.25, le=4)
    pan_x: float | None = Field(None, ge=-2000, le=2000)
    pan_y: float | None = Field(None, ge=-1400, le=1400)
    grid: bool | None = None
    contours: int | None = Field(None, ge=8, le=64, strict=True)


class Animation(StrictModel):
    playing: bool = False
    time: float = Field(0, ge=0, le=3600)
    speed: float = Field(0.65, ge=0.1, le=3)
    motion: float = Field(0.45, ge=0, le=1)


class AnimationPatch(PatchModel):
    playing: bool | None = None
    time: float | None = Field(None, ge=0, le=3600)
    speed: float | None = Field(None, ge=0.1, le=3)
    motion: float | None = Field(None, ge=0, le=1)


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
]
Name = Annotated[str, Field(min_length=1, max_length=80)]


class Pose(StrictModel):
    x: float = Field(ge=-1000, le=2000)
    y: float = Field(ge=-700, le=1400)
    radius: float = Field(ge=80, le=400)
    elongation: float = Field(ge=0.4, le=2.5)
    rotation: float = Field(ge=-360, le=360)
    warp: float = Field(ge=0, le=1)


class Keyframe(StrictModel):
    time: float = Field(ge=0, le=12)
    parameters: Pose
    easing: Literal["linear", "smooth"] = "smooth"


class TrackModel(StrictModel):
    keyframes: list[Keyframe] = Field(default_factory=list, max_length=24)

    @model_validator(mode="after")
    def ordered_keys(self):
        validate_keyframes([key.model_dump() for key in self.keyframes])
        return self


class Island(TrackModel):
    id: Identifier
    name: Name
    type: Literal["island"] = "island"
    parameters: Parameters = Field(default_factory=Parameters)
    style: Style = Field(default_factory=Style)


class Blend(StrictModel):
    id: Identifier
    name: Name = "Island confluence"
    source_a: Identifier
    source_b: Identifier
    operation: Literal["union", "smooth_union"] = "smooth_union"
    amount: float = Field(0.6, ge=0, le=1)
    style: Style = Field(default_factory=lambda: Style(palette="aurora"))


class Recipe(StrictModel):
    schema_version: Literal[4] = 4
    title: Name = "Tidal Atlas"
    objects: list[Island] = Field(max_length=16)
    blends: list[Blend] = Field(default_factory=list, max_length=2)
    layer_order: list[Identifier] = Field(max_length=18)
    view: View = Field(default_factory=View)
    animation: Animation = Field(default_factory=Animation)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        version = schema["properties"]["schema_version"]
        version.pop("const", None)
        version["enum"] = [1, 2, 3, 4]
        schema["required"].remove("layer_order")
        schema["allOf"] = [
            {
                "if": {
                    "properties": {"schema_version": {"const": 4}},
                    "required": ["schema_version"],
                },
                "then": {"required": ["layer_order"]},
            }
        ]
        return schema

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy(cls, values):
        if not isinstance(values, dict):
            return values
        legacy = type(values.get("schema_version")) is int and values[
            "schema_version"
        ] in {1, 2, 3}
        construction = "schema_version" not in values and "layer_order" not in values
        if legacy or construction:
            order = []
            for field in ("objects", "blends"):
                items = values.get(field, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, (Island, Blend)):
                            order.append(item.id)
                        elif isinstance(item, dict) and "id" in item:
                            order.append(item["id"])
            return {**values, "schema_version": 4, "layer_order": order}
        return values

    @model_validator(mode="after")
    def static_references(self):
        islands = {obj.id: obj for obj in self.objects}
        ids = [obj.id for obj in self.objects] + [blend.id for blend in self.blends]
        if len(ids) != len(set(ids)):
            raise ValueError("Island and blend IDs must be globally unique")
        if len(self.layer_order) != len(ids) or set(self.layer_order) != set(ids):
            raise ValueError(
                "Layer order must contain every island and blend ID exactly once"
            )
        for blend in self.blends:
            if blend.source_a == blend.source_b:
                raise ValueError("Choose two distinct source islands")
            for source in (blend.source_a, blend.source_b):
                if source not in islands:
                    raise ValueError(
                        "Blend operands must reference islands; nested blends/cycles are not supported"
                    )
                if islands[source].keyframes:
                    raise ValueError(
                        "Blending supports static islands only; remove their pose tracks or remove the blend first"
                    )
        return self


class Create(TrackModel):
    op: Literal["create_geometry"]
    name: Name = "Untitled island"
    parameters: Parameters = Field(default_factory=Parameters)
    style: Style = Field(default_factory=Style)


class Update(StrictModel):
    op: Literal["update_geometry"]
    id: Identifier
    parameters: ParameterPatch = Field(default_factory=ParameterPatch)
    name: Name | None = None


class Delete(StrictModel):
    op: Literal["delete_geometry"]
    id: Identifier


class SetStyle(StrictModel):
    op: Literal["set_style"]
    id: Identifier
    style: StylePatch


class ReorderLayers(StrictModel):
    op: Literal["reorder_layers"]
    order: list[Identifier] = Field(max_length=18)


class SetView(StrictModel):
    op: Literal["set_view"]
    view: ViewPatch = Field(default_factory=ViewPatch)
    animation: AnimationPatch = Field(default_factory=AnimationPatch)


class Select(StrictModel):
    op: Literal["select"]
    ids: list[Identifier] = Field(max_length=18)


class SetKeyframe(StrictModel):
    op: Literal["set_keyframe"]
    id: Identifier
    keyframe: Keyframe


class DeleteKeyframe(StrictModel):
    op: Literal["delete_keyframe"]
    id: Identifier
    time: float = Field(ge=0, le=12)


class KeyPosition(StrictModel):
    x: float = Field(ge=-1000, le=2000)
    y: float = Field(ge=-700, le=1400)


class TransformLayers(StrictModel):
    op: Literal["transform_layers"]
    ids: list[Identifier] = Field(
        min_length=1, max_length=18, json_schema_extra={"uniqueItems": True}
    )
    dx: float = Field(0, ge=-3000, le=3000)
    dy: float = Field(0, ge=-2100, le=2100)
    scale: float = Field(1, ge=0.1, le=4)
    rotation: float = Field(0, ge=-360, le=360)
    pivot: KeyPosition | None = None

    @model_validator(mode="after")
    def unique_layers(self):
        if len(self.ids) != len(set(self.ids)):
            raise ValueError("Transform IDs must be unique")
        return self


class LayoutIslands(StrictModel):
    op: Literal["layout_islands"]
    ids: list[Identifier] = Field(
        min_length=2, max_length=16, json_schema_extra={"uniqueItems": True}
    )
    mode: Literal["align_x", "align_y", "space_x", "space_y"]
    time: float = Field(0, ge=0, le=12)

    @model_validator(mode="after")
    def valid_selection(self):
        if len(self.ids) != len(set(self.ids)):
            raise ValueError("Layout IDs must be unique")
        if self.mode.startswith("space") and len(self.ids) < 3:
            raise ValueError("Even spacing needs at least three islands")
        return self


class RetimeTarget(StrictModel):
    id: Identifier
    times: list[Annotated[float, Field(ge=0, le=12)]] = Field(
        min_length=1, max_length=24, json_schema_extra={"uniqueItems": True}
    )

    @model_validator(mode="after")
    def unique_times(self):
        if len(self.times) != len(set(self.times)):
            raise ValueError("Source times must be unique")
        return self


class TimingTargets(StrictModel):
    targets: list[RetimeTarget] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def unique_tracks(self):
        ids = [target.id for target in self.targets]
        if len(ids) != len(set(ids)):
            raise ValueError("Target island IDs must be unique")
        return self


class RetimeKeyframes(TimingTargets):
    op: Literal["retime_keyframes"]
    delta: float = Field(ge=-12, le=12)


class ScaleKeyframes(TimingTargets):
    op: Literal["scale_keyframes"]
    anchor: float = Field(ge=0, le=12)
    factor: float = Field(ge=0.1, le=4)


class EditKeyframe(StrictModel):
    op: Literal["edit_keyframe"]
    id: Identifier
    time: float = Field(ge=0, le=12)
    new_time: float | None = Field(None, ge=0, le=12)
    position: KeyPosition | None = None

    @model_validator(mode="after")
    def has_edit(self):
        if self.new_time is None and self.position is None:
            raise ValueError("Supply new_time or a complete x/y position")
        return self


class CreateBlend(StrictModel):
    op: Literal["create_blend"]
    name: Name = "Island confluence"
    source_a: Identifier
    source_b: Identifier
    operation: Literal["union", "smooth_union"] = "smooth_union"
    amount: float = Field(0.6, ge=0, le=1)
    style: Style = Field(default_factory=lambda: Style(palette="aurora"))


class UpdateBlend(PatchModel):
    op: Literal["update_blend"]
    id: Identifier
    name: Name | None = None
    source_a: Identifier | None = None
    source_b: Identifier | None = None
    operation: Literal["union", "smooth_union"] | None = None
    amount: float | None = Field(None, ge=0, le=1)
    style: StylePatch | None = None


class DeleteBlend(StrictModel):
    op: Literal["delete_blend"]
    id: Identifier


Child = Annotated[
    Union[
        Create,
        Update,
        Delete,
        SetStyle,
        ReorderLayers,
        SetView,
        Select,
        TransformLayers,
        LayoutIslands,
        SetKeyframe,
        DeleteKeyframe,
        EditKeyframe,
        RetimeKeyframes,
        ScaleKeyframes,
        CreateBlend,
        UpdateBlend,
        DeleteBlend,
    ],
    Field(discriminator="op"),
]


class Mutation(StrictModel):
    expected_revision: int = Field(ge=0, strict=True)
    request_id: Identifier | None = None


class CreateCommand(Create, Mutation):
    pass


class UpdateCommand(Update, Mutation):
    pass


class DeleteCommand(Delete, Mutation):
    pass


class StyleCommand(SetStyle, Mutation):
    pass


class ReorderLayersCommand(ReorderLayers, Mutation):
    pass


class ViewCommand(SetView, Mutation):
    pass


class SelectCommand(Select, Mutation):
    pass


class TransformLayersCommand(TransformLayers, Mutation):
    pass


class LayoutIslandsCommand(LayoutIslands, Mutation):
    pass


class KeyframeCommand(SetKeyframe, Mutation):
    pass


class DeleteKeyframeCommand(DeleteKeyframe, Mutation):
    pass


class EditKeyframeCommand(EditKeyframe, Mutation):
    pass


class RetimeKeyframesCommand(RetimeKeyframes, Mutation):
    pass


class ScaleKeyframesCommand(ScaleKeyframes, Mutation):
    pass


class CreateBlendCommand(CreateBlend, Mutation):
    pass


class UpdateBlendCommand(UpdateBlend, Mutation):
    pass


class DeleteBlendCommand(DeleteBlend, Mutation):
    pass


class BatchCommand(Mutation):
    op: Literal["batch"]
    label: Name = "Compose artwork"
    commands: list[Child] = Field(min_length=1, max_length=32)


class UndoCommand(Mutation):
    op: Literal["undo"]


class RedoCommand(Mutation):
    op: Literal["redo"]


class LoadCommand(Mutation):
    op: Literal["load_recipe"]
    recipe: Recipe


COMMAND_MODELS = {
    "create_geometry": CreateCommand,
    "update_geometry": UpdateCommand,
    "delete_geometry": DeleteCommand,
    "set_style": StyleCommand,
    "reorder_layers": ReorderLayersCommand,
    "set_view": ViewCommand,
    "select": SelectCommand,
    "transform_layers": TransformLayersCommand,
    "layout_islands": LayoutIslandsCommand,
    "set_keyframe": KeyframeCommand,
    "delete_keyframe": DeleteKeyframeCommand,
    "edit_keyframe": EditKeyframeCommand,
    "retime_keyframes": RetimeKeyframesCommand,
    "scale_keyframes": ScaleKeyframesCommand,
    "create_blend": CreateBlendCommand,
    "update_blend": UpdateBlendCommand,
    "delete_blend": DeleteBlendCommand,
    "batch": BatchCommand,
    "undo": UndoCommand,
    "redo": RedoCommand,
    "load_recipe": LoadCommand,
}
COMMAND = TypeAdapter(
    Annotated[Union[tuple(COMMAND_MODELS.values())], Field(discriminator="op")]
)
DESCRIPTIONS = {
    "create_blend": "Create a non-destructive union/smooth_union of two distinct static island IDs. No tracks or nested operands. Amount 0..1 is dimensionless legacy smooth-min alpha, not a Euclidean distance. Sources stay editable. At most two blends.",
    "update_blend": "Edit a blend's source IDs, operation, amount, name or style. Preserve source objects. Only static island operands; no nested/cyclic references. Requires latest revision.",
    "delete_blend": "Remove only a blend record, restoring its separate source artwork. Does not delete or alter source islands. Undoable; requires latest revision.",
    "get_scene": "Read authoritative artwork, object IDs, current revision, selection and undo history. Read before editing.",
    "get_selection": "Read selected object IDs, complete selected objects, document ID and current revision.",
    "create_geometry": "Create a bounded declarative island field. Positive radii are world units; rotation is degrees. Requires latest revision.",
    "update_geometry": "Modify named parameters of one island, preserving all unspecified parameters. Requires latest revision.",
    "delete_geometry": "Remove one island. Reversible with undo. Requires latest revision.",
    "set_style": "Change one island or blend layer's palette, visibility or opacity (0.05..1). Opacity composites the complete layer once; hiding a blend restores separate source artwork. Source visibility never removes its field from a blend. Requires latest revision.",
    "reorder_layers": "Set back-to-front layer order. Standalone calls require every current island/blend ID exactly once. Batches may order their final remaining layers before deletion; final missing/duplicate/unknown IDs fail atomically. Requires latest revision.",
    "set_view": "Set view and/or art-directed animation parameters. This is not a physical simulation. Requires latest revision.",
    "select": "Set selected island or blend layer IDs, visible in the manual inspector. Requires latest revision.",
    "transform_layers": "Atomically translate, uniformly scale, and rotate explicit island/blend IDs and every authored pose. Expand blends to retained sources, moving shared sources once; dependent blends may also change. Scale then rotate about supplied pivot (default unique base-center mean), then translate. Preserve times/easing, authored degrees, style, selection, order and playback; reject any out-of-bounds base/key pose without clamping. Existing procedural tide remains unchanged. Requires latest revision.",
    "layout_islands": "Atomically align or evenly space 2..16 unique explicit island IDs using authored centers sampled at supplied time 0..12 (default 0; no wall-clock anchor). align_x makes a vertical line at mean x; align_y makes a horizontal line at mean y. space_x/space_y need 3+ islands: sort centers with ASCII ID tie-breaks and keep the outer centers fixed. Translate each complete base/track; preserve shape, timing/easing, style, order, selection and playback. Reject any out-of-bounds pose without partial commits. Blend IDs are unsupported; moving retained sources preserves references and can change dependent blends. Center spacing does not guarantee edge gaps or collision avoidance. Requires latest revision.",
    "set_keyframe": "Insert or replace a complete six-parameter island pose at 0..12 seconds. At most 24 unique sorted keys per island. Left key easing controls interpolation; rotation uses authored degrees. Requires latest revision.",
    "delete_keyframe": "Delete one island pose key at its exact time. Reversible with shared undo. Requires latest revision.",
    "edit_keyframe": "Move an existing key's x/y position and/or retime it within 0..12 seconds. Identify the exact source time. Preserve all other pose values and easing; sort after retiming. Occupied destination times fail without changes. Requires latest revision.",
    "retime_keyframes": "Shift explicit existing keys together by delta seconds across 1..16 unique island tracks. Supply targets [{id,times}] with 1..24 unique exact source times each and finite delta -12..12. Vacate selected times simultaneously, preserve each pose/easing and sort afterward. Crossing unselected keys is allowed when final times are free. Reject the entire edit for missing keys, destinations outside 0..12 or exact occupied/duplicate destinations; never round, clamp or wrap. Preserve base geometry, styles, selection, order and playback. Blend record IDs are unsupported. Requires latest revision; shared undo/redo and atomic batch apply.",
    "scale_keyframes": "Stretch/compress explicit selected key times using anchor + (time-anchor)*factor across 1..16 unique island tracks, with 1..24 exact source times per target. Required anchor is finite 0..12 seconds; required positive factor is 0.1..4 (1 is exact identity). No inferred selection or wall-clock anchor. Preserve anchored times exactly, all poses/easing, base geometry, styles, order, selection and playback. Vacate selected times together, sort afterward and reject all targets for missing keys, exact occupied/duplicate destinations or any result outside 0..12. No rounding, clamping, wrapping, reversal or endpoint auto-match. Shared atomic batch/revision/retry/undo contracts apply.",
    "batch": "Apply up to 32 edits atomically with one undo step. Child schemas and operation preconditions apply; cross-record scene invariants are checked on the final candidate before persistence. Failure leaves artwork/history/revision unchanged. Child commands cannot include revision metadata.",
    "undo": "Undo the last complete transaction, across manual and agent edits. Revision continues increasing.",
    "redo": "Restore the last undone transaction. Revision continues increasing.",
    "load_recipe": "Replace artwork with a validated version-4 recipe; versions 1/2/3 migrate to islands-then-blends back-to-front order and retain existing tracks/styles/dependencies. One undoable transaction. No expressions or executable code.",
}


def tool_definitions() -> list[dict]:
    """Generate the public tool schema from the exact command validators."""
    tools = []
    for name in ("get_scene", "get_selection", *COMMAND_MODELS):
        if name in COMMAND_MODELS:
            schema = COMMAND_MODELS[name].model_json_schema()
            schema["properties"].pop("op")
            schema["required"] = [
                key for key in schema.get("required", []) if key != "op"
            ]
        else:
            schema = {"type": "object", "properties": {}, "additionalProperties": False}
        tools.append(
            {
                "name": name,
                "description": DESCRIPTIONS[name],
                "inputSchema": schema,
                "annotations": {
                    "readOnlyHint": name.startswith("get_"),
                    "destructiveHint": name
                    in {
                        "delete_geometry",
                        "delete_keyframe",
                        "delete_blend",
                        "load_recipe",
                    },
                    "idempotentHint": name.startswith("get_"),
                    "openWorldHint": False,
                },
            }
        )
    return tools


class SceneError(Exception):
    def __init__(self, code: str, message: str, details=None, status: int = 400):
        super().__init__(message)
        self.code, self.message, self.details, self.status = (
            code,
            message,
            details,
            status,
        )

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


def initial_recipe() -> dict:
    return Recipe(
        title="Midnight archipelago",
        objects=[
            Island(
                id="island_ember",
                name="Solstice",
                parameters=Parameters(
                    x=320,
                    y=375,
                    radius=215,
                    elongation=0.95,
                    rotation=-24,
                    lobes=3,
                    warp=0.68,
                    phase=0.4,
                ),
                style=Style(palette="ember"),
            ),
            Island(
                id="island_lagoon",
                name="Undertow",
                parameters=Parameters(
                    x=710,
                    y=305,
                    radius=195,
                    elongation=0.9,
                    rotation=151,
                    lobes=3,
                    warp=0.72,
                    phase=2.2,
                ),
                style=Style(palette="lagoon"),
            ),
            Island(
                id="island_moon",
                name="Drift",
                parameters=Parameters(
                    x=760,
                    y=580,
                    radius=80,
                    elongation=1.1,
                    rotation=15,
                    lobes=4,
                    warp=0.42,
                    phase=4,
                ),
                style=Style(palette="aurora"),
            ),
        ],
    ).model_dump()


def scene_changes(before, after):
    """Summarize committed data differences, never client labels or identity."""
    old = {obj["id"]: obj for obj in [*before["objects"], *before["blends"]]}
    new = {obj["id"]: obj for obj in [*after["objects"], *after["blends"]]}
    changes = {
        "created_ids": [key for key in new if key not in old],
        "removed_ids": [key for key in old if key not in new],
        "updated_ids": [key for key in new if key in old and new[key] != old[key]],
        **{
            f"{key}_changed": before[key] != after[key]
            for key in ("selection", "view", "animation", "layer_order", "title")
        },
    }
    parts = []
    for key, verb in (
        ("created_ids", "Created"),
        ("updated_ids", "Updated"),
        ("removed_ids", "Removed"),
    ):
        if changes[key]:
            count = len(changes[key])
            parts.append(f"{verb} {count} layer" + ("s" if count != 1 else ""))
    for key, label in (
        ("selection", "Selection"),
        ("view", "View"),
        ("animation", "Animation"),
        ("layer_order", "Layer order"),
        ("title", "Title"),
    ):
        if changes[f"{key}_changed"]:
            parts.append(label + " changed")
    return changes, "; ".join(parts) or "No artwork change"


class SceneService:
    """One locked scene, bounded history and durable atomic recipe snapshots.

    This first version is a single-user loopback studio, not a multi-tenant server.
    Undo history and replay keys last for this process; the recipe/revision persist.
    """

    tool_definitions = staticmethod(tool_definitions)

    def __init__(self, storage_path: str | Path | None = None):
        self._lock = threading.RLock()
        self._animation_epoch = time.monotonic()
        self._storage = Path(storage_path) if storage_path else None
        self._scene = {
            **initial_recipe(),
            "document_id": "doc_" + uuid.uuid4().hex[:12],
            "revision": 0,
            "selection": [],
        }
        self._past: list[dict] = []
        self._future: list[dict] = []
        self._events: list[dict] = []
        self._session_commits = 0
        self._session_id = "session_" + uuid.uuid4().hex
        self._requests: OrderedDict = OrderedDict()
        if self._storage and self._storage.exists():
            saved = json.loads(self._storage.read_text())
            recipe = Recipe.model_validate(
                {key: saved[key] for key in Recipe.model_fields if key in saved}
            ).model_dump()
            self._validate_ids(recipe)
            document_id = TypeAdapter(Identifier).validate_python(saved["document_id"])
            revision = saved["revision"]
            if type(revision) is not int or revision < 0:
                raise ValueError("Stored revision is invalid")
            self._scene = {
                **recipe,
                "document_id": document_id,
                "revision": revision,
                "selection": [],
            }

    def _live_scene(self) -> dict:
        scene = copy.deepcopy(self._scene)
        if scene["animation"]["playing"]:
            elapsed = time.monotonic() - self._animation_epoch
            scene["animation"]["time"] = (
                scene["animation"]["time"] + elapsed * scene["animation"]["speed"]
            ) % 12
        return scene

    def snapshot(self) -> dict:
        with self._lock:
            return {
                **self._live_scene(),
                "session_id": self._session_id,
                "history": {
                    "can_undo": bool(self._past),
                    "can_redo": bool(self._future),
                    "entries": copy.deepcopy(self._events[-30:]),
                    "session_commits": self._session_commits,
                    "entry_limit": 30,
                },
            }

    def recipe(self) -> dict:
        with self._lock:
            live = self._live_scene()
            return {key: live[key] for key in Recipe.model_fields}

    @staticmethod
    def _frame_time(scene: dict, time_value: float | None) -> float:
        if time_value is None:
            return scene["animation"]["time"]
        if (
            isinstance(time_value, bool)
            or not isinstance(time_value, (float, int))
            or not math.isfinite(time_value)
            or not 0 <= time_value <= 3600
        ):
            raise SceneError(
                "validation_error",
                "Frame time must be finite and between 0 and 3600 seconds",
            )
        return float(time_value)

    @staticmethod
    def _geometry_scene_from_snapshot(scene: dict, time_value: float):
        # A derived snapshot, never a second editable source of truth. Existing
        # engine consumers receive real ImplicitCurve objects under stable IDs.
        from scene_management.scene_manager import SceneManager

        manager = SceneManager()
        colors = {
            "ember": "#f0a088",
            "lagoon": "#8ed0c6",
            "aurora": "#d7ba75",
            "mono": "#d9dfcf",
        }
        consumed = {
            source
            for b in scene["blends"]
            if b["style"]["visible"]
            for source in (b["source_a"], b["source_b"])
        }
        by_id = {obj["id"]: obj for obj in [*scene["objects"], *scene["blends"]]}
        for layer_id in scene["layer_order"]:
            obj = by_id[layer_id]
            if not obj["style"]["visible"] or obj["id"] in consumed:
                continue
            field = SceneService._field_from_snapshot(scene, obj["id"], time_value)
            manager.add_object(
                obj["id"],
                field.level_set(0),
                {
                    "color": colors[obj["style"]["palette"]],
                    "alpha": obj["style"]["opacity"],
                    "linewidth": 1.0,
                },
            )
        return manager

    def get_geometry(self, object_id: str, time_value: float | None = None):
        """Return a detached existing-BaseField-compatible numeric field."""

        scene = self.snapshot()
        frame_time = self._frame_time(scene, time_value)
        return self._field_from_snapshot(scene, object_id, frame_time)

    @staticmethod
    def _field_from_snapshot(scene, object_id, frame_time):
        from geometry import KineticIslandField
        from geometry.static_blend import StaticBlendField

        by_id = {obj["id"]: obj for obj in scene["objects"]}
        blend = next((b for b in scene["blends"] if b["id"] == object_id), None)
        if blend:
            return StaticBlendField(
                by_id[blend["source_a"]]["parameters"],
                by_id[blend["source_b"]]["parameters"],
                blend["operation"],
                blend["amount"],
            )
        obj = by_id.get(object_id)
        if obj is None:
            raise SceneError(
                "object_not_found", f"Unknown geometry: {object_id}", status=404
            )
        linked = any(
            object_id in {b["source_a"], b["source_b"]} for b in scene["blends"]
        )
        return KineticIslandField(
            sample_parameters(obj["parameters"], obj["keyframes"], frame_time),
            time=0 if linked else frame_time,
            motion=0 if linked else scene["animation"]["motion"],
        )

    def geometry_scene(self, time_value: float | None = None):
        """Adapt one authoritative revision to the existing SceneManager API."""
        scene = self.snapshot()
        return self._geometry_scene_from_snapshot(
            scene, self._frame_time(scene, time_value)
        )

    def geometry_paths(
        self, resolution: int = 180, time_value: float | None = None
    ) -> dict:
        """Extract real engine shoreline paths through GraphicsBackendInterface."""
        from graphics_backend.graphics_interface import GraphicsBackendInterface

        if type(resolution) is not int or not 24 <= resolution <= 720:
            raise SceneError(
                "validation_error", "Resolution must be an integer from 24 through 720"
            )
        scene = self.snapshot()
        frame_time = self._frame_time(scene, time_value)
        manager = self._geometry_scene_from_snapshot(scene, frame_time)
        paths = GraphicsBackendInterface(manager).get_curve_paths(
            bounds=(-1000, 2000, -700, 1400), resolution=resolution
        )
        return {
            "document_id": scene["document_id"],
            "revision": scene["revision"],
            "time": frame_time,
            "paths": paths,
        }

    def invoke(
        self,
        tool: str,
        args: dict,
        actor: str = "mcp",
        *,
        entrypoint: str | None = None,
        caller_hint: str | None = None,
    ) -> dict:
        if not isinstance(args, dict):
            raise SceneError("invalid_arguments", "Tool arguments must be an object")
        if tool in {"get_scene", "get_selection"}:
            if args:
                raise SceneError(
                    "invalid_arguments", "This read tool takes no arguments"
                )
            scene = self.snapshot()
            if tool == "get_scene":
                return {"ok": True, "scene": scene}
            return {
                "ok": True,
                "document_id": scene["document_id"],
                "revision": scene["revision"],
                "selection": scene["selection"],
                "objects": [
                    o
                    for o in [*scene["objects"], *scene["blends"]]
                    if o["id"] in scene["selection"]
                ],
            }
        if tool not in COMMAND_MODELS:
            raise SceneError("unknown_tool", f"Unknown tool: {tool}")
        if "op" in args:
            raise SceneError(
                "invalid_arguments", "Do not supply op inside named tool arguments"
            )
        return self.execute(
            {"op": tool, **args},
            actor=actor,
            entrypoint=entrypoint or "internal",
            caller_hint=caller_hint,
        )

    def execute(
        self,
        command: dict,
        actor: str = "manual",
        *,
        entrypoint: str = "internal",
        caller_hint: str | None = None,
    ) -> dict:
        try:
            parsed = COMMAND.validate_python(command)
        except ValidationError as exc:
            if any(
                error["msg"]
                == "Value error, Island and blend IDs must be globally unique"
                for error in exc.errors()
            ):
                raise SceneError(
                    "duplicate_id", "Island and blend IDs must be globally unique"
                ) from exc
            raise SceneError(
                "validation_error",
                "Command validation failed",
                exc.errors(
                    include_url=False, include_context=False, include_input=False
                ),
            ) from exc
        if actor not in {"manual", "mcp", "webmcp"}:
            raise SceneError("invalid_actor", "Unknown editing source")
        if entrypoint not in {"manual_http", "mcp_protocol", "tool_http", "internal"}:
            raise SceneError("invalid_source", "Unknown server entry point")
        if caller_hint not in {None, "mcp", "webmcp"}:
            raise SceneError("invalid_source", "Unknown caller transport hint")
        source = {
            "entrypoint": entrypoint,
            "identity_verified": False,
            "caller_hint": caller_hint if entrypoint == "tool_http" else None,
        }
        normalized = parsed.model_dump(mode="json")
        fingerprint = hashlib.sha256(
            json.dumps(normalized, sort_keys=True).encode()
        ).hexdigest()
        with self._lock:
            if parsed.request_id and parsed.request_id in self._requests:
                prior_fingerprint, prior_result = self._requests[parsed.request_id]
                if fingerprint != prior_fingerprint:
                    raise SceneError(
                        "request_id_reused",
                        "This request ID was already used for a different command",
                        status=409,
                    )
                return {
                    **copy.deepcopy(prior_result),
                    "scene": self.snapshot(),
                    "replayed": True,
                }
            if parsed.expected_revision != self._scene["revision"]:
                raise SceneError(
                    "revision_conflict",
                    "Artwork changed. Read the current scene and reconsider your edit.",
                    {
                        "expected": parsed.expected_revision,
                        "actual": self._scene["revision"],
                    },
                    409,
                )
            before = self._live_scene()
            candidate = copy.deepcopy(before)
            label = DESCRIPTIONS[parsed.op].split(".")[0]
            affected: list[str] = []
            related = None
            if parsed.op in {"undo", "redo"}:
                stack = self._past if parsed.op == "undo" else self._future
                if not stack:
                    raise SceneError(
                        "nothing_to_" + parsed.op, f"Nothing to {parsed.op}", status=409
                    )
                entry = stack[-1]
                related = {
                    "revision": entry["after"]["revision"],
                    "transaction_id": entry["transaction_id"],
                }
                candidate = copy.deepcopy(
                    entry["before"] if parsed.op == "undo" else entry["after"]
                )
                label = parsed.op.title() + ": " + entry["label"]
                affected = list(candidate["layer_order"])
            elif parsed.op == "load_recipe":
                recipe = parsed.recipe.model_dump()
                self._validate_ids(recipe)
                candidate.update(recipe)
                candidate["selection"] = []
                affected = list(candidate["layer_order"])
                label = "Load " + recipe["title"]
            elif parsed.op == "batch":
                label = parsed.label
                for child in parsed.commands:
                    affected.extend(self._apply(candidate, child))
            else:
                affected.extend(self._apply(candidate, parsed))
                label = {
                    "create_geometry": "Create island",
                    "update_geometry": "Shape island",
                    "set_style": "Change palette / appearance",
                    "set_view": "Adjust view / motion",
                    "select": "Select layer",
                    "transform_layers": "Arrange layers and whole motion paths",
                    "layout_islands": "Align or space island centers and whole paths",
                    "reorder_layers": "Reorder composition layers",
                    "delete_geometry": "Remove island",
                    "set_keyframe": "Capture island pose",
                    "delete_keyframe": "Remove island pose",
                    "edit_keyframe": "Edit island motion key",
                    "retime_keyframes": "Shift selected motion keys",
                    "scale_keyframes": "Scale selected key times around anchor",
                    "create_blend": "Create static confluence",
                    "update_blend": "Shape static confluence",
                    "delete_blend": "Remove confluence, retain sources",
                }[parsed.op]
            try:
                Recipe.model_validate(
                    {key: candidate[key] for key in Recipe.model_fields}
                )
            except ValidationError as exc:
                raise SceneError(
                    "validation_error", exc.errors(include_input=False)[0]["msg"]
                ) from exc
            self._validate_ids(candidate)
            candidate["document_id"] = before["document_id"]
            candidate["revision"] = before["revision"] + 1
            changes, summary = scene_changes(before, candidate)
            if parsed.op in {"undo", "redo"}:
                summary = parsed.op.title() + ": " + summary
            transaction_id = "tx_" + uuid.uuid4().hex[:16]
            # Persistence happens before in-memory commit: IO failure is not success.
            self._persist(candidate)
            self._scene = candidate
            self._animation_epoch = time.monotonic()
            if parsed.op == "undo":
                self._future.append(self._past.pop())
            elif parsed.op == "redo":
                self._past.append(self._future.pop())
            else:
                self._past.append(
                    {
                        "before": before,
                        "after": copy.deepcopy(candidate),
                        "label": label,
                        "transaction_id": transaction_id,
                    }
                )
                self._past = self._past[-100:]
                self._future.clear()
            self._session_commits += 1
            self._events.append(
                {
                    "label": label,
                    "actor": actor,
                    "source": source,
                    "summary": summary,
                    "changes": changes,
                    "operation": parsed.op,
                    "related": related,
                    "committed_at": datetime.now(timezone.utc).isoformat(),
                    "revision": candidate["revision"],
                    "transaction_id": transaction_id,
                }
            )
            self._events = self._events[-100:]
            result = {
                "ok": True,
                "scene": self.snapshot(),
                "transaction_id": transaction_id,
                "affected_ids": list(dict.fromkeys(affected)),
                "replayed": False,
            }
            if parsed.request_id:
                self._requests[parsed.request_id] = (fingerprint, copy.deepcopy(result))
                if len(self._requests) > 256:
                    self._requests.popitem(last=False)
            return result

    @staticmethod
    def _validate_ids(recipe: dict):
        ids = [obj["id"] for obj in recipe["objects"]] + [
            b["id"] for b in recipe.get("blends", [])
        ]
        if len(ids) != len(set(ids)):
            raise SceneError("duplicate_id", "Recipe object IDs must be unique")
        if any(key not in set(ids) for key in recipe.get("selection", [])):
            raise SceneError(
                "validation_error", "Selection must reference existing layers"
            )

    @staticmethod
    def _patch(target: dict, patch: BaseModel):
        # Explicit null is rejected, rather than silently erasing a bounded value.
        values = patch.model_dump(exclude_unset=True)
        if any(value is None for value in values.values()):
            raise SceneError("validation_error", "Patch values cannot be null")
        target.update(values)

    def _apply(self, scene: dict, command: BaseModel) -> list[str]:
        if command.op in {"retime_keyframes", "scale_keyframes"}:
            try:
                targets = [target.model_dump() for target in command.targets]
                changed = (
                    retimed_islands(scene, targets, command.delta)
                    if command.op == "retime_keyframes"
                    else scaled_islands(scene, targets, command.anchor, command.factor)
                )
            except RetimeError as exc:
                raise SceneError(exc.code, str(exc), status=exc.status) from exc
            replacements = {island["id"]: island for island in changed}
            scene["objects"] = [
                replacements.get(island["id"], island) for island in scene["objects"]
            ]
            return list(replacements)
        if command.op == "layout_islands":
            try:
                changed = laid_out_islands(
                    scene, command.ids, command.mode, command.time
                )
            except KeyError as exc:
                raise SceneError(
                    "object_not_found", f"Unknown island: {exc.args[0]}", status=404
                ) from exc
            except ValueError as exc:
                raise SceneError("validation_error", str(exc)) from exc
            replacements = {island["id"]: island for island in changed}
            scene["objects"] = [
                replacements.get(island["id"], island) for island in scene["objects"]
            ]
            return list(replacements)
        if command.op == "transform_layers":
            try:
                targets = resolve_islands(scene, command.ids)
                changed = transformed_islands(
                    targets,
                    **command.model_dump(
                        exclude={"op", "ids", "expected_revision", "request_id"}
                    ),
                )
            except KeyError as exc:
                raise SceneError(
                    "object_not_found", f"Unknown layer: {exc.args[0]}", status=404
                ) from exc
            except ValueError as exc:
                raise SceneError("validation_error", str(exc)) from exc
            replacements = {island["id"]: island for island in changed}
            scene["objects"] = [
                replacements.get(island["id"], island) for island in scene["objects"]
            ]
            return list(replacements)
        if command.op == "reorder_layers":
            scene["layer_order"] = list(command.order)
            return list(command.order)
        if command.op == "set_style":
            layer = next(
                (
                    o
                    for o in [*scene["objects"], *scene["blends"]]
                    if o["id"] == command.id
                ),
                None,
            )
            if layer is None:
                raise SceneError("object_not_found", "Unknown layer", status=404)
            self._patch(layer["style"], command.style)
            return [command.id]
        if command.op == "create_blend":
            if len(scene["blends"]) >= 2:
                raise SceneError("blend_limit", "A scene supports at most two blends")
            blend = Blend(
                id="blend_" + uuid.uuid4().hex[:12],
                **command.model_dump(exclude={"op", "expected_revision", "request_id"}),
            ).model_dump()
            scene["blends"].append(blend)
            scene["layer_order"].append(blend["id"])
            return [blend["id"], blend["source_a"], blend["source_b"]]
        if command.op in {"update_blend", "delete_blend"}:
            blend = next((b for b in scene["blends"] if b["id"] == command.id), None)
            if blend is None:
                raise SceneError("blend_not_found", "Unknown blend", status=404)
            if command.op == "delete_blend":
                scene["blends"].remove(blend)
                scene["layer_order"] = [
                    key for key in scene["layer_order"] if key != blend["id"]
                ]
                scene["selection"] = [i for i in scene["selection"] if i != blend["id"]]
            else:
                values = command.model_dump(
                    exclude_unset=True,
                    exclude={"op", "id", "style", "expected_revision", "request_id"},
                )
                blend.update(values)
                if command.style is not None:
                    self._patch(blend["style"], command.style)
            return [command.id, blend["source_a"], blend["source_b"]]
        if command.op == "create_geometry":
            if len(scene["objects"]) >= 16:
                raise SceneError("object_limit", "A scene supports at most 16 islands")
            obj = Island(
                id="island_" + uuid.uuid4().hex[:12],
                name=command.name,
                parameters=command.parameters,
                style=command.style,
                keyframes=command.keyframes,
            ).model_dump()
            scene["objects"].append(obj)
            scene["layer_order"].append(obj["id"])
            scene["selection"] = [obj["id"]]
            return [obj["id"]]
        if command.op == "set_view":
            self._patch(scene["view"], command.view)
            self._patch(scene["animation"], command.animation)
            return []
        if command.op == "select":
            existing = {obj["id"] for obj in [*scene["objects"], *scene["blends"]]}
            if any(i not in existing for i in command.ids):
                raise SceneError(
                    "object_not_found",
                    "Selection includes an unknown layer",
                    status=404,
                )
            scene["selection"] = list(dict.fromkeys(command.ids))
            return scene["selection"]
        obj = next((o for o in scene["objects"] if o["id"] == command.id), None)
        if obj is None:
            raise SceneError(
                "object_not_found", f"Unknown island: {command.id}", status=404
            )
        if command.op == "update_geometry":
            self._patch(obj["parameters"], command.parameters)
            if command.name is not None:
                obj["name"] = command.name
        elif command.op == "set_style":
            self._patch(obj["style"], command.style)
        elif command.op == "set_keyframe":
            key = command.keyframe.model_dump()
            keys = [k for k in obj["keyframes"] if k["time"] != key["time"]]
            keys.append(key)
            keys.sort(key=lambda k: k["time"])
            if len(keys) > 24:
                raise SceneError(
                    "keyframe_limit", "An island supports at most 24 keyframes"
                )
            obj["keyframes"] = keys
        elif command.op == "edit_keyframe":
            key = next((k for k in obj["keyframes"] if k["time"] == command.time), None)
            if key is None:
                raise SceneError(
                    "keyframe_not_found", "No keyframe at that exact time", status=404
                )
            target_time = command.time if command.new_time is None else command.new_time
            if any(k is not key and k["time"] == target_time for k in obj["keyframes"]):
                raise SceneError(
                    "keyframe_collision",
                    "That time already has a pose. Choose an unoccupied time.",
                )
            key["time"] = target_time
            if command.position is not None:
                key["parameters"].update(command.position.model_dump())
            obj["keyframes"].sort(key=lambda k: k["time"])
        elif command.op == "delete_keyframe":
            keys = [k for k in obj["keyframes"] if k["time"] != command.time]
            if len(keys) == len(obj["keyframes"]):
                raise SceneError(
                    "keyframe_not_found", "No keyframe at that exact time", status=404
                )
            obj["keyframes"] = keys
        elif command.op == "delete_geometry":
            if any(
                command.id in {b["source_a"], b["source_b"]} for b in scene["blends"]
            ):
                raise SceneError(
                    "source_in_use",
                    "Remove the source's blends before deleting this island",
                )
            scene["objects"] = [o for o in scene["objects"] if o["id"] != command.id]
            scene["layer_order"] = [
                key for key in scene["layer_order"] if key != command.id
            ]
            scene["selection"] = [i for i in scene["selection"] if i != command.id]
        return [command.id]

    def _persist(self, scene: dict):
        if not self._storage:
            return
        temp = self._storage.with_suffix(".tmp")
        try:
            self._storage.parent.mkdir(parents=True, exist_ok=True)
            with temp.open("w") as stream:
                json.dump(scene, stream, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            temp.replace(self._storage)
        except OSError as exc:
            raise SceneError(
                "storage_error",
                "Could not save the artwork. No edit was committed.",
                status=503,
            ) from exc
