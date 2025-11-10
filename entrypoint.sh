#!/bin/bash

set -eu

/action/create_issue_user_story.py \
  --github-api-url "$GITHUB_API_URL" \
  --github-repository "$GITHUB_REPOSITORY" \
  --github-token "$INPUT_GITHUB_TOKEN" \
  --openai-api-key "$INPUT_OPENAI_API_KEY" \
  --azure-openai-api-key "$INPUT_AZURE_OPENAI_API_KEY" \
  --azure-openai-endpoint "$INPUT_AZURE_OPENAI_ENDPOINT" \
  --azure-openai-version "$INPUT_AZURE_OPENAI_VERSION" \
  --issue-title "$INPUT_ISSUE_TITLE" \
  --issue-description "$INPUT_ISSUE_DESCRIPTION" \
  --complexity "$INPUT_COMPLEXITY" \
  --duration "$INPUT_DURATION" \
  --labels "$INPUT_LABELS" \
  --assignees "$INPUT_ASSIGNEES"
