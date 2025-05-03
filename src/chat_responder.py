# chat_responder.py

import socket
import threading
import json
import base64
from datetime import datetime
from pyDes import triple_des, PAD_PKCS5  # pip install pyDes
import os

# Diffie–Hellman parameters (must match initiator)
P = 19
G = 2
PORT = 6001

LOG_FILE = "chatlog.txt"
PEER_FILE = "peers.json"   

def get_username_from_ip(ip: str) -> str:
    """Optional: look up the peer’s username in peers.json."""
    try:
        with open(PEER_FILE, "r") as f:
            peers = json.load(f)
        return peers[ip]["username"]
    except:
        return ip

def write_log(entry: str):
    """Append a single line to the chat log."""
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def handle_client(conn: socket.socket, addr):
    ip = addr[0]
    try:
        # First receive the key payload
        key_raw = conn.recv(4096)
        if not key_raw:
            return
        msg = json.loads(key_raw.decode())
        username = get_username_from_ip(ip)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Secure
        if "key" in msg:
            A = int(msg["key"])
            b = 6
            B = pow(G, b, P)
            shared = pow(A, b, P)

            des_key = str(shared).ljust(24).encode()[:24]
            cipher = triple_des(des_key, padmode=PAD_PKCS5)

            # Send back our B
            conn.send(json.dumps({"key": str(B)}).encode())

            # Receive encrypted message
            enc_chunks = b""
            conn.settimeout(5.0)  # wait up to 3 sec
            while True:
                try:
                    part = conn.recv(4096)
                    if not part:
                        break
                    enc_chunks += part
                except socket.timeout:
                    break

            if not enc_chunks:
                print(f"[{ts}] {username}@{ip}: No encrypted message received.")
                return

            try:
                enc_msg = json.loads(enc_chunks.decode())
                token = enc_msg.get("encrypted_message", "")
                if token:
                    ciphertext = base64.b64decode(token)
                    plaintext = cipher.decrypt(ciphertext).decode()
                    print(f"[{ts}] {username} (secure)@{ip}: {plaintext}")
                    write_log(f"{ts} | {username} | RECEIVED (Secure): {plaintext}")
            except Exception as e:
                print(f"Failed to parse encrypted payload: {e}")
                print("Raw data was:", enc_chunks)

        elif "unencrypted_message" in msg:
            text = msg["unencrypted_message"]
            print(f"[{ts}] {username} (plain)@{ip}: {text}")
            write_log(f"{ts} | {username} | RECEIVED (Plain): {text}")

        else:
            print(f"[{ts}] {username}@{ip}: Unknown payload: {msg}")

    except Exception as e:
        print(f"Error handling client {ip}: {e}")

    finally:
        conn.close()


def start_server():
    """Launch TCP server on PORT, one thread per connection."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("", PORT))
    srv.listen()
    print(f"\nChatResponder listening on TCP port {PORT}...")

    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nResponder shutting down...")
    finally:
        srv.close()

if __name__ == "__main__":
    start_server()
