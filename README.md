# **CMPT 371 A3 Socket Programming `End-to-end Encrypted Messenger`**

**Course:** CMPT 371 \- Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  
<span style="color: purple;">***RUBRIC NOTE: As per submission guidelines, only one group member will submit the link to this repository on Canvas.***

## **Group Members**

| Name | Student ID | Email |
| :---- | :---- | :---- |
| Julianna Morena | 301577023 | jam46@sfu.ca |
| Sukhman Virk | 301468282 | john.smith@university.edu |

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
Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, and process termination can be viewed below:  
[**▶️ Watch Project Demo on YouTube**](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

* **Python 3.10** or higher.  
* No external pip installations are required (uses standard socket, threading, json, sys libraries).  
* (Optional) VS Code or Terminal.

<span style="color: purple;">***RUBRIC NOTE: No external libraries are required. Therefore, a requirements.txt file is not strictly necessary for dependency installation, though one might be included for environment completeness.***</span>

## **4\. Step-by-Step Run Guide**

<span style="color: purple;">***RUBRIC NOTE: The grader must be able to copy-paste these commands.***</span>


### **Step 1: Start the Server**

Open your terminal and navigate to the project folder. The server binds to 127.0.0.1 on port 5050\.  
```bash
python server.py  
# Console output: "[STARTING] Server is listening on 127.0.0.1:5050"
```

### **Step 2: Connect Player 1 (X)**

Open a **new** terminal window (keep the server running). Run the client script to start the first client.  
```bash
python client.py  
# Console output: "Connected. Waiting for opponent..."
```

### **Step 3: Connect Player 2 (O)**

Open a **third** terminal window. Run the client script again to start the second client.  
```bash
python client.py  
# Console output: "Connected. Waiting for opponent..."
# Console output: "Match found! You are Player O."
```

### **Step 4: Gameplay**

1. **Player X** will be prompted: Enter row and col (e.g., '1 1'):.  
2. Type two numbers separated by a space (from 0 to 2\) and press Enter.  
3. The server updates the board on both screens.  
4. **Player O** takes their turn.  
5. The connection naturally terminates when a win/draw is achieved.

## **5\. Technical Protocol Details (JSON over TCP)**

We designed a custom application-layer protocol for data exchange usin JSON over TCP:

* **Message Format:** `{"type": <string>, "payload": <data>}`  
* **Handshake Phase:** \* Client sends: `{"type": "CONNECT"}`  
  * Server responds: `{"type": "WELCOME", "payload": "Player X"}`  
* **Gameplay Phase:**  
  * Client sends: `{"type": "MOVE", "row": 1, "col": 1}`  
  * Server broadcasts: `{"type": "UPDATE", "board": [[...], [...], [...]], , "turn": "O", "status": "ongoing"}`


## **6\. Academic Integrity & References**

<span style="color: purple;">***RUBRIC NOTE: List all references used and help you got. Below is an example.***</span>

* **Code Origin:**  
  * The socket boilerplate was adapted from the course tutorial "TCP Echo Server". The core multithreaded game logic, protocol, and state management were written by the group.  
* **GenAI Usage:**  
  * ChatGPT was used to assist in generating the Unicode box-drawing characters for the CLI interface, and to help structure the TCP buffer-splitting logic (`\n delimiter`).  
  * Gemini was used to help in `README.md` writing and polishing.  
  * GitHub Copilot was used to help plan the workflow of the application.   
* **References:**  
  * [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)  
  * [Real Python: Intro to Python Threading](https://realpython.com/intro-to-python-threading/)
