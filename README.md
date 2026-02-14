# Socket Chat Application

Terminal-based multi-client chat app built with Python sockets.

## Goals
- Learn TCP socket programming and concurrency.
- Build a reliable chat server that handles multiple clients.
- Add basic commands and clean disconnects.

## Planned Features
- Multi-client broadcast chat
- Username selection
- Commands: /help, /quit, /users
- Join/leave notifications
- Basic input prompt formatting

## How It Works (Planned)
- The server accepts multiple TCP clients and broadcasts messages.
- Each client runs separate send/receive loops for smooth interaction.
- Usernames are registered on connect; join/leave events are announced.
- Simple commands control the session (help, users, quit).

## Project Structure
- server/: TCP server entry point and server logic
- client/: TCP client entry point and client logic

## Run (future)
Server: python server/server.py
Client: python client/client.py
