"""CLI entry point."""
from __future__ import annotations
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="dometic", description="Dometic 39424.602 control")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="Run the daemon").set_defaults(fn=cmd_run)
    sub.add_parser("status", help="Print current state").set_defaults(
        fn=cmd_status)
    args = parser.parse_args(argv)
    if args.cmd is None:
        return cmd_run(args)
    return args.fn(args)


def cmd_run(_args):
    from dometic.daemon import run
    from dometic.api import start_api_in_thread
    start_api_in_thread()
    run()


def cmd_status(_args):
    import urllib.request
    import json
    with urllib.request.urlopen("http://localhost:8080/api/state", timeout=3) as r:
        print(json.dumps(json.loads(r.read()), indent=2))


if __name__ == "__main__":
    sys.exit(main() or 0)
