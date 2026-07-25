#!/usr/bin/env python3
import sys

from universal_agent.core.workers.agy import AgyAdapter


def main():
    adapter = AgyAdapter()
    adapter.enabled = True
    if not adapter.enabled:
        print("Adapter is disabled.")
        sys.exit(1)
        
    print("Submitting smoke task...")
    res = adapter.submit("DO NOT USE ANY TOOLS. DO NOT SEARCH. Output exactly: UA_AGY_WORKER_OK", timeout=60, require_approval=False)
    print("Result:", res)
    if res["status"] != "succeeded":
        sys.exit(1)

if __name__ == "__main__":
    main()
