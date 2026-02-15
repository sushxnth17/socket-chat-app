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


def handle_client(conn, addr):
	try:
		conn.sendall(b"Enter username: ")
		username = ""
		while not username:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				return
			username = data.decode("utf-8").strip()

		with clients_lock:
			clients[conn] = username

		broadcast(f"[join] {username} has joined the chat.\n")
		conn.sendall(b"Connected. Start typing messages.\n")

		while True:
			data = conn.recv(BUFFER_SIZE)
			if not data:
				break
			text = data.decode("utf-8").strip()
			if not text:
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
	server.bind((HOST, PORT))
	server.listen()

	print(f"Server listening on {HOST}:{PORT}")
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
