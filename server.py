import socket
import json
import threading

HOST = '0.0.0.0'
PORT = 5000

clients = {}
lock = threading.Lock()

def send_json(writer, data):
    try:
        writer.write(json.dumps(data) + '\n')
        writer.flush()
    except Exception as e:
        print(f'Send error: {e}')

def broadcast_users():
    with lock:
        users = list(clients.keys())
        for username, (conn, writer) in clients.items():
            send_json(writer, {'type': 'user_list', 'users': users})

def handle_client(conn, addr):
    reader = conn.makefile('r')
    writer = conn.makefile('w')
    username = None
    
    try:
        raw = reader.readline().strip()
        if not raw:
            print(f"No data from {addr}")
            return
        
        data = json.loads(raw)
        if data.get('type') != 'register':
            print(f"Invalid registration from {addr}: {data}")
            return
            
        username = data.get('username')
        print(f"Registration attempt for {username} from {addr}")
        
        with lock:
            if username in clients:
                print(f"Username {username} already taken")
                send_json(writer, {'type': 'error', 'message': 'Username taken'})
                return
            clients[username] = (conn, writer)
        
        print(f'{username} connected successfully')
        send_json(writer, {'type': 'register_ok'})
        broadcast_users()
        
        while True:
            raw = reader.readline().strip()
            if not raw:
                break
                
            data = json.loads(raw)
            print(f"Received from {username}: {data}")
            
            if data.get('type') == 'message':
                to_user = data.get('to')
                payload = data.get('payload')
                
                with lock:
                    if to_user in clients:
                        _, to_writer = clients[to_user]
                        print(f"Forwarding message from {username} to {to_user}")
                        send_json(to_writer, {
                            'type': 'message',
                            'from': username,
                            'payload': payload
                        })
                    else:
                        print(f"User {to_user} not found")
                        send_json(writer, {
                            'type': 'error',
                            'message': f'User {to_user} not found'
                        })
                        
            elif data.get('type') == 'user_list':
                with lock:
                    users = list(clients.keys())
                    print(f"Sending user list to {username}: {users}")
                    send_json(writer, {'type': 'user_list', 'users': users})
                    
    except Exception as e:
        print(f'Error handling client {username}:', e)
    finally:
        if username:
            with lock:
                clients.pop(username, None)
            print(f'{username} disconnected')
            broadcast_users()
        
        try:
            conn.close()
        except:
            pass

def start():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f'Python server running on {HOST}:{PORT}')
    
    while True:
        conn, addr = s.accept()
        print(f"New connection from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    start()