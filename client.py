from crypto_utils import encrypt_message, decrypt_message
import socket
import json
import threading
import sys

HOST = '127.0.0.1'
PORT = 5000

class Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.reader = self.sock.makefile('r')
        self.writer = self.sock.makefile('w')

    def send(self, data):
        try:
            self.writer.write(json.dumps(data) + '\n')
            self.writer.flush()
        except Exception as e:
            print(f"Send error: {e}")

    def receive_loop(self):
        try:
            while True:
                data = json.loads(self.reader.readline())
                if data['type'] == 'register_ok':
                    print("Registered successfully")
                elif data['type'] == 'user_list':
                    print(f"Users: {', '.join(data['users'])}")
                elif data['type'] == 'message':
                    decrypted = decrypt_message(data['payload'], self.password)
                    print(f"{data['from']}: {decrypted}")
                elif data['type'] == 'error':
                    print(f"Error: {data['message']}")
        except Exception as e:
            print(f"Receive error: {e}")

    def run(self):
        self.send({'type': 'register', 'username': self.username})
        threading.Thread(target=self.receive_loop).start()
        
        # Read commands from stdin (from backend)
        for line in sys.stdin:
            line = line.strip()
            if line.startswith('/msg '):
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    to_user, msg = parts[1], parts[2]
                    encrypted = encrypt_message(msg, self.password)
                    self.send({'type': 'message', 'to': to_user, 'payload': encrypted})
            elif line == '/users':
                # Note: Server doesn't have a /users command; this is handled by backend sending /users, but client can request user list if needed
                pass
            elif line == '/quit':
                break
        self.sock.close()

def main():
    username = input("Username: ")
    password = input("Shared password: ")
    client = Client(username, password)
    client.run()

if __name__ == "__main__":
    main()