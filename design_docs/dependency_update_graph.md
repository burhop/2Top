# dependency_update_graph.md

# Dependency and Update Graph Design Document

## Purpose

This module defines a **dependency-aware graph system** for tracking and managing relationships between scene objects in a 2D implicit sketching system. It ensures that when a scene object (e.g. an implicit curve) is modified, all downstream objects that depend on it (e.g. fields, regions, composites, or other curves) are either updated or marked as broken. The system enables dynamic subtree editing, repair workflows, and prevents cyclic dependencies.

## Core Concepts

### Node
Each node in the dependency graph corresponds to a **scene object ID** managed by the `SceneManager`.

### Edge
A directed edge from node A to B means: **B depends on A**. If A is modified, B may need to be recomputed or marked invalid.

### Valid / Broken State
Each object in the graph has a state:
- `VALID`: All dependencies are satisfied.
- `BROKEN`: One or more parent dependencies are missing, invalid, or no longer compatible.

## Interface: `DependencyGraph`

```python
class DependencyGraph:
    def __init__(self): ...

    def add_object(self, obj_id: str) -> None: ...
    def remove_object(self, obj_id: str) -> None: ...

    def add_dependency(self, child_id: str, parent_id: str) -> None: ...
    def remove_dependency(self, child_id: str, parent_id: str) -> None: ...
    def replace_dependency(self, child_id: str, old_parent_id: str, new_parent_id: str) -> None: ...

    def get_parents(self, obj_id: str) -> List[str]: ...
    def get_children(self, obj_id: str) -> List[str]: ...
    def get_subtree(self, root_id: str) -> Set[str]: ...

    def has_cycle(self, candidate_parent: str, candidate_child: str) -> bool: ...

    def mark_as_broken(self, obj_id: str, reason: str) -> None: ...
    def clear_broken(self, obj_id: str) -> None: ...
    def is_broken(self, obj_id: str) -> bool: ...
    def get_broken_objects(self) -> List[str]: ...

    def notify_change(self, obj_id: str) -> None: ...
    def simulate_update(self, root_id: str, temp_params: Dict[str, Any]) -> Dict[str, Any]: ...
```

## Integration Points

### With SceneManager
- `SceneManager.add_object()` must also call `DependencyGraph.add_object()`.
- MCP `create_object`, `offset_object`, `blend_objects`, etc., should register dependencies when objects are derived.
- `SceneManager.remove_object()` must call `DependencyGraph.remove_object()` and mark children as broken.
- When a command like `update_parameters` is received, `DependencyGraph.notify_change(obj_id)` should be invoked.

### With Geometry Objects
- Geometry objects may expose an optional `recompute(**kwargs)` interface so that the graph can trigger recomputations downstream.
- Alternatively, SceneManager provides the recompute logic and uses metadata from the graph to know what inputs are needed.

### With Graphics Interface
- Broken objects may be styled differently (e.g., red dashed lines). Use `get_broken_objects()` to determine which objects to render as invalid.

### With UI
- Show broken objects with tooltip reason (`mark_as_broken(reason)` supports this).
- During live dragging, the UI may call `simulate_update()` to preview changes across the subtree.
- Prompt user with fix suggestions if objects become broken (e.g., "Adjust intersection tolerance?").

## Failure and Recovery Semantics

- If any parent of an object is missing or broken, the child is considered `BROKEN`.
- On upstream repair (e.g., a curve is moved back into an intersecting position), the child may become valid again.
- Invalid operations are prevented (e.g., replacing a dependency that would introduce a cycle).

## Advanced Features (Planned)

- `Undo/Redo` support that includes dependency graphs
- Persistent dependency serialization (e.g., saved in `.scene.py` or `.json`)
- Change notification hooks (`on_change(obj_id)`) for observers
- Partial recompute on animation frames

## Example Scenario

1. User creates curve `c1`.
2. User creates offset field `f1` from `c1` → `add_dependency("f1", "c1")`.
3. User creates area region `a1` from `f1` → `add_dependency("a1", "f1")`.
4. User changes parameter of `c1` → triggers `notify_change("c1")`
   - All descendants (`f1`, `a1`) are recomputed if possible.
5. If new `c1` causes `f1`’s field to fail (e.g., due to self-intersection), `f1` and `a1` are marked broken.
6. UI displays broken state. User drags `c1` back → dependency auto-recovers and `clear_broken("f1")` is called.

---

This module provides the scaffolding for real-time procedural modeling, robust error tracking, and dynamic interaction with AI and UI-driven workflows. It ensures a coherent and traceable dataflow in the implicit modeling system.
