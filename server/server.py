import socket
import threading


HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024

clients = {}
clients_lock = threading.Lock()


def broadcast(message, exclude_conn=None):
	data = message.encode("utf-8")
	with clients_lock:
		for conn in list(clients.keys()):
			if conn is exclude_conn:
				continue
			try:
				conn.sendall(data)
			except OSError:
				pass


def send_to_client(conn, message):
	try:
		conn.sendall(message.encode("utf-8"))
	except OSError:
		pass


def is_username_taken(username, exclude_conn=None):
	with clients_lock:
		for c, u in clients.items():
			if c is not exclude_conn and u.lower() == username.lower():
				return True
	return False


def handle_command(conn, username, text):
	parts = text.split(maxsplit=2)
	cmd = parts[0].lower()

	if cmd == "/help":
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
		with clients_lock:
			users = list(clients.values())
		users_text = f"\n=== Online Users ({len(users)}) ===\n" + "\n".join(users) + "\n\n"
		send_to_client(conn, users_text)
		return True

	elif cmd == "/dm":
		if len(parts) < 3:
			send_to_client(conn, "Usage: /dm <username> <message>\n")
			return True
		target_user = parts[1]
		message = " ".join(parts[2:])
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
		send_to_client(conn, "Disconnecting...\n")
		return False

	return None


def handle_client(conn, addr):
	try:
		username = ""
		while not username:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				return
			username = data.decode("utf-8").strip()

			if not username or len(username) > 20:
				send_to_client(conn, "[error] Username must be 1-20 characters.\n")
				username = ""
				continue

			if is_username_taken(username):
				send_to_client(conn, "[error] Username already taken. Try another.\n")
				username = ""
				continue

		with clients_lock:
			clients[conn] = username

		broadcast(f"[join] {username} has joined the chat.\n")
		conn.sendall(b"\n=== Connected! Type /help for commands ===\n\n")

		while True:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				break
			text = data.decode("utf-8").strip()
			if not text:
				continue

			if text.startswith("/"):
				result = handle_command(conn, username, text)
				if result is False:
					break
				elif result is True:
					continue

			broadcast(f"{username}: {text}\n", exclude_conn=conn)
	except ConnectionError:
		pass
	finally:
		with clients_lock:
			username = clients.pop(conn, None)
		if username:
			broadcast(f"[leave] {username} has left the chat.\n")
		try:
			conn.close()
		except OSError:
			pass


def start_server():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		server.bind((HOST, PORT))
		server.listen()
	except OSError as exc:
		print(f"Server failed to start: {exc}", flush=True)
		server.close()
		return

	print(f"Server listening on {HOST}:{PORT}", flush=True)
	try:
		while True:
			conn, addr = server.accept()
			thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
			thread.start()
	except KeyboardInterrupt:
		print("\nShutting down server.")
	finally:
		server.close()


if __name__ == "__main__":
	start_server()
