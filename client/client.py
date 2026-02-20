"""
TCP Chat Client

Connects to the chat server, prompts for a username, and runs two concurrent loops:
- Receive loop (background thread): listen for server messages
- Send loop (main thread): read user input and send to server
"""

import socket
import threading
import sys

# Server connection details
HOST = "127.0.0.1"  # Server address (change to server's IP for remote)
PORT = 5000  # Server port
BUFFER_SIZE = 1024  # Max bytes per recv() call


def receive_messages(sock):
	"""
	Background thread that continuously listens for messages from the server.
	Prints them to stdout as they arrive.
	"""
	while True:
		try:
			data = sock.recv(BUFFER_SIZE)
			if not data:
				# Empty data means server closed the connection
				print("\n[disconnected] Server closed the connection.")
				break
			text = data.decode("utf-8")
			if text:
				print(text, end="", flush=True)  # Flush to show immediately
		except OSError as e:
			# Connection error (server crashed, network issue, etc.)
			if "[Errno 10054]" not in str(e):
				pass  # Suppress duplicate error messages
			break


def start_client():
	"""
	Main client flow:
	1. Connect to server
	2. Prompt for and validate username
	3. Start receive thread
	4. Loop: read user input and send to server
	5. Handle /quit or disconnection
	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((HOST, PORT))
	except OSError:
		print("Unable to connect to the server.")
		return

	try:
		# Phase 1: Username registration
		username = ""
		while not username or len(username) > 20:
			username = input("Enter username (1-20 chars): ").strip()
			if not username:
				print("Username cannot be empty.")
			elif len(username) > 20:
				print("Username too long. Max 20 characters.")
	
		# Send username to server
		sock.sendall((username + "\n").encode("utf-8"))

		# Phase 2: Start background receive thread
		receiver = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
		receiver.start()

		# Phase 3: Main message loop (send user input to server)
		while True:
			message = sys.stdin.readline()  # Block until user types something
			if not message:
				break  # stdin closed (EOF)
			message = message.strip()
			if message == "/quit":
				# User requested to quit
				print("Disconnecting...")
				break
			if message:
				# Send non-empty messages to server
				sock.sendall((message + "\n").encode("utf-8"))

	except KeyboardInterrupt:
		# User pressed Ctrl+C
		pass
	finally:
		# Phase 4: Cleanup
		try:
			sock.close()
		except OSError:
			pass


if __name__ == "__main__":
	start_client()
