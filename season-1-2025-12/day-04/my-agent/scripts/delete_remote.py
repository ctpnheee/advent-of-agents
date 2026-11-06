"""Delete the deployed agent (and its sessions) so it stops costing money.

Usage: uv run python scripts/delete_remote.py
"""

import json

from _common import ROOT, client, deployed_agent_name

name = deployed_agent_name()
if input(f"Delete {name}? Type 'yes' to confirm: ").strip().lower() != "yes":
    raise SystemExit("Cancelled.")

client().agent_engines.delete(name=name, force=True)  # force=True also removes its sessions
(ROOT / "deployment_metadata.json").write_text(
    json.dumps({"remote_agent_engine_id": "None", "deployment_timestamp": "None"}, indent=2)
)
print("Deleted. deployment_metadata.json reset.")
