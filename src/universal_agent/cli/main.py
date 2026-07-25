import argparse
import sys
import requests

API_URL = "http://127.0.0.1:8765"

def main():
    parser = argparse.ArgumentParser(description="Universal Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    health_parser = subparsers.add_parser("health")
    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("goal", type=str)

    args = parser.parse_args()

    if args.command == "health":
        try:
            r = requests.get(f"{API_URL}/health")
            print(r.json())
        except Exception as e:
            print(f"Error connecting to API: {e}")
            sys.exit(1)
    elif args.command == "submit":
        try:
            r = requests.post(f"{API_URL}/task", json={"goal": args.goal})
            print(r.json())
        except Exception as e:
            print(f"Error connecting to API: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
