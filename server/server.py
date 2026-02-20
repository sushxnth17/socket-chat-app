"""
TCP Chat Server

Listens for incoming client connections, manages usernames, broadcasts messages
to all connected clients, and handles special commands (/help, /users, /dm, /quit).
"""

import socket
import threading

# Server configuration
HOST = "0.0.0.0"  # Listen on all interfaces (change to "127.0.0.1" for local-only)
PORT = 5000  # TCP port
BUFFER_SIZE = 1024  # Max bytes per recv() call

# Global state: maps socket connection to username
clients = {}
clients_lock = threading.Lock()  # Protect clients dict from race conditions


def broadcast(message, exclude_conn=None):
	"""Send a message to all connected clients except optionally one."""
	data = message.encode("utf-8")
	with clients_lock:
		for conn in list(clients.keys()):
			if conn is exclude_conn:
				continue  # Skip the sender
			try:
				conn.sendall(data)
			except OSError:
				pass  # Client may have disconnected


def send_to_client(conn, message):
	"""Send a message to a single client."""
	try:
		conn.sendall(message.encode("utf-8"))
	except OSError:
		pass  # Client may have disconnected


def is_username_taken(username, exclude_conn=None):
	"""Check if a username is already in use (case-insensitive)."""
	with clients_lock:
		for c, u in clients.items():
			if c is not exclude_conn and u.lower() == username.lower():
				return True
	return False


def handle_command(conn, username, text):
	"""
	Process commands starting with /.
	Returns: True if command handled, False if user requested /quit, None if unknown command.
	"""
	parts = text.split(maxsplit=2)
	cmd = parts[0].lower()

	if cmd == "/help":
		# Show available commands
		help_text = (
			"\n=== Commands ===\n"
			"/help - Show this help\n"
			"/users - List online users\n"
			"/dm <user> <msg> - Send direct message\n"
			"/quit - Disconnect\n\n"
		)
		send_to_client(conn, help_text)
		return True

	elif cmd == "/users":
		# List all online users
		with clients_lock:
			users = list(clients.values())
		users_text = f"\n=== Online Users ({len(users)}) ===\n" + "\n".join(users) + "\n\n"
		send_to_client(conn, users_text)
		return True

	elif cmd == "/dm":
		# Send a direct message to one user
		if len(parts) < 3:
			send_to_client(conn, "Usage: /dm <username> <message>\n")
			return True
		target_user = parts[1]
		message = " ".join(parts[2:])  # Support multi-word messages
		with clients_lock:
			target_conn = None
			for c, u in clients.items():
				if u.lower() == target_user.lower():
					target_conn = c
					break
		if target_conn:
			send_to_client(target_conn, f"[DM from {username}] {message}\n")
			send_to_client(conn, f"[DM to {target_user}] {message}\n")
		else:
			send_to_client(conn, f"No user named '{target_user}'. Use /users to see online users.\n")
		return True

	elif cmd == "/quit":
		# Disconnect the user
		send_to_client(conn, "Disconnecting...\n")
		return False

	return None  # Unknown command


def handle_client(conn, addr):
	"""
	Handle a single client connection. Runs in its own thread.
	1. Get and validate username
	2. Announce join
	3. Loop: receive messages and process/broadcast
	4. On disconnect: announce leave
	"""
	try:
		# Phase 1: Username registration
		username = ""
		while not username:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				return  # Client closed without sending username
			username = data.decode("utf-8").strip()

			# Validate username
			if not username or len(username) > 20:
				send_to_client(conn, "[error] Username must be 1-20 characters.\n")
				username = ""
				continue

			if is_username_taken(username):
				send_to_client(conn, "[error] Username already taken. Try another.\n")
				username = ""
				continue

		# Phase 2: Register user and announce join
		with clients_lock:
			clients[conn] = username

		broadcast(f"[join] {username} has joined the chat.\n")
		conn.sendall(b"\n=== Connected! Type /help for commands ===\n\n")

		# Phase 3: Message loop
		while True:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				break  # Client disconnected
			text = data.decode("utf-8").strip()
			if not text:
				continue  # Ignore empty messages

			# Check for commands
			if text.startswith("/"):
				result = handle_command(conn, username, text)
				if result is False:
					break  # User requested /quit
				elif result is True:
					continue  # Command handled, get next input
				# else: unknown command, treat as message

			# Broadcast to other clients
			broadcast(f"{username}: {text}\n", exclude_conn=conn)

	except ConnectionError:
		pass  # Client forcibly disconnected
	finally:
		# Phase 4: Cleanup and announce leave
		with clients_lock:
			username = clients.pop(conn, None)
		if username:
			broadcast(f"[leave] {username} has left the chat.\n")
		try:
			conn.close()
		except OSError:
			pass


def start_server():
	"""Create a TCP server socket and accept incoming connections."""
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse port after restart
	try:
		server.bind((HOST, PORT))
		server.listen()  # Allow queued connections
	except OSError as exc:
		print(f"Server failed to start: {exc}", flush=True)
		server.close()
		return

	print(f"Server listening on {HOST}:{PORT}", flush=True)
	try:
		while True:
			conn, addr = server.accept()  # Block until client connects
			# Spawn a thread to handle this client (daemon threads exit when main exits)
			thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
			thread.start()
	except KeyboardInterrupt:
		print("\nShutting down server.")
	finally:
		server.close()


if __name__ == "__main__":
	start_server()
