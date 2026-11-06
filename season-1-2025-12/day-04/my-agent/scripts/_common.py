"""Shared helpers: find the deployed agent and build a Vertex AI client."""

import json
import os
from pathlib import Path

import vertexai
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "app" / ".env")

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.getenv("AGENT_ENGINE_LOCATION", "us-central1")


def client() -> vertexai.Client:
    return vertexai.Client(project=PROJECT, location=LOCATION)


def deployed_agent_name() -> str:
    """Resource name written by `make deploy` into deployment_metadata.json."""
    meta = json.loads((ROOT / "deployment_metadata.json").read_text())
    name = meta.get("remote_agent_engine_id")
    if not name or name == "None":
        raise SystemExit("No deployed agent found. Run `make deploy` first.")
    return name
