"""Vercel entrypoint for the FastAPI application."""

import sys
from pathlib import Path

# Make the website directory importable when Vercel executes this function.
website_dir = Path(__file__).resolve().parents[1]
if str(website_dir) not in sys.path:
    sys.path.insert(0, str(website_dir))

from app import app  # noqa: E402

