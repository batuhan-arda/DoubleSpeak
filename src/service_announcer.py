# service_announcer.py:

from socket import *
import json
from datetime import datetime
import time

class Service_Announcer:
    def __init__(self):
        self.username = input("Enter username: ")
        print("Welcome " + self.username)
        self.broadcast_ip = "192.168.1.255"
        self.port = 6000
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.last_update = 0  # Initialize the last broadcast timestamp

    def announce_presence(self):
        payload = json.dumps({"username": self.username}).encode('utf-8')
        while True:
            self.last_update = time.time()  # Record the time of the broadcast
            self.socket.sendto(payload, (self.broadcast_ip, self.port))
            #print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Broadcasted presence as {self.username}")
            time.sleep(8)

if __name__ == "__main__":
    announcer = Service_Announcer()
    announcer.announce_presence()