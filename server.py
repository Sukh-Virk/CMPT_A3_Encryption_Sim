import socket
import json
import threading

HOST = '0.0.0.0'
PORT = 5000

# Store client info with username, connection, writer, and password
clients = {}  # username -> (conn, writer, password)
room_password = None  # The password for the chat room (set by first user)
room_creator = None   # Username of the room creator
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
        for username, (conn, writer, password) in clients.items():
            send_json(writer, {'type': 'user_list', 'users': users})

def handle_client(conn, addr):
    global room_password, room_creator
    
    reader = conn.makefile('r')
    writer = conn.makefile('w')
    username = None
    password = None
    
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
        password = data.get('password', '')
        
        print(f"Registration attempt for {username} from {addr}")
        print(f"Current room password: {room_password if room_password else 'Not set yet'}")
        
        with lock:
            # Check if username already exists
            if username in clients:
                print(f"Username {username} already taken")
                send_json(writer, {'type': 'error', 'message': 'Username taken'})
                return
            
            # Check if room has no users (empty)
            if len(clients) == 0:
                # First user in empty room - they set the password
                room_password = password
                room_creator = username
                print(f"Room created by {username} with password: {room_password}")
                send_json(writer, {'type': 'register_ok', 'message': 'Room created! You are the host.'})
                
                # Store client with password
                clients[username] = (conn, writer, password)
                print(f"User {username} added. Current clients: {list(clients.keys())}")
                print(f"Room password is now: {room_password}")
                
            else:
                # Room has existing users - check password
                if password != room_password:
                    print(f"Password mismatch for {username}. Room password is '{room_password}', got '{password}'")
                    send_json(writer, {'type': 'error', 'message': 'Incorrect room password. Cannot join.'})
                    return  # Don't add the user
                else:
                    print(f"{username} joined with correct password")
                    send_json(writer, {'type': 'register_ok', 'message': f'Joined room! Hosted by {room_creator}'})
                    
                    # Store client with password
                    clients[username] = (conn, writer, password)
                    print(f"User {username} added. Current clients: {list(clients.keys())}")
        
        # If we got here, user was successfully added
        print(f'{username} connected successfully')
        
        # Broadcast updated user list to all clients
        broadcast_users()
        
        # Handle subsequent messages
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
                        _, to_writer, to_password = clients[to_user]
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
        if username and username in clients:
            with lock:
                clients.pop(username, None)
                print(f'{username} disconnected')
                print(f"Remaining clients: {list(clients.keys())}")
                
                # If room becomes empty, reset the room password
                if len(clients) == 0:
                    room_password = None
                    room_creator = None
                    print("Room is empty. Password has been reset. Next user will set new password.")
                # If room creator leaves but others remain, keep the password
                elif username == room_creator:
                    # Find a new room creator (first user in the list)
                    new_creator = list(clients.keys())[0]
                    room_creator = new_creator
                    print(f"Room creator changed from {username} to {new_creator}")
                
                broadcast_users()
        
        try:
            conn.close()
        except:
            pass

def start():
    global room_password, room_creator
    
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