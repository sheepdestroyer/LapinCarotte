#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

DEPENDABOT_FILE=".github/dependabot.yml"

echo "Configuring Dependabot for MINOR/PATCH updates on pip (default)..."
cat << 'EOF' > $DEPENDABOT_FILE
version: 2
updates:
  # Enable version updates for pip
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    target-branch: "main"
    # By default, only allow patch and minor updates for all pip dependencies.
    # To enable major updates, trigger the toggle workflow with 'major_updates_enabled: true'.
    allowed_updates:
      - match:
          dependency-name: "*" # Apply to all pip dependencies
          update-type: "semver:patch"
      - match:
          dependency-name: "*" # Apply to all pip dependencies
          update-type: "semver:minor"

  # Enable version updates for GitHub Actions
  # By default, this allows all updates for GitHub Actions, including major versions.
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "daily"
    target-branch: "main"
EOF

echo "Successfully wrote restrictive configuration to $DEPENDABOT_FILE"
