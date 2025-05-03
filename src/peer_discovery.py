# peer_discovery.py:

import socket
import json
import time
import threading
import datetime 

class Peer_Discovery: 
    def __init__(self, port=6000, 
                 save_interval = 10, 
                 peer_file="peers.json"):
        self.port = port
        self.save_interval = save_interval
        self.peer_file = peer_file
        self.peer_dict = {} # "username": str, "last_seen": float
        self.online = True
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET # IPv4 family
                        , socket.SOCK_DGRAM # UDP
                        ) 
        self.sock.bind(('', self.port))
        self.sock.settimeout(1.0) # regularly check online status
    
    def start(self):
        # Two background threads: Listener and Saver threads
        # daemon stops the thread automatically on end of program
        self.listener_thread = threading.Thread(target=self.listen, daemon=True)
        self.saver_thread = threading.Thread(target=self.save_periodically, daemon=True)
        self.listener_thread.start() # Listener thread
        self.saver_thread.start() # Saver thread

    def listen(self):
        while self.online:
            try:
                data, addr = self.sock.recvfrom(1024) # 1024 byte limit, wait for UDP packets
                # addr = (ip, port) of sender
                ip = addr[0]
                message = data.decode()
                json_data = json.loads(message)
                username = json_data.get("username")
                timestamp = time.time()

                # ignore messages with no username
                if username is None: 
                    continue
                
                # Convert Unix timestamp to a human‐readable string
                timestamp = time.time()
                human_readable = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                if ip in self.peer_dict:
                    self.peer_dict[ip]["last_seen"] = timestamp
                
                else:
                    self.peer_dict[ip] = {"username": username, "last_seen": timestamp}
                    print(f" {username}: is online \n")
            
            except socket.timeout:
                continue
            
            except Exception as e:
                print(f"Error receiving UDP message: {e}")
    
    def save_periodically(self):
        while self.online:
            time.sleep(self.save_interval)

            # parse JSON
            try:
                with open(self.peer_file, "w") as f:
                    json.dump(self.peer_dict, f)
            except Exception as e:
                print(f"Failure to save : {e}")
    
    def stop(self):
        print("Stopping Peer Discovery..")
        self.online = False
        self.listener_thread.join()
        self.saver_thread.join()
        self.sock.close()
        print("Peer Discovery finished.")

    def get_peers(self):
        return self.peer_dict
    

if __name__ == "__main__":
    pd = Peer_Discovery()
    pd.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pd.stop() # run until user presses Ctrl+C