# **CMPT 371 A3 Socket Programming `End-to-end Encrypted Messenger`**

**Course:** CMPT 371 \- Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  

## **Group Members**

| Name | Student ID | Email |
| :---- | :---- | :---- |
| Julianna Morena | 301577023 | jam46@sfu.ca |
| Sukhman Virk | 301468282 | ssv12@sfu.ca |

## **1\. Project Overview & Description**

This project is a secure, multi-user chat application built using Python's Socket API (TCP) for backend communication and React with WebSockets for the frontend interface. It allows multiple clients to connect to a central Python server, register with unique usernames, and exchange private messages with other online users in real-time. The system features end-to-end message encryption using a shared password, ensuring that message content remains confidential even if intercepted. The architecture consists of three layers: a Python server managing user sessions and message routing, a Node.js WebSocket server that bridges the React frontend with the Python client processes, and a React-based GUI that provides a modern, responsive chat experience. The server handles user authentication, maintains real-time user lists, validates message formats, and ensures that messages are only delivered to intended recipients, preventing unauthorized access or message interception.

## **2\. System Limitations & Edge Cases**

As required by the project specifications, we have identified and handled (or defined) the following limitations and potential issues within our application scope:

* **Cross-Layer Communication & Process Management:**
  * <span style="color: green;">*Solution:*</span> We established a three-tier architecture where the React frontend communicates via WebSocket to a Node.js server, which spawns individual Python client processes. Each Python client maintains a persistent TCP connection to the central Python server. The Node.js server acts as a bidirectional bridge, forwarding messages between the browser and Python processes while managing process lifecycle and stdout/stderr buffering.

   * <span style="color: red;">*Limitation:*</span> Process spawning introduces latency and resource overhead per connection. In a high-traffic scenario, the Node.js server would need to implement connection pooling, reuse Python processes, or consider a unified WebSocket-native Python backend to eliminate the intermediary process layer.
 
* **User State Management & Consistency:**
  * <span style="color: green;">*Solution:*</span> The Python server maintains a centralized dictionary of connected clients and their associated connection objects. When users join or leave, the server broadcasts the updated user list to all connected clients, ensuring consistency across the distributed system. The React frontend updates its UI immediately upon receiving these broadcasts

   * <span style="color: red;">*Limitation:*</span> If a client disconnects abruptly (e.g., network failure, browser crash), the server may not immediately detect the disconnection until the TCP keepalive timeout occurs. This can result in stale user entries being displayed to other clients temporarily. A production implementation would require TCP keepalive settings or periodic heartbeat messages to detect stale connections more aggressively
 
* **Message Encryption & Data Privacy:**
  * <span style="color: green;">*Solution:*</span> We integrated encryption functionality using a shared password that both communicating parties must know. Messages are encrypted on the client side before transmission and decrypted on the receiving client, ensuring that even if network traffic is intercepted, message contents remain confidential.
    
  * <span style="color: red;">*Limitation:*</span> The encryption key (shared password) is transmitted once during initial connection and stored in memory on both the Python client and server. A more secure implementation would use public-key cryptography to establish session keys without exposing the shared secret, and implement proper key rotation mechanisms.
 
* **Input Validation & Security:** 
  * <span style="color: green;">*Solution:*</span> We implemented validation at multiple levels to prevent malformed data from crashing the system. The React frontend isables message sending when no recipient is selected or message is empty, preventing invalid WebSocket messages. The Python client validates message format (/msg recipient message) before sending to server, catching malformed commands, and the Python server verifies that incoming JSON payloads contain required fields (type, username, to, payload) before processing, and gracefully ignores malformed messages.

  * <span style="color: red;">*Limitation:*</span> While we validate message structure, we do not implement message rate limiting, content filtering, or flood protection. A malicious user could theoretically spam the server with rapid messages, consuming resources. Additionally, message encryption is implemented but the shared password is transmitted in plaintext during initial connection, which would require TLS/SSL for proper production deployment.

## **3\. Video Demo**

<span style="color: purple;">***RUBRIC NOTE: Include a clickable link.***</span>  
Our 2-minute video demonstration covering connection establishment, data exchange, real-time messaging, and process termination can be viewed below:  
[**▶️ Watch Project Demo on YouTube**](https://youtu.be/7kttlxfOX04)

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

* **Python 3.7 or higher** or higher.  
* *External pip installation required:* The `cryptography` library must be installed for encryption functionality.
* Node.js 14 or higher (for WebSocket server)
* npm (for managing Node.js and React dependencies)
* VS Code 

<span style="color: purple;">***RUBRIC NOTE: No external libraries are required. Therefore, a requirements.txt file is not strictly necessary for dependency installation, though one might be included for environment completeness.***</span>

## **4\. Step-by-Step Run Guide**

<span style="color: purple;">***RUBRIC NOTE: The grader must be able to copy-paste these commands.***</span>


### **Step 1: Start the Python Server**

Open your terminal and navigate to the project folder. The server binds to 127.0.0.1 on port 5000\.  
```bash
python server.py  
# Console output: "Python server running on 0.0.0.0:5000"
```

### **Step 2: Start the Node.js WebSocket Server**

Open a **new** terminal window (keep the first server running). The Node.js server acts as a bridge between the React frontend and Python clients, binding to port 3001.  
```bash
node server.js  
# Console output: "WebSocket server listening on ws://localhost:3001"
```

### **Step 3: Start the React Application**

1. Open a **third** terminal window. Navigate to the React app directory from the project folder.
 ```bash
cd app
```  

2. Within third terminal, install dependencies through npm (only has to be done first time after cloning repo, otherwise skip).
 ```bash
npm install
```  
3. Within third terminal, start React development server.
```bash
npm run dev  
# Console output:
# > 371-project@0.0.0 dev
# > vite

# VITE v8.0.2  ready in [time] ms

#  ➜  Local:   http://localhost:5173/ (note: this should be a link, might be different port)
#  ➜  Network: use --host to expose
#  ➜  press h + enter to show help
```

### **Step 4: Connect Both Users**

1. Connect the first user by opening the link given in step 3 in a new window.
2. Enter a username (e.g., "Alice") and a shared password (e.g., "secret123").
3. Click Connect.
4. Connect the second user by opening the link given in step 3 in a **different** window.
5. Enter a different username (e.g., "Bob") and the same shared password (e.g., "secret123").
6. Click Connect (both users will see each other in the Online Users panel).

### **Step 5: Start Chatting**
1. Within the first window, select a recipient from the Online Users panel by clicking on their name (e.g., "Bob"). The selected recipient will be highlighted in green. You will not need to select if there is only one other person in the room.
2. Type a message in the input box: (e.g., `Hello Bob!`).
3. Click the Send button.
4. The message will appear in:
    * Your chat window (as "Alice → Bob: Hello Bob!")
    * Bob's chat window (as "Alice: Hello Bob!"
5. Bob can now reply by selecting "Alice" and typing a response.
6. To disconnect, simply close the browser tab. The WebSocket connection and Python client process for that user closes. The Python server process terminates when all windows are closed.

## **5\. Technical Protocol Details (JSON over TCP & Inter-Process Communication)**

We designed a custom application-layer protocol for data exchange across three distinct communication channels: JSON over TCP between Python client and Python server, WebSocket messaging between React frontend and Node.js server, and stdin/stdout piping between Node.js and Python client processes.

### Layer 1: Python Client ↔ Python Server (TCP/JSON Protocol) 

* **Message Format:** `{"type": <string>, "<fields>": <data>}`  
* **Handshake Phase:**
  * Client sends: `{"type": "register", "username": "Alice", "password": "secret123"}`
  * Server responds (success): `{"type": "register_ok", "message": "Room created! You are the host."}` / `{"type": "register_ok", "message": "Joined room! Hosted by Alice"}`
  * Server responds (error): `{"type": "error", "message": "Username taken"}` / `{"type": "error", "message": "Incorrect room password. Cannot join."}`
* **User Management Phase:**  
  * Client sends: `{"type": "user_list"}`  
  * Server broadcasts: `{"type": "user_list", "users": ["Alice", "Bob", "Charlie"]}`
 * **Messaging Phase:**
   * Client sends: `{"type": "message", "to": "Bob", "payload": "<encrypted>"}`
   * Server forwards to recipient: (success): `{"type": "message", "from": "Alice", "payload": ""<encrypted>"}`
   * Server responds (error): `{"type": "error", "message": "User not found"}`

### Layer 2: Node.js ↔ Python Client (stdin/stdout Process Communication)

* **Message Format:** Text-based commands (stdin) and formatted strings (stdout).
* **Handshake Phase:**
  * Node.js sends (stdin): `<username>`
  * Node.js sends (stdin): `<password>`
  * Python responds (stdout, success):  `"Room created! You are the host."` / `"Joined room! Hosted by Alice"`
  * Python responds (stdout, error): `"Error: Incorrect room password. Cannot join."`
* **User Management Phase:**  
   * Node.js sends (stdin): `"/users"`  
   * Python responds (stdout): `"Users: Alice, Bob, Charlie"`
 * **Messaging Phase:**
   * Node.js sends (stdin): `"/msg Bob Bob Hello!"` 
   * Python client encrypts:	`encrypt_message("Hello Bob!", password)`
   * Python sends to server:	`Encrypted JSON payload`
   * Python forwards received message (stdout):	`"Alice: Hello Bob!" (decrypted)`
   * Python responds (stdout, error): `"Error: User not found"`

### Layer 3: React ↔ Node.js (WebSocket Protocol)

* **Message Format:** Text commands and responses.
* **Handshake Phase:**
  * React sends: `<username>`
  * React sends: `<password>`
  * Node.js responds (success): `"Room created! You are the host."` / `"Joined room! Hosted by Alice"`
  * Node.js response (error): `"Error: Incorrect room password. Cannot join.""`
* **User Management Phase:**  
  * React sends: `"/users"`  
  * Node.js responds: `"Users: Alice, Bob, Charlie"`
 * **Messaging Phase:**
   * React sends: `"/msg Bob Bob Hello!"` 
   * Node.js forwards decrypted message (success): `"Alice: Hello Bob!"`
   * Node.js responds (error): `"Error: User not found"`

## **6\. Academic Integrity & References**

* **Code Origin:**  
  * No outright Boiler plates were used. Functions were either hand made or altered by copilot or chatgpt for debugging.  
* **Gen AI Usage:**  
  * ChatGPT was used to create a roadmap on where to begin and for brainstorming. It also assisted in debugging functions that weren’t working.
  * GitHub Copilot was used in assisting with generating functions like encryption and decryption. Some functions were handmade but were later altered if there were bugs with the help of GitHub Copilot.
  * DeepSeek assisted in the creation of the README.md.
* **References:**  
 * [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)  
 * [Real Python: Intro to Python Threading](https://realpython.com/intro-to-python-threading/)
 * [Python Sockets (Real Python)](https://realpython.com/python-sockets/)
 * [React Setup (Official Docs)](https://react.dev/learn/start-a-new-react-project)
 * [Vite Guide (React Setup)](https://vitejs.dev/guide/)
 * [Fernet (Symmetric Encryption) – Cryptography Documentation](https://cryptography.io/en/latest/fernet/)
 * [Cryptography Library Documentation](https://cryptography.io/en/latest/)
 * [Python Cryptography Tutorial (Fernet Explained)](https://www.geeksforgeeks.org/fernet-symmetric-encryption-using-cryptography-module-in-python/)
