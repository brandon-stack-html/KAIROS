# init_workspace.ps1
# Initializes the standard SaaS Boilerplate workspace structure.
# Run once after cloning a new project from this boilerplate.
#
# Usage:
#   .\init_workspace.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── 1. Validate required tools ────────────────────────────────────────
Write-Host "Checking required tools..." -ForegroundColor Cyan

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error @"
ERROR: 'uv' is not installed or not in PATH.

Install it with:
  Windows (PowerShell):  irm https://astral.sh/uv/install.ps1 | iex
  Docs:                  https://docs.astral.sh/uv/getting-started/installation/
"@
    exit 1
}

Write-Host "  [OK] uv $(uv --version)" -ForegroundColor Green

# ── 2. Create standard folder structure ───────────────────────────────
Write-Host "`nCreating folder structure..." -ForegroundColor Cyan

$folders = @(
    "src",
    "tests",
    "docs",
    "alembic/versions"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "  Exists:  $folder" -ForegroundColor Gray
    }
}

# ── 3. Generate .env from .env.example ───────────────────────────────
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "`n  Created .env from .env.example — update your secrets!" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n  .env already exists — skipped." -ForegroundColor Gray
}

# ── 4. Install dependencies ───────────────────────────────────────────
Write-Host "`nInstalling dependencies with uv..." -ForegroundColor Cyan
uv sync
Write-Host "  [OK] Dependencies installed." -ForegroundColor Green

# ── 5. Agent initialization examples (commented out) ─────────────────
Write-Host "`nWorkspace ready." -ForegroundColor Green
Write-Host @"

---- Agent Commands Reference -----------------------------------------------

# Codex (code generation — brute force):
  aider --model openrouter/openai/gpt-5-codex ``
        --message "Generate UserRepository following hexagonal architecture" ``
        --no-git --yes --no-pretty

# Gemini (context audit across modules):
  gemini --prompt "Review DDD consistency in src/domain/ and report errors"

# Dev server:
  uv run uvicorn src.infrastructure.api.main:app --reload

# Alembic (first migration):
  uv run alembic revision --autogenerate -m "initial"
  uv run alembic upgrade head

-----------------------------------------------------------------------------
"@
