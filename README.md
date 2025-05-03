# Peer-to-Peer Chat Application

This project is a local-network-based peer-to-peer (P2P) chat application written in Python. It enables multiple users on the same network to discover each other and communicate via either plain text or secure encrypted messages using TCP sockets and a basic Diffie–Hellman key exchange.

---

## 📦 Components

The system consists of the following main modules:

- **Service Announcer**: Periodically broadcasts your presence to the network via UDP.
- **Peer Discovery**: Listens for incoming UDP broadcasts and maintains a list of recently seen peers.
- **Chat Initiator**: Allows you to choose a peer, initiate a TCP connection, and send messages (plain or encrypted).
- **Chat Responder**: Listens for incoming TCP messages and handles decryption or plain text logging.

---

## 🚀 How to Run

1. Make sure all devices are on the same local network.
2. Run `main.py` on each computer.
3. Enter your username when prompted.
4. Use the menu to view peers, chat with a peer, or view chat history.

---

## 🔐 Secure Messaging

- Uses **Diffie–Hellman Key Exchange** (with P=19, G=2) to generate a shared key.
- **DES encryption** is used via the `pyDes` library.
- Encrypted messages are base64-encoded and transmitted as JSON over TCP.

---

## 🛠 Platform and Requirements

- **Platform**: Windows 11 (tested)
- **Python Version**: 3.9
- **Dependencies**:
  - `pyDes`
  - `socket`
  - `threading`
  - `json`
  - `base64`
  - `datetime`

## ⚠️ Known Limitations

- Only supports terminal interaction — no GUI available.
- Peer discovery relies on static IP addresses; changing IPs during runtime may cause issues in tracking peers.
- Secure chat uses a small prime number (P=19), which is **not cryptographically secure** and should not be used in production systems.
- The chat history (`chatlog.txt`) is shared across all conversations and not separated per user or session.
- The encryption method (DES) is outdated and used here only for educational purposes.
- If a peer closes the program unexpectedly, their "Online" status may not update until the 15-minute timeout expires.

## 👥 Contributors

- **Can Sarı** – Implemented the peer discovery system, wrote the project report, and contributed to the UDP communication modules.
- **Batuhan Arda Bekar** – Developed the service announcer, performed Wireshark captures and analysis, and contributed to the documentation.
- **Hüseyin Can Gülkan** – Implemented the TCP chat logic, encryption/decryption mechanisms, and handled overall testing of the application.

---

## 📝 License

This project is intended solely for educational use as part of the CMP2204 course at Bahçeşehir University.  
No warranties or guarantees are provided.  
Not suitable for real-world deployment or secure communication purposes.
