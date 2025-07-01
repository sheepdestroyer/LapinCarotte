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

---

### **Phase 3: Testing & Validation**

Testing is not optional. It is a core responsibility to guarantee that changes are correct and do not break existing functionality.

1.  **Write New, Relevant Tests:**
    * For any new feature or bug fix, you **must** write corresponding unit or integration tests.
    * Place new tests in the `tests/` directory, following the naming convention `test_*.py`.
    * Use `tests/test_game_entities_player.py` as a reference for creating tests for game logic.
2.  **Run the Full Test Suite after any change:**
    * Once after each individual step of a task (after any change), and again before finally submitting the tesk result, run the entire test suite locally in verbose mode to ensure that your changes have not introduced any regressions.
    * Install the requirements and Execute the tests in verbose mode using the command: `pip install -r requirements.txt -r requirements_dev.txt && python -m pytest -v`.
    * The Continuous Integration workflow (`run-tests.yml`) will also run these tests, but they must pass locally first.

---

### **Phase 4: Documentation & Housekeeping**

After implementation and testing, the agent must update all relevant documentation.

1.  **Update `TODO.md`:** Modify the `TODO.md` file to reflect the work completed. Update the status of your assigned task (e.g., from `⏳ À faire` to `✅ Terminé`).
2.  **Update `README.md`:** If your changes affect how a user runs the application, builds it, or understands its features, you must update the `README.md` accordingly.
3.  **Update `CI.md`:** This is only required if you have made changes to any of the GitHub Actions workflows in the `.github/workflows/` directory. Your changes must be clearly documented in `CI.md`.

---

### **Phase 5: Final Review & Submission**

Perform a final check to ensure all steps have been completed.

1.  **Review the Checklist:** Go through this document one last time and confirm that every applicable step from Phase 1 to Phase 4 has been successfully executed.
2.  **Submit Your Changes:** Once you have verified compliance with the entire protocol, you may submit your changes.
