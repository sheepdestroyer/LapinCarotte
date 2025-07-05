This `AGENTS.md` file outlines a comprehensive protocol for any agent making changes.
An agent must follow these steps methodically before submitting any change to ensure code quality, consistency, and maintainability.

### Understanding and Managing CI/CD Workflows

This repository utilizes GitHub Actions for various automation tasks, including testing, building, and release management, as well as Dependabot for dependency updates.

-   **Detailed Workflow Documentation:** A comprehensive description of all workflows, their triggers, purposes, and configurations can be found in [CI.md](CI.md).
-   **Agent Responsibility:** If you are tasked with modifying existing workflows, implementing new ones, or replicating parts of this CI/CD setup, you **must first consult `CI.md`** to understand the current automation landscape.
-   **Consistency:** When making changes or additions, strive to maintain consistency with the patterns and practices documented in `CI.md` unless explicitly instructed otherwise for a specific task.
-   **Replication:** If asked to replicate these workflows in another project, use `CI.md` as your primary reference for their intended functionality and setup.



## **Agent Protocol: Pre-Submission Checklist**

This document outlines the essential, non-negotiable steps an agent must follow before submitting changes to this repository. Adherence to this protocol is critical for maintaining project integrity.

---

### **Phase 1: Task Comprehension & Analysis**

Before writing any code, the agent must have a complete understanding of the repository and the assigned task.

1.  **Full Repository Review:** Start by reading all files in the repository. This provides a global understanding of the architecture, from the main application loop (`main.py`) to state management (`game_state.py`), entities (`game_entities.py`), configuration (`config.py`), and CI/CD automation (`.github/workflows/`, `CI.md`).
2.  **Consult Task & Project Documentation:**
    * Thoroughly review the task description in `TODO.md` to understand the specific requirements.
    * Read the `README.md` for a high-level project overview.
    * Read `CI.md` to understand the continuous integration, build, and release processes. This is mandatory if your task involves changing workflows.

---

### **Phase 2: Implementation & Development**

All code must be written in a consistent and maintainable manner.

1.  **Adhere to Existing Patterns:** Write code that matches the style and architectural patterns already present in the project. For example, entity logic belongs in `game_entities.py`, state management changes go into `game_state.py`, and the main loop in `main.py` should remain clean.
2.  **Use Centralized Configuration:** Do not use hard-coded "magic numbers." All constants (e.g., speeds, sizes, colors, timings) must be defined in and imported from `config.py`.
3.  **Manage Assets Correctly:** All images and sounds must be loaded through the `AssetManager` class to ensure they are correctly located and packaged in the final executable.
4.  **Utilize the Logging System:**
    *   The game uses Python's `logging` module. Informational messages suitable for general console output (like CLI menus or major game state changes) should use `logging.info()`.
    *   For detailed diagnostic information useful during development and debugging, use `logging.debug()`. These messages will only be visible when the `--debug` flag is used.
    *   Warnings about potential issues that don't stop execution should use `logging.warning()`.
    *   Errors that are caught but represent a problem should use `logging.error()` or `logging.exception()` (if within an `except` block to include traceback).
    *   When adding new features or complex logic, include relevant `logging.debug()` statements to trace execution flow and variable states. This aids in future troubleshooting. Avoid using `print()` for debugging; use the logging framework.
5.  **Bilingual Documentation (EN/FR):**
    *   All code comments and logging messages must be bilingual: English first, then French.
    *   *Tous les commentaires de code et messages de log doivent être bilingues : anglais d'abord, puis français.*
    *   Keep comments and logs concise and clear in both languages.
    *   *Gardez les commentaires et les logs concis et clairs dans les deux langues.*
    *   Brief introductory paragraphs (docstrings or comments) should be added to important files and major functions/classes, also in bilingual format (EN then FR).
    *   *De brefs paragraphes d'introduction (docstrings ou commentaires) doivent être ajoutés aux fichiers importants et aux fonctions/classes majeures, également en format bilingue (EN puis FR).*

---

### **Phase 3: Testing & Validation**

Testing is not optional. It is a core responsibility to guarantee that changes are correct and do not break existing functionality.

1.  **Write New, Relevant Tests:**
    * For any new feature or bug fix, you **must** write corresponding unit or integration tests. This includes testing different game states, CLI interactions (if applicable to the feature), and any new modules like asset handlers.
    * Place new tests in the `tests/` directory, following the naming convention `test_*.py`.
    * Use `tests/test_game_entities_player.py` as a reference for creating tests for game logic.
2.  **Run the Full Test Suite after any change:**
    * Once after each individual step of a task (after any change), and again before finally submitting the tesk result, run the entire test suite locally in verbose mode to ensure that your changes have not introduced any regressions. The suite covers various aspects including core game logic, entity behavior, asset management, and CLI functionality.
    * Install the requirements and Execute the tests in verbose mode using the command: `pip install -r requirements.txt -r requirements_dev.txt && python -m pytest -v`.
    * The Continuous Integration workflow (`run-tests.yml`) will also run these tests, but they must pass locally first.
3.  **Maintain Test Scenario Coverage (`full_adventure_game_test.yml`):**
    * Any addition or significant modification to automated tests (in the `tests/` directory) **must** be reflected in `full_adventure_game_test.yml`.
    * This includes adding new narrative steps if new broad functionality is tested, updating existing steps to reference new/modified test functions, or adjusting `coverage_status`.
    * The `full_adventure_game_test.yml` file, located in the repository root, serves as a high-level map of test coverage against a narrative game scenario and must be kept synchronized with the actual test suite. Its purpose is to provide a human-readable overview of what aspects of the game are tested and by which specific test cases.

---

### **Phase 4: Documentation & Housekeeping**

After implementation and testing, the agent must update all relevant documentation.

1.  **Update `TODO.md`:** Modify the `TODO.md` file to reflect the work completed. Update the status of your assigned task (e.g., from `⏳ À faire` to `✅ Terminé`).
2.  **Update `README.md`:** If your changes affect how a user runs the application, builds it, or understands its features, you must update the `README.md` accordingly. For instance, adding a new command-line argument, a significant feature like asset fallbacks, or changes to game controls should be documented.
3.  **Update `CI.md`:** This is only required if you have made changes to any of the GitHub Actions workflows in the `.github/workflows/` directory. Your changes must be clearly documented in `CI.md`.

---

### **Phase 5: Final Review & Submission**

Perform a final check to ensure all steps have been completed.

1.  **Review the Checklist:** Go through this document one last time and confirm that every applicable step from Phase 1 to Phase 4 has been successfully executed.
2.  **Submit Your Changes:** Once you have verified compliance with the entire protocol, you may submit your changes.
