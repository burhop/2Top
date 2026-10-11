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


class Recipe(StrictModel):
    schema_version: Literal[2] = 2
    title: Name = "Tidal Atlas"
    objects: list[Island] = Field(max_length=16)
    view: View = Field(default_factory=View)
    animation: Animation = Field(default_factory=Animation)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy(cls, values):
        if (
            isinstance(values, dict)
            and type(values.get("schema_version")) is int
            and values["schema_version"] == 1
        ):
            return {**values, "schema_version": 2}
        return values


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


class SetView(StrictModel):
    op: Literal["set_view"]
    view: ViewPatch = Field(default_factory=ViewPatch)
    animation: AnimationPatch = Field(default_factory=AnimationPatch)


class Select(StrictModel):
    op: Literal["select"]
    ids: list[Identifier] = Field(max_length=16)


class SetKeyframe(StrictModel):
    op: Literal["set_keyframe"]
    id: Identifier
    keyframe: Keyframe


class DeleteKeyframe(StrictModel):
    op: Literal["delete_keyframe"]
    id: Identifier
    time: float = Field(ge=0, le=12)


Child = Annotated[
    Union[
        Create, Update, Delete, SetStyle, SetView, Select, SetKeyframe, DeleteKeyframe
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


class ViewCommand(SetView, Mutation):
    pass


class SelectCommand(Select, Mutation):
    pass


class KeyframeCommand(SetKeyframe, Mutation):
    pass


class DeleteKeyframeCommand(DeleteKeyframe, Mutation):
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
    "set_view": ViewCommand,
    "select": SelectCommand,
    "set_keyframe": KeyframeCommand,
    "delete_keyframe": DeleteKeyframeCommand,
    "batch": BatchCommand,
    "undo": UndoCommand,
    "redo": RedoCommand,
    "load_recipe": LoadCommand,
}
COMMAND = TypeAdapter(
    Annotated[Union[tuple(COMMAND_MODELS.values())], Field(discriminator="op")]
)
DESCRIPTIONS = {
    "get_scene": "Read authoritative artwork, object IDs, current revision, selection and undo history. Read before editing.",
    "get_selection": "Read selected object IDs, complete selected objects, document ID and current revision.",
    "create_geometry": "Create a bounded declarative island field. Positive radii are world units; rotation is degrees. Requires latest revision.",
    "update_geometry": "Modify named parameters of one island, preserving all unspecified parameters. Requires latest revision.",
    "delete_geometry": "Remove one island. Reversible with undo. Requires latest revision.",
    "set_style": "Change one island's palette, visibility or opacity. Requires latest revision.",
    "set_view": "Set view and/or art-directed animation parameters. This is not a physical simulation. Requires latest revision.",
    "select": "Set selected island IDs, visible in the manual inspector. Requires latest revision.",
    "set_keyframe": "Insert or replace a complete six-parameter island pose at 0..12 seconds. At most 24 unique sorted keys per island. Left key easing controls interpolation; rotation uses authored degrees. Requires latest revision.",
    "delete_keyframe": "Delete one island pose key at its exact time. Reversible with shared undo. Requires latest revision.",
    "batch": "Apply up to 32 enumerated edits atomically with one undo step. Failure leaves the artwork unchanged. Child commands cannot include revision metadata.",
    "undo": "Undo the last complete transaction, across manual and agent edits. Revision continues increasing.",
    "redo": "Restore the last undone transaction. Revision continues increasing.",
    "load_recipe": "Replace artwork with a validated version-2 choreography recipe; version-1 recipes migrate with empty tracks. One undoable transaction. No expressions or executable code.",
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
                    in {"delete_geometry", "delete_keyframe", "load_recipe"},
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
        self._requests: OrderedDict = OrderedDict()
        if self._storage and self._storage.exists():
            saved = json.loads(self._storage.read_text())
            recipe = Recipe.model_validate(
                {key: saved[key] for key in Recipe.model_fields}
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
                "history": {
                    "can_undo": bool(self._past),
                    "can_redo": bool(self._future),
                    "entries": copy.deepcopy(self._events[-30:]),
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
        from geometry import KineticIslandField
        from scene_management.scene_manager import SceneManager

        manager = SceneManager()
        colors = {
            "ember": "#f0a088",
            "lagoon": "#8ed0c6",
            "aurora": "#d7ba75",
            "mono": "#d9dfcf",
        }
        for obj in scene["objects"]:
            if not obj["style"]["visible"]:
                continue
            field = KineticIslandField(
                sample_parameters(obj["parameters"], obj["keyframes"], time_value),
                time=time_value,
                motion=scene["animation"]["motion"],
            )
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
        from geometry import KineticIslandField

        scene = self.snapshot()
        frame_time = self._frame_time(scene, time_value)
        obj = next((obj for obj in scene["objects"] if obj["id"] == object_id), None)
        if obj is None:
            raise SceneError(
                "object_not_found", f"Unknown island: {object_id}", status=404
            )
        return KineticIslandField(
            sample_parameters(obj["parameters"], obj["keyframes"], frame_time),
            time=frame_time,
            motion=scene["animation"]["motion"],
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

    def invoke(self, tool: str, args: dict, actor: str = "mcp") -> dict:
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
                    o for o in scene["objects"] if o["id"] in scene["selection"]
                ],
            }
        if tool not in COMMAND_MODELS:
            raise SceneError("unknown_tool", f"Unknown tool: {tool}")
        if "op" in args:
            raise SceneError(
                "invalid_arguments", "Do not supply op inside named tool arguments"
            )
        return self.execute({"op": tool, **args}, actor=actor)

    def execute(self, command: dict, actor: str = "manual") -> dict:
        try:
            parsed = COMMAND.validate_python(command)
        except ValidationError as exc:
            raise SceneError(
                "validation_error",
                "Command validation failed",
                exc.errors(
                    include_url=False, include_context=False, include_input=False
                ),
            ) from exc
        if actor not in {"manual", "mcp", "webmcp"}:
            raise SceneError("invalid_actor", "Unknown editing source")
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
            if parsed.op in {"undo", "redo"}:
                stack = self._past if parsed.op == "undo" else self._future
                if not stack:
                    raise SceneError(
                        "nothing_to_" + parsed.op, f"Nothing to {parsed.op}", status=409
                    )
                entry = stack[-1]
                candidate = copy.deepcopy(
                    entry["before"] if parsed.op == "undo" else entry["after"]
                )
                label = parsed.op.title() + ": " + entry["label"]
                affected = [obj["id"] for obj in candidate["objects"]]
            elif parsed.op == "load_recipe":
                recipe = parsed.recipe.model_dump()
                self._validate_ids(recipe)
                candidate.update(recipe)
                candidate["selection"] = []
                affected = [obj["id"] for obj in candidate["objects"]]
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
                    "select": "Select island",
                    "delete_geometry": "Remove island",
                    "set_keyframe": "Capture island pose",
                    "delete_keyframe": "Remove island pose",
                }[parsed.op]
            candidate["document_id"] = before["document_id"]
            candidate["revision"] = before["revision"] + 1
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
                    }
                )
                self._past = self._past[-100:]
                self._future.clear()
            transaction_id = "tx_" + uuid.uuid4().hex[:16]
            self._events.append(
                {
                    "label": label,
                    "actor": actor,
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
        ids = [obj["id"] for obj in recipe["objects"]]
        if len(ids) != len(set(ids)):
            raise SceneError("duplicate_id", "Recipe object IDs must be unique")

    @staticmethod
    def _patch(target: dict, patch: BaseModel):
        # Explicit null is rejected, rather than silently erasing a bounded value.
        values = patch.model_dump(exclude_unset=True)
        if any(value is None for value in values.values()):
            raise SceneError("validation_error", "Patch values cannot be null")
        target.update(values)

    def _apply(self, scene: dict, command: BaseModel) -> list[str]:
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
            scene["selection"] = [obj["id"]]
            return [obj["id"]]
        if command.op == "set_view":
            self._patch(scene["view"], command.view)
            self._patch(scene["animation"], command.animation)
            return []
        if command.op == "select":
            existing = {o["id"] for o in scene["objects"]}
            if any(i not in existing for i in command.ids):
                raise SceneError(
                    "object_not_found",
                    "Selection includes an unknown island",
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
        elif command.op == "delete_keyframe":
            keys = [k for k in obj["keyframes"] if k["time"] != command.time]
            if len(keys) == len(obj["keyframes"]):
                raise SceneError(
                    "keyframe_not_found", "No keyframe at that exact time", status=404
                )
            obj["keyframes"] = keys
        elif command.op == "delete_geometry":
            scene["objects"] = [o for o in scene["objects"] if o["id"] != command.id]
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
