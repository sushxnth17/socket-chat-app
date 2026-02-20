# Socket Chat Application

A **terminal-based multi-client chat app** built with Python sockets. Connect multiple users over TCP, broadcast messages, send direct messages, and manage the session with simple commands.

## Features

✅ **Multi-client support** – Handle many users at once with threads  
✅ **Broadcast messaging** – Send messages to all connected users  
✅ **Direct messaging (DM)** – Send private 1-to-1 messages  
✅ **User commands** – `/help`, `/users`, `/dm`, `/quit`  
✅ **Username validation** – Prevent duplicates, enforce length limits  
✅ **Join/leave notifications** – Track who enters and leaves  
✅ **Clean shutdown** – Graceful disconnect handling  

## How It Works

**Server (`server/server.py`)**
- Listens on `127.0.0.1:5000` (or `0.0.0.0:5000` for remote access)
- Accepts incoming TCP connections in a loop
- Spawns a thread per client to handle messages concurrently
- Maintains a shared dictionary of active users
- Broadcasts or routes messages based on commands

**Client (`client/client.py`)**
- Connects to the server
- Prompts for a username (1-20 chars, no duplicates)
- Starts a receive thread to listen for incoming messages
- Main thread reads user input (messages and commands)
- Sends messages to the server

**Communication Flow**
```
Client A                    Server                    Client B
   |                          |                          |
   |-- connect() ----------->  |                          |
   |                          |<------------ connect() ---|
   |                          |                          |
   |-- username "alice" ----->  (stores alice)           |
   |                          |-- announce join -------->  |
   |                          |-- announce join ------->  (to A)
   |                          |                          |
   |-- "hi everyone" -------->  |-- broadcast ---------->  |
   |                          |-- broadcast ---------->  (A doesn't see own)
   |                          |                          |
   |-- /dm bob "hey" -------->  |-- route to bob ------->  |
   |                          |                          |
   |-- /quit ------------->  (disconnect)                |
   |                          |-- announce leave ----->  (to others)
   (close)                   (close)
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- No external packages (standard library only)

### Clone & Run

```bash
# Clone the repository
git clone https://github.com/sushxnth17/socket-chat-app.git
cd socket-chat-app

# Terminal 1: Start the server
python server/server.py

# Terminal 2+: Start one or more clients
python client/client.py
```

You should see:
```
Server: Server listening on 0.0.0.0:5000
Client: Enter username (1-20 chars):
```

## Commands

### Server-side (automatic)
- **Join announcement** – `[join] <username> has joined the chat.`
- **Leave announcement** – `[leave] <username> has left the chat.`

### Client-side (type these)
| Command | Usage | Example |
|---------|-------|---------|
| `/help` | Show available commands | `/help` |
| `/users` | List all online users | `/users` |
| `/dm <user> <msg>` | Send a private message | `/dm alice hello there` |
| `/quit` | Disconnect gracefully | `/quit` |

## Usage Example

**Terminal 1 (Server):**
```
$ python server/server.py
Server listening on 0.0.0.0:5000
```

**Terminal 2 (Client A):**
```
$ python client/client.py
Enter username (1-20 chars): alice
[join] alice has joined the chat.
Connected! Type /help for commands

/users
=== Online Users (1) ===
alice

hello everyone!
```

**Terminal 3 (Client B):**
```
$ python client/client.py
Enter username (1-20 chars): bob
[join] bob has joined the chat.
Connected! Type /help for commands

alice: hello everyone!

/dm alice hi alice! welcome
[DM to alice] hi alice! welcome
```

**Terminal 2 (Client A receives):**
```
[join] bob has joined the chat.
[DM from bob] hi alice! welcome
```

## Architecture

```
socket-chat-app/
├── server/
│   └── server.py          # Server: accepts clients, handles commands, broadcasts
├── client/
│   └── client.py          # Client: connects, send/receive threads
├── README.md              # This file
├── requirements.txt       # No external dependencies
└── .gitignore             # Ignore __pycache__, .venv, etc.
```

## Code Overview

### `server.py` Key Functions
- **`broadcast(message, exclude_conn)`** – Send message to all except sender
- **`send_to_client(conn, message)`** – Send to a single client
- **`is_username_taken(username)`** – Check for duplicate usernames
- **`handle_command(conn, username, text)`** – Process `/help`, `/users`, `/dm`, `/quit`
- **`handle_client(conn, addr)`** – Per-client thread routine

### `client.py` Key Functions
- **`receive_messages(sock)`** – Background thread listening for server messages
- **`start_client()`** – Main flow: connect, prompt username, input loop

## Remote Access

To run on different machines (LAN or WAN):

1. **Server machine**: Edit `server.py`
   ```python
   HOST = "0.0.0.0"  # Listen on all interfaces
   PORT = 5000
   ```

2. **Client machine**: Edit `client.py`
   ```python
   HOST = "192.168.1.10"  # Server's IP (or hostname)
   PORT = 5000
   ```

3. **Firewall**: Allow inbound TCP on port 5000 if needed

**For Internet access (different networks)**, use a tunneling service like **ngrok**:
```bash
# On server machine
ngrok tcp 5000

# Copy the forwarding address (e.g., 0.tcp.ngrok.io:12345)
# On client, set HOST = "0.tcp.ngrok.io" and PORT = 12345
```

## Testing & Edge Cases

- **Duplicate usernames** – Rejected; user prompted to try another
- **Long usernames** – Limited to 20 chars
- **Empty messages** – Ignored
- **Simultaneous sends** – Thread-safe with locks
- **Client disconnect** – Server announces leave; others stay connected
- **Server shutdown (Ctrl+C)** – Closes gracefully

## Limitations & Future Enhancements

**Current limitations:**
- Single-server (no clustering)
- No persistence/logging
- No encryption (plain TCP)
- No user authentication
- Fixed 1024-byte buffer

**Potential improvements:**
- Add chat rooms/channels
- Implement message history
- Use SSL/TLS for encryption
- Add user login/password system
- Increase buffer size or streaming
- Add a GUI (tkinter/PyQt)
- Use asyncio instead of threading

## Learning Outcomes

This project teaches:
- **TCP socket programming** with `socket` module
- **Concurrent programming** with `threading`
- **Thread safety** with locks and shared state
- **Protocol design** (simple text-based messages)
- **Error handling** for network operations
- **User input validation** and sanitization

## License

Open source—feel free to use, modify, and share!

---

Built with ❤️ as a hands-on socket programming exercise.
