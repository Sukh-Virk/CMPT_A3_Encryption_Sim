import socket
import json
import threading
import sys
from crypto_utils import encrypt_message, decrypt_message

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
            sys.stdout.flush()

    def receive_loop(self):
        while self.running:
            try:
                line = self.reader.readline()
                if not line:
                    break
                    
                data = json.loads(line.strip())
                
                if data['type'] == 'message':
                    # Decrypt the message payload
                    encrypted_payload = data['payload']
                    try:
                        decrypted_text = decrypt_message(encrypted_payload, self.password)
                        # Send decrypted message to stdout (will be caught by Node)
                        print(f"{data['from']}: {decrypted_text}")
                        sys.stdout.flush()
                    except ValueError as e:
                        print(f"Error: Failed to decrypt message from {data['from']}")
                        sys.stdout.flush()
                    
                elif data['type'] == 'user_list':
                    # Send user list to stdout
                    print('Users: ' + ', '.join(data['users']))
                    sys.stdout.flush()
                    
                elif data['type'] == 'register_ok':
                    # Send registration confirmation
                    msg = data.get('message', 'Registered')
                    print(msg)
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
        # Send registration with password to Python server
        print(f"Sending registration for {self.username}")
        sys.stdout.flush()
        self.send({
            'type': 'register', 
            'username': self.username,
            'password': self.password
        })
        
        # Start receive thread
        receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        receive_thread.start()
        
        # Read commands from stdin (from Node WebSocket)
        while self.running:
            try:
                cmd = sys.stdin.readline().strip()
                if not cmd:
                    continue
                
                if cmd.startswith('/msg '):
                    parts = cmd.split(' ', 2)
                    if len(parts) != 3:
                        print('Usage: /msg target message')
                        sys.stdout.flush()
                        continue
                    target, text = parts[1], parts[2]
                    
                    # Encrypt the message before sending
                    encrypted_text = encrypt_message(text, self.password)
                    
                    # Send encrypted message to server
                    self.send({
                        'type': 'message', 
                        'to': target, 
                        'payload': encrypted_text
                    })
                    
                elif cmd == '/users':
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