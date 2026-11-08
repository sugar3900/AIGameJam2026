#!/usr/bin/env python3
"""
Run a Python file (or snippet) inside the *running* Unreal Editor via the
PythonScriptPlugin remote-execution protocol.

    python3 Tools/run_in_editor.py Tools/Editor/build_apartment.py
    python3 Tools/run_in_editor.py -c "import unreal; unreal.log('hi')"

Requires Project Settings > Plugins > Python > Enable Remote Execution
(already on in Config/DefaultEngine.ini).
"""
import argparse
import os
import sys
import time

ENGINE = os.environ.get("UE_ENGINE_DIR", "/Users/Shared/Epic Games/UE_5.8/Engine")
sys.path.insert(0, os.path.join(ENGINE, "Plugins/Experimental/PythonScriptPlugin/Content/Python"))
import remote_execution as rex  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("-c", "--command")
    ap.add_argument("--timeout", type=float, default=600)
    args = ap.parse_args()

    if args.command:
        command, mode = args.command, rex.MODE_EXEC_FILE
    elif args.file:
        command, mode = os.path.abspath(args.file), rex.MODE_EXEC_FILE
    else:
        ap.error("pass a file or -c")

    cfg = rex.RemoteExecutionConfig()
    cfg.multicast_bind_address = "0.0.0.0"
    remote = rex.RemoteExecution(cfg)
    remote.start()
    try:
        # Wait specifically for this checkout; never fall back to another project.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        deadline = time.time() + 20
        node = None
        while time.time() < deadline:
            node = next((n for n in remote.remote_nodes if os.path.realpath(n.get("project_root", "")) == os.path.realpath(here)), None)
            if node:
                break
            time.sleep(0.2)
        if not node:
            print("No editor found for this worktree", file=sys.stderr)
            return 2
        remote.open_command_connection(node["node_id"])
        result = remote.run_command(command, unattended=True, exec_mode=mode, raise_on_failure=False)
        for entry in result.get("output", []):
            print(f"[{entry['type']}] {entry['output']}".rstrip())
        if not result.get("success"):
            print("FAILED:", result.get("result"), file=sys.stderr)
            return 1
        return 0
    finally:
        remote.stop()


if __name__ == "__main__":
    sys.exit(main())
