# AI Project Rules: Modular Smart Surveillance

These rules govern the development of the modular AI surveillance project. They are designed to enforce strict separation of concerns, scalability, and integration safety.

## 📁 Modular Architecture
- **Isolation**: Enforce strict folder isolation: `/detection`, `/face_recognition`, `/behavior`, `/dashboard`.
- **No Cross-Imports**: Do not create cross-module imports (e.g., `detection` should not import from `behavior`).
- **No Shared Logic**: Do not share internal logic between modules to avoid tight coupling.
- **Independence**: Each module must be independently executable via its own `main.py`.
- **Interfaces**: Only expose functionality via defined interfaces (e.g., functions returning `dict` or `JSON`).

## 🤝 Collaboration & Development Safety
- **Module Scoping**: Do not modify files outside the target module folder during a task.
- **No Shared Utilities**: Never generate shared utility files (like a global `utils.py`) across modules. Every module must provide its own utilities.
- **Structured Communication**: All module communication must use structured outputs (dictionaries/JSON).
- **Contracts**: Define clear input/output contracts (API documentation) before generating logic.
- **Mocks**: Use dummy/mock data for all standalone development to remain independent of other modules.
- **Global Variables**: Avoid using global variables that are intended to be shared across multiple modules.

## 🔗 Integration Rules
- **Centralized Integration**: Only the root `main.py` is allowed to handle module integration.
- **No Direct Calls**: No module is allowed to call another module directly.
- **Plug-and-Play**: All modules must be designed as plug-and-play components.
- **Standardized Outputs**: Integration must use function calls with standardized outputs.
- **Separation**: Do not embed integration logic (like dashboard updates) inside the core model/detection code.

## ✍️ Code Generation Rules
- **Folder Placement**: Always place generated code in the correct module folder.
- **Preservation**: Never overwrite or regenerate existing module files unless explicitly asked.
- **Micro-functions**: Keep functions small, single-purpose, and testable.
- **Consistency**: Use consistent naming conventions (lower_case for Python files, CamelCase for classes) across all modules.
- **Abstraction**: Do not hardcode file paths or system-specific values; use configuration or relative paths.
- **Documentation**: Include minimal but clear inline documentation (docstrings).

## 🧪 Testing Rules
- **Standalone Execution**: Each module must run independently via its own `main.py`.
- **Sample Data**: Use sample images/videos for testing (local mock data).
- **Simulations**: Simulate inputs where real-time hardware data is unavailable.
- **Zero-Dependency Tests**: Do not depend on the specific state of other modules for testing.
- **Deterministic**: Ensure deterministic outputs for test scenarios.

## 🏗️ Scalability and Clean Design
- **Structured APIs**: Use function-based APIs for all module outputs.
- **JSON/Dict Results**: Return structured data (dict/JSON), not raw console prints.
- **Organized Structure**: Maintain a readable and organized folder structure.
- **Decoupling**: Proactively avoid tight coupling and hidden dependencies.
- **Future-Proofing**: Design for future extension (e.g., adding new models, RTSP inputs, or UI updates).
- **Production Quality**: Keep code clean, minimal, and prioritized for production performance.
