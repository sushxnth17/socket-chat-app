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
			print(text, end="")
		except OSError:
			break


def start_client():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((HOST, PORT))
	except OSError:
		print("Unable to connect to the server.")
		return

	try:
		username = input("Enter username: ").strip()
		if not username:
			return
		sock.sendall((username + "\n").encode("utf-8"))

		receiver = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
		receiver.start()

		while True:
			message = sys.stdin.readline()
			if not message:
				break
			sock.sendall(message.encode("utf-8"))
	except KeyboardInterrupt:
		pass
	finally:
		try:
			sock.close()
		except OSError:
			pass


if __name__ == "__main__":
	start_client()
