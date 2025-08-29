#!/usr/bin/env bash
set -euo pipefail

# Default to .env in project root unless overridden
ENV_FILE="${ENV_FILE:-.env}"

# Run your app
# uv run --env-file "$ENV_FILE" -m src.scraper_test "$@"
uv run --env-file "$ENV_FILE" -m src.scraper.apis.eaglewood "$@"