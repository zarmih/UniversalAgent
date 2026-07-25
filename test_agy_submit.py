from universal_agent.core.workers.agy import AgyAdapter
import sys
import time

adapter = AgyAdapter()
adapter.enabled = True
res = adapter.submit("DO NOT USE ANY TOOLS. DO NOT SEARCH. Output exactly: UA_AGY_WORKER_OK", timeout=60, require_approval=False)
print("Result:", res)
