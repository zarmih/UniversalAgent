import argparse
import sys
import time

import requests

API_URL = "http://127.0.0.1:8765"

def main():
    parser = argparse.ArgumentParser(description="Universal Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("health")
    subparsers.add_parser("doctor")
    
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("goal", type=str)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("task_id", type=str)

    subparsers.add_parser("list")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("task_id", type=str)

    events_parser = subparsers.add_parser("events")
    events_parser.add_argument("task_id", type=str)

    evidence_parser = subparsers.add_parser("evidence")
    evidence_parser.add_argument("task_id", type=str)

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("task_id", type=str)

    deny_parser = subparsers.add_parser("deny")
    deny_parser.add_argument("task_id", type=str)
    deny_parser.add_argument("--reason", type=str, default="")

    cancel_parser = subparsers.add_parser("cancel")
    cancel_parser.add_argument("task_id", type=str)

    subparsers.add_parser("agy-status")
    subparsers.add_parser("agy-start")
    subparsers.add_parser("agy-stop")
    agy_submit_parser = subparsers.add_parser("agy-submit")
    agy_submit_parser.add_argument("goal", type=str)

    # Legacy alias
    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("goal", type=str)

    args = parser.parse_args()

    try:
        if args.command == "health" or args.command == "doctor":
            r = requests.get(f"{API_URL}/health")
            print(r.json())
        elif args.command == "create":
            r = requests.post(f"{API_URL}/tasks", json={"goal": args.goal})
            print(r.json())
        elif args.command == "submit":
            r = requests.post(f"{API_URL}/tasks", json={"goal": args.goal})
            task = r.json()
            requests.post(f"{API_URL}/tasks/{task['id']}/run")
            time.sleep(1)
            r2 = requests.get(f"{API_URL}/tasks/{task['id']}")
            print(r2.json())
        elif args.command == "run":
            r = requests.post(f"{API_URL}/tasks/{args.task_id}/run")
            print(r.json())
        elif args.command == "list":
            r = requests.get(f"{API_URL}/tasks")
            for t in r.json():
                print(f"{t['id']} [{t['status']}] {t['goal']}")
        elif args.command == "show":
            r = requests.get(f"{API_URL}/tasks/{args.task_id}")
            print(r.json())
        elif args.command == "events":
            r = requests.get(f"{API_URL}/tasks/{args.task_id}/events")
            for e in r.json():
                print(f"[{e['timestamp']}] {e['status_from']} -> {e['status_to']} : {e['reason']}")
        elif args.command == "evidence":
            r = requests.get(f"{API_URL}/tasks/{args.task_id}/evidence")
            for e in r.json():
                print(f"[{e['timestamp']}] {e['worker']} - {e['summary']} (Exit: {e['exit_code']})")
        elif args.command == "approve":
            r = requests.post(f"{API_URL}/tasks/{args.task_id}/approve")
            print(r.json())
        elif args.command == "deny":
            r = requests.post(f"{API_URL}/tasks/{args.task_id}/deny", json={"action": "deny", "reason": args.reason})
            print(r.json())
        elif args.command == "cancel":
            r = requests.post(f"{API_URL}/tasks/{args.task_id}/cancel")
            print(r.json())
        elif args.command == "agy-status":
            r = requests.get(f"{API_URL}/agy/status")
            print(r.json())
        elif args.command == "agy-start":
            r = requests.post(f"{API_URL}/agy/start")
            print(r.json())
        elif args.command == "agy-stop":
            r = requests.post(f"{API_URL}/agy/stop")
            print(r.json())
        elif args.command == "agy-submit":
            r = requests.post(f"{API_URL}/agy/submit", json={"goal": args.goal})
            print(r.json())
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
