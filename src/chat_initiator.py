import socket
import json
import time
import base64
import os
from datetime import datetime
from pyDes import triple_des, PAD_PKCS5  

# Diffie–Hellman parameters
P = 19
G = 2
TCP_PORT = 6001

PEER_FILE = "peers.json"
LOG_FILE = "chatlog.txt"


def get_current_peers():
    """Load peers.json and return {username: (ip, status)} for peers seen in last 15m."""
    try:
        with open(PEER_FILE, "r") as f:
            all_peers = json.load(f)
    except:
        return {}

    now = time.time()
    result = {}
    for ip, info in all_peers.items():
        last_seen = info.get("last_seen", 0)
        username = info.get("username", ip)
        if now - last_seen <= 900:
            status = "Online" if now - last_seen <= 10 else "Away"
            result[username] = (ip, status)
    return result


def write_log(entry: str):
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def handle_chat():
    peers = get_current_peers()
    if not peers:
        print("No users found.")
        return

    print("Available users:")
    for name, (_, status) in peers.items():
        print(f" - {name} {status}")

    target = input("Enter the username to chat with: ").strip()
    if target not in peers:
        print("User not found.")
        return

    ip, _ = peers[target]
    secure = input("Secure chat? (y/n): ").strip().lower() == "y"
    msg = input("Enter your message: ").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if secure:
        try:
            a = 5  # private key
            A = pow(G, a, P)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, TCP_PORT))
                s.send(json.dumps({"key": str(A)}).encode())

                data = s.recv(1024)
                resp = json.loads(data.decode())
                B = int(resp.get("key", 0))

                shared_secret = pow(B, a, P)
                des_key = str(shared_secret).ljust(24).encode()[:24]
                cipher = triple_des(des_key, padmode=PAD_PKCS5)

                ciphertext = cipher.encrypt(msg)
                b64 = base64.b64encode(ciphertext).decode()

                s.send(json.dumps({"encrypted_message": b64}).encode())

            write_log(f"{timestamp} | {target} | SENT (Secure): {msg}")
            print("Message sent (secure).")

        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"Error: Could not connect to {target} at {ip}. They may be offline.")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return

    else:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, TCP_PORT))
                s.send(json.dumps({"unencrypted_message": msg}).encode())

            write_log(f"{timestamp} | {target} | SENT (Plain): {msg}")
            print("Message sent (plain).")

        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"Error: Could not connect to {target} at {ip}. They may be offline.")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return


def view_history():
    if not os.path.exists(LOG_FILE):
        print("No chat history.")
        return

    print("\n--- Chat History ---")
    with open(LOG_FILE, "r") as f:
        print(f.read())
    print("--------------------\n")


def main_menu():
    while True:
        print("\nOptions:\n1. Users\n2. Chat\n3. History\n4. Exit")
        choice = input("Choose an option: ").strip().lower()

        if choice in ["1", "users"]:
            peers = get_current_peers()
            if not peers:
                print("No users found.")
            for name, (_, status) in peers.items():
                print(f" - {name} {status}")

        elif choice in ["2", "chat"]:
            handle_chat()

        elif choice in ["3", "history"]:
            view_history()

        elif choice in ["4", "exit"]:
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main_menu()
