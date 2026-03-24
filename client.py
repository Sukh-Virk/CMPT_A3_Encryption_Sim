import socket
import json
import threading
import sys
import time

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
        self.running = True

    def send(self, data):
        try:
            self.writer.write(json.dumps(data) + '\n')
            self.writer.flush()
        except Exception as e:
            print(f'Send error: {e}')

    def receive_loop(self):
        while self.running:
            try:
                line = self.reader.readline()
                if not line:
                    break
                    
                data = json.loads(line.strip())
                
                if data['type'] == 'message':
                    # Send message to stdout (will be caught by Node)
                    print(f"{data['from']}: {data['payload']}")
                    sys.stdout.flush()
                    
                elif data['type'] == 'user_list':
                    # Send user list to stdout
                    print('Users: ' + ', '.join(data['users']))
                    sys.stdout.flush()
                    
                elif data['type'] == 'register_ok':
                    # Send registration confirmation
                    print('Registered')
                    sys.stdout.flush()
                    
                elif data['type'] == 'error':
                    # Send error to stdout
                    print(f'Error: {data["message"]}')
                    sys.stdout.flush()
                    
            except Exception as e:
                if self.running:
                    print(f'Error in receive loop: {e}')
                    sys.stdout.flush()
                break

    def run(self):
        # Send registration to Python server
        print(f"Sending registration for {self.username}")
        sys.stdout.flush()
        self.send({'type': 'register', 'username': self.username})
        
        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        receive_thread.start()
        
        # Read commands from stdin (from Node WebSocket)
        while self.running:
            try:
                cmd = sys.stdin.readline().strip()
                if not cmd:
                    continue
                
                print(f"Processing command: {cmd}")
                sys.stdout.flush()
                    
                if cmd.startswith('/msg '):
                    parts = cmd.split(' ', 2)
                    if len(parts) != 3:
                        print('Usage: /msg target message')
                        sys.stdout.flush()
                        continue
                    target, text = parts[1], parts[2]
                    print(f"Sending message to {target}: {text}")
                    sys.stdout.flush()
                    self.send({'type': 'message', 'to': target, 'payload': text})
                    
                elif cmd == '/users':
                    print("Requesting user list")
                    sys.stdout.flush()
                    self.send({'type': 'user_list'})
                    
                elif cmd == '/quit':
                    break
                    
            except Exception as e:
                print(f'Error processing command: {e}')
                sys.stdout.flush()
                break
        
        self.running = False
        self.sock.close()

def main():
    if len(sys.argv) < 3:
        print('Error: Missing username or password')
        sys.stdout.flush()
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Starting client for {username}")
    sys.stdout.flush()
    
    try:
        client = Client(username, password)
        client.run()
    except Exception as e:
        print(f'Error: {e}')
        sys.stdout.flush()

if __name__ == '__main__':
    main()