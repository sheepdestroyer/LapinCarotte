#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

DEPENDABOT_FILE=".github/dependabot.yml"

echo "Configuring Dependabot to ALLOW MAJOR updates for pip..."
cat << 'EOF' > $DEPENDABOT_FILE
version: 2
updates:
  # Enable version updates for pip
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    target-branch: "main"
    # Allowing all updates, including major, for pip dependencies.
    # To restrict to minor/patch, trigger the toggle workflow with 'major_updates_enabled: false'.

  # Enable version updates for GitHub Actions
  # By default, this allows all updates for GitHub Actions, including major versions.
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "daily"
    target-branch: "main"
EOF

echo "Successfully wrote permissive configuration to $DEPENDABOT_FILE"
