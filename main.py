#main.py:

import threading
import time
import json
import os
from datetime import datetime

from src.service_announcer import Service_Announcer
from src.peer_discovery import Peer_Discovery
from src.chat_responder import start_server
from src.chat_initiator import handle_chat, view_history  

PEER_FILE = "peers.json"

def print_peers(peer_file: str, local_username: str):
    """ 
    Load peers.json, and print all peers seen in the last 15m,
    marking those seen in last 10s as Online, otherwise Away.
    """
    now = time.time()
    try:
        with open(peer_file, "r") as f:
            peers = json.load(f)
    except:
        peers = {}

    print(f"\nLogged in as: {local_username}")
    print(f"Active Peers ({datetime.now().strftime('%H:%M:%S')}):")
    for ip, info in peers.items():
        name = info.get("username", "Unknown")
        if name == local_username:
            continue
        last_seen = info.get("last_seen", 0)
        elapsed = now - last_seen
        status = "Online" if elapsed <= 10 else "Away"
        print(f" - {name:10s} {status:7s} {ip}")
    print()

def main():
    
    announcer = Service_Announcer()
    local_username = announcer.username
    
    try:
        with open(PEER_FILE, "w") as f:
            json.dump({}, f)
    except Exception as e:
        print("Error clearing peers.json:", e)

    pd = Peer_Discovery()
    pd.start()

    threading.Thread(target=announcer.announce_presence, daemon=True).start()

    threading.Thread(target=start_server, daemon=True).start()

    try:
        while True:
            print_peers(PEER_FILE, local_username)

            print("Options:")
            print("  1. Users")
            print("  2. Chat")
            print("  3. History")
            print("  4. Exit")
            choice = input("Choose an option: ").strip().lower()

            if choice in ("1", "users"):
                # just reprint peers and loop
                continue

            elif choice in ("2", "chat"):
                handle_chat()

            elif choice in ("3", "history"):
                view_history()

            elif choice in ("4", "exit"):
                break

            else:
                print("Invalid option, try again.")

    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        pd.stop()


if __name__ == "__main__":
    main()