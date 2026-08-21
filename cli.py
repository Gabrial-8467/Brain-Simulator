#!/usr/bin/env python3
"""Aashu CLI — entry point for the Virtual Brain."""
import sys
import os

DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON = os.path.join(DIR, "myenv", "bin", "python")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print("Usage: aashu run [live|deterministic] [port]")
        print("  live            Run Aashu brain server in live mode (default)")
        print("  deterministic   Run Aashu brain server in deterministic mode")
        sys.exit(0)

    if args[0] == "run":
        mode = args[1] if len(args) > 1 else "live"
        port = args[2] if len(args) > 2 else "8000"
        cmd_args = []
        if mode in ("deterministic", "det"):
            cmd_args.append("--deterministic")
        elif mode != "live":
            print(f"Unknown mode: {mode} (use 'live' or 'deterministic')")
            sys.exit(1)
        print(f"Starting Aashu Virtual Brain in {mode} mode on port {port} ...")
        os.execvp(PYTHON, [PYTHON, os.path.join(DIR, "api_server.py"), *cmd_args, "--port", port])
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: aashu run [live|deterministic] [port]")
        sys.exit(1)

if __name__ == "__main__":
    main()
