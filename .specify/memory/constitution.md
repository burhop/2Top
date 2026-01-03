<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Added sections: Additional Constraints, Development Workflow
- Templates requiring updates:
  - ✅ plan-template.md (updated to align with new principles in "Constitution Check" section)
  - ✅ spec-template.md (no direct changes needed, but will be used to create specifications that follow the new principles)
  - ✅ tasks-template.md (no direct changes needed, but will be used to create task lists that follow the new principles)
- Follow-up TODOs: None
-->
# 2Top Constitution
<!-- 2D Implicit Geometry Library Constitution -->

## Core Principles

### I. Test-First (NON-NEGOTIABLE)
All code must be developed with a test-first approach. Unit tests are required for all new functionality, and they must be written before implementation. This includes edge case testing. Every function and class must be covered by tests. The red-green-refactor cycle is mandatory. Tests must be clear, maintainable, and cover all possible failure conditions and edge cases.
<!-- TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### II. Mathematics Correctness
Mathematical accuracy is paramount. All mathematical operations and algorithms must be mathematically sound. Functions that perform geometric calculations or evaluate implicit functions must be verified for correctness. All floating-point operations must be carefully considered for precision and stability. Mathematical properties of the underlying geometry must be preserved in all operations.
<!-- Every mathematical function must be rigorously tested and verified for correctness -->

### III. Error Handling and Explanations
All errors must be well-handled with clear, informative error messages. When mathematical or computational errors occur, the system should provide specific, actionable information to help users understand and resolve the issue. Exception messages should be descriptive and help with debugging.
<!-- Clear, informative error messages and proper exception handling for all edge cases -->

### IV. Clean Module Interfaces
Each module must have a well-defined, clean interface. Public APIs should be consistent, well-documented, and easy to use. Private functions and internal details should be hidden. Module boundaries should be well-defined, and modules should be loosely coupled.
<!-- Well-defined, clean interfaces between different modules with clear public APIs -->

### V. React UI with Reusable Components
For all user interfaces, we will use React with a strong focus on reusable and extendable components. This includes many similar forms for creating and managing objects. UI components should be stateless when possible, and should be built to be composable.
<!-- React-based UI with reusable, extendable components and many similar forms for object management -->

## Additional Constraints

### Technology Stack
- No new dependencies should be added to the existing project
- The project will use Python 3.11+ for core implementation
- For UI, we will use React with TypeScript
- All code must be compatible with the existing library ecosystem

### Development Practices
- All code must be fully tested with comprehensive test coverage, including edge cases
- All mathematical functions must be verified for correctness
- All error conditions must be properly handled with clear messages
- All components must be well-encapsulated and have clear interfaces
- All code must be maintained in a way that supports the long-term goals of the 2Top project

## Development Workflow

### Code Review Process
- All code changes must be reviewed by at least one other team member
- All new code must have test coverage
- All mathematical functions must be reviewed for correctness
- All error handling must be reviewed for completeness
- All UI components must be reviewed for reusability and extensibility

### Release Process
- All releases must be tested and verified
- All mathematical properties must be maintained
- All error handling must be verified
- All UI components must be tested for proper behavior
- All changes must be documented

## Governance
<!-- Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

All PRs/reviews must verify compliance with the core principles. All new code must be fully tested, with a strong focus on edge cases. All mathematical functions must be correct. All error handling must be clear and informative. All UI components must be reusable and extendable. The project will not add new dependencies to the existing codebase.

**Version**: 1.0.0 | **Ratified**: 2026-01-03 | **Last Amended**: 2026-01-03
<!-- Version: 1.0.0 | Ratified: 2026-01-03 | Last Amended: 2026-01-03 -->