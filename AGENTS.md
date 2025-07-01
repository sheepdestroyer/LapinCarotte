An Agent must always start by reading all files from the repository in order to have a global understanding of the application.
After implementing a Task, the agent always update TODO.md and README.md accordingly.

## Understanding and Managing CI/CD Workflows

This repository utilizes GitHub Actions for various automation tasks, including testing, building, and release management, as well as Dependabot for dependency updates.

-   **Detailed Workflow Documentation:** A comprehensive description of all workflows, their triggers, purposes, and configurations can be found in [CI.md](CI.md).
-   **Agent Responsibility:** If you are tasked with modifying existing workflows, implementing new ones, or replicating parts of this CI/CD setup, you **must first consult `CI.md`** to understand the current automation landscape.
-   **Consistency:** When making changes or additions, strive to maintain consistency with the patterns and practices documented in `CI.md` unless explicitly instructed otherwise for a specific task.
-   **Replication:** If asked to replicate these workflows in another project, use `CI.md` as your primary reference for their intended functionality and setup.
