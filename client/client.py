import socket
import threading
import sys


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


def receive_messages(sock):
	while True:
		try:
			data = sock.recv(BUFFER_SIZE)
			if not data:
				print("\n[disconnected] Server closed the connection.")
				break
			text = data.decode("utf-8")
			if text:
				print(text, end="", flush=True)
		except OSError as e:
			if "[Errno 10054]" not in str(e):
				pass
			break


def start_client():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((HOST, PORT))
	except OSError:
		print("Unable to connect to the server.")
		return

	try:
		username = ""
		while not username or len(username) > 20:
			username = input("Enter username (1-20 chars): ").strip()
			if not username:
				print("Username cannot be empty.")
			elif len(username) > 20:
				print("Username too long. Max 20 characters.")
	
		sock.sendall((username + "\n").encode("utf-8"))

		receiver = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
		receiver.start()

		while True:
			message = sys.stdin.readline()
			if not message:
				break
			message = message.strip()
			if message == "/quit":
				print("Disconnecting...")
				break
			if message:
				sock.sendall((message + "\n").encode("utf-8"))
	except KeyboardInterrupt:
		pass
	finally:
		try:
			sock.close()
		except OSError:
			pass


if __name__ == "__main__":
	start_client()
