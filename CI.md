# Continuous Integration and Automation (CI/CD)

This document outlines the GitHub Actions workflows and related automation configurations used in this repository. Understanding these is crucial for maintaining the project and for any agents tasked with modifying or replicating this setup.

## Table of Contents

1.  [Workflow Overview](#workflow-overview)
2.  [Test Execution Workflow (`run-tests.yml`)](#test-execution-workflow-run-testsyml)
3.  [Build and Release Workflow (`release.yml`)](#build-and-release-workflow-releaseyml)
4.  [Dependabot Configuration (`dependabot.yml`)](#dependabot-configuration-dependabotyml)
5.  [Toggle Dependabot Major Updates Workflow (`toggle_dependabot_major_updates.yml`)](#toggle-dependabot-major-updates-workflow-toggle_dependabot_major_updatesyml)

## 1. Workflow Overview

Our CI/CD setup automates testing, building, releasing, and dependency management using GitHub Actions and Dependabot.

-   **Testing:** Ensures code quality and catches regressions.
-   **Building & Releasing:** Automates the creation of distributable binaries for Windows and Linux and manages GitHub Releases.
-   **Dependency Management:** Keeps dependencies up-to-date via Dependabot, with configurable strategies for updates.

## 2. Test Execution Workflow (`run-tests.yml`)

-   **File:** `.github/workflows/run-tests.yml`
-   **Purpose:** Automatically runs the project's test suite to ensure code changes are valid and do not introduce regressions.
-   **Triggers:**
    -   On `push` to any branch (`**`).
    -   On `pull_request` targeting the `main` branch.
-   **Key Steps & Configuration:**
    1.  **Environment:** Runs on `ubuntu-latest`.
    2.  **Python Setup:** Sets up Python using `actions/setup-python@v5`.
        -   `python-version`: Currently configured for `3.13`.
        -   Caches `pip` dependencies for faster subsequent runs.
    3.  **Dependency Installation:**
        -   Upgrades `pip`.
        -   Installs dependencies from `requirements.txt`.
        -   Conditionally installs dependencies from `requirements_dev.txt` if it exists.
    4.  **Run Tests:** Executes `python -m pytest -v` to run the test suite. This suite includes tests for core game logic, entity behavior, asset management, and command-line interface functionality.

## 3. Build and Release Workflow (`release.yml`)

-   **File:** `.github/workflows/release.yml`
-   **Purpose:** Automates the building of executables for Windows and Linux, and creates/updates GitHub Releases with these assets when a version tag is pushed.
-   **Triggers:**
    -   On `push` of a tag matching the pattern `v*` (e.g., `v1.0`, `v0.2-beta`, `v1.2.3`).
    -   Manual trigger via `workflow_dispatch` (allows specifying a tag name).
-   **Key Jobs & Logic:**
    1.  **`determine_tag` Job:**
        -   Determines the Git tag to be used for the release, whether from a tag push event or manual input.
    2.  **`build-windows` Job:**
        -   Runs on `windows-latest`.
        -   Sets up Python (currently `3.13`).
        -   Installs dependencies from `requirements.txt`.
        -   Runs `python build_exe.py` (which uses PyInstaller) to create `LapinCarotte.exe`.
        -   Uploads the executable as a workflow artifact named `lapin-carotte-windows`.
    3.  **`build-linux` Job:**
        -   Runs on `ubuntu-latest`.
        -   Sets up Python (currently `3.13`).
        -   Installs dependencies from `requirements.txt`.
        -   Runs `python -u build_exe.py` (unbuffered output for PyInstaller).
        -   Includes a subsequent step to list `dist/` contents and PyInstaller build logs for debugging, which runs `if: always()`.
        -   Uploads the executable as a workflow artifact named `lapin-carotte-linux`.
    4.  **`create-release` Job:**
        -   Runs `if: always()` to ensure it executes even if build jobs fail (to create partial or pre-releases).
        -   Requires `contents: write` permission.
        -   **Checkout:** Checks out the repository at the determined tag.
        -   **Prepare Release Body:** Dynamically generates release notes indicating which builds succeeded or failed.
        -   **Get Existing Release Info:** Uses `gh release view <tag>` to check if a release for the tag already exists.
        -   **Create GitHub Release (Conditional):**
            -   If no release exists for the tag (`steps.get_existing_release.outputs.RELEASE_EXISTS == 'false'`), it creates a new GitHub Release using `actions/create-release@v1`.
            -   The release name is `Release <tag_name>`.
            -   The body is the dynamically generated notes from "Prepare Release Body".
            -   It's marked as a `prerelease` if either the Windows or Linux build failed.
        -   **Set Upload URL:** Determines the appropriate `upload_url` (either from an existing release or the newly created one). Fails the job if no URL can be found.
        -   **Download & Upload Assets:**
            -   Conditionally (if their respective builds succeeded) downloads the `lapin-carotte-windows` and `lapin-carotte-linux` artifacts.
            -   Uploads these executables to the determined GitHub Release URL using `actions/upload-release-asset@v1`.

## 4. Dependabot Configuration (`dependabot.yml`)

-   **File:** `.github/dependabot.yml`
-   **Purpose:** Configures Dependabot to automatically create Pull Requests for updating dependencies.
-   **Key Configurations:**
    1.  **`pip` (Python dependencies):**
        -   Checks for updates daily in the root directory (for `requirements.txt`).
        -   Targets the `main` branch.
        -   **Default Update Strategy:** Configured via `allowed_updates` to only allow `semver:patch` and `semver:minor` updates. Major version updates are ignored by default.
        -   To temporarily allow major updates, this file must be manually modified (see `toggle_dependabot_major_updates.yml` workflow).
    2.  **`github-actions` (GitHub Actions used in workflows):**
        -   Checks for updates daily in the root directory (for workflow files).
        -   Targets the `main` branch.
        -   **Default Update Strategy:** Allows all updates, including major versions of actions (no `allowed_updates` or `ignore` rules restricting this).

## 5. Toggle Dependabot Major Updates Workflow (`toggle_dependabot_major_updates.yml`)

-   **File:** `.github/workflows/toggle_dependabot_major_updates.yml`
-   **Purpose:** Provides a manual way to switch the update strategy for `pip` dependencies in `.github/dependabot.yml` between "minor/patch only" and "allow all (including major)".
-   **Trigger:**
    -   Manual trigger via `workflow_dispatch`.
-   **Input:**
    -   `major_updates_enabled` (boolean, default: `false`):
        -   `false`: Configures `dependabot.yml` for minor/patch `pip` updates.
        -   `true`: Configures `dependabot.yml` for all (including major) `pip` updates.
-   **Key Steps & Configuration:**
    1.  **Permissions:** Requires `contents: write` to commit changes to `dependabot.yml`.
    2.  **Checkout:** Checks out the current branch from which the workflow is run.
    3.  **Update Dependabot Configuration File:**
        -   Based on the `major_updates_enabled` input, it executes an external shell script:
            -   `.github/scripts/set_dependabot_restrictive.sh`: Writes `dependabot.yml` with `allowed_updates` for pip restricting to minor/patch.
            -   `.github/scripts/set_dependabot_permissive.sh`: Writes `dependabot.yml` with no `allowed_updates` for pip, allowing all updates.
    4.  **Commit and Push:**
        -   If `.github/dependabot.yml` was changed by the script, it commits the file with a message indicating the new strategy and pushes it to the branch the workflow was run from.
        -   If no changes were made (file already in desired state), no commit/push occurs.
-   **External Scripts:**
    -   `.github/scripts/set_dependabot_restrictive.sh`
    -   `.github/scripts/set_dependabot_permissive.sh`
    -   These scripts contain the `cat << 'EOF' ... EOF` heredoc blocks to generate the respective `dependabot.yml` content. This approach was chosen to avoid YAML parsing issues with complex inline scripts in the main workflow file.
