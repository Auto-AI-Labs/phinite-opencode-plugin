"""Install the Phinite plugin into OpenCode (Python 3.9+, standard library only).

OpenCode has no package format for commands, agents, skills and MCP servers together, so this copies them into an
OpenCode config folder and adds the `phinite` server to its opencode.json:

    python install.py                      # global: ~/.config/opencode
    python install.py --project <repo>     # one project: <repo>/.opencode
    python install.py --uninstall [--project <repo>]

Then run `opencode mcp auth phinite` to sign in. Re-run after `git pull` to update.
"""
import argparse
import json
import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
MCP_URL = "https://mcp.dev.phinite.ai/mcp"
SERVER = {"type": "remote", "url": MCP_URL}


def target(project):
    if project:
        return pathlib.Path(project).resolve() / ".opencode"
    base = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
    return pathlib.Path(base) / "opencode"


def items(dest):
    """(source, destination) pairs this plugin owns. templates/ goes inside the phinite-project skill, where the
    project script looks when it isn't in a plugin folder."""
    for f in sorted((HERE / "commands").glob("phinite-*.md")):
        yield f, dest / "commands" / f.name
    yield HERE / "agents" / "phinite-builder.md", dest / "agents" / "phinite-builder.md"
    for d in sorted((HERE / "skills").glob("phinite-*")):
        yield d, dest / "skills" / d.name
    yield HERE / "templates", dest / "skills" / "phinite-project" / "templates"


def remove(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def config_file(dest):
    for name in ("opencode.json", "opencode.jsonc"):
        if (dest / name).exists():
            return dest / name
    return dest / "opencode.json"


def set_server(dest, add):
    path = config_file(dest)
    try:
        cfg = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"$schema": "https://opencode.ai/config.json"}
    except ValueError:
        print(f"! {path} has comments or isn't plain JSON; edit it by hand:")
        print('  "mcp": {"servers": {"phinite": ' + json.dumps(SERVER) + "}}   (OpenCode 1.x: \"mcp\": {\"phinite\": ...})")
        return
    mcp = cfg.setdefault("mcp", {})
    v1 = bool(mcp) and "servers" not in mcp          # OpenCode 1.x keeps servers directly under "mcp"
    servers = mcp if v1 else mcp.setdefault("servers", {})
    if add:
        servers["phinite"] = dict(SERVER, enabled=True) if v1 else SERVER
    else:
        servers.pop("phinite", None)
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"{'added' if add else 'removed'} the phinite server in {path}")


def main():
    ap = argparse.ArgumentParser(description="Install the Phinite plugin into OpenCode.")
    ap.add_argument("--project", help="install into <project>/.opencode instead of the global config")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()
    dest = target(args.project)
    dest.mkdir(parents=True, exist_ok=True)
    for src, dst in items(dest):
        remove(dst)
        if not args.uninstall:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src, dst)
    set_server(dest, not args.uninstall)
    if args.uninstall:
        print(f"removed the Phinite commands, agent and skills from {dest}")
    else:
        print(f"installed into {dest}. Restart OpenCode, then sign in: opencode mcp auth phinite")


if __name__ == "__main__":
    main()
