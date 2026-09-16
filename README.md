# 💬 Real-Time Chat (FastAPI + WebSockets)

A real-time group chat application built with FastAPI's native WebSocket support — demonstrates persistent, bidirectional client-server communication as an alternative to the traditional request-response HTTP model.

**Live demo:** [Add your deployment link here]

---

## What it does

- Multiple users can join a shared chat room using just a username (no signup required).
- Messages are broadcast instantly to all connected users, with correct sender attribution.
- New joiners immediately see who else is already in the room.
- Join/leave events are broadcast live to everyone connected.
- Duplicate usernames are rejected with a clear, user-facing message.

## Why I built it

All my previous projects (Django, FastAPI CRUD apps, even StudyBuddy's chat) use the standard request-response model — the client asks, the server answers, done. I wanted to understand and build something fundamentally different: a system where the server can push data to clients without them asking first, which is how real-time features (live chat, notifications, live dashboards) actually work under the hood.

## Tech stack

| Layer | Tool |
|---|---|
| Backend | FastAPI (native WebSocket support) |
| Server | Uvicorn (ASGI) |
| Frontend | Vanilla HTML/CSS/JavaScript (no framework) |

## Architecture

```
Client connects → ws://server/ws/{username}
   → Backend checks username isn't already taken
   → If taken: reject with a clear reason, connection never fully opens
   → If available: accept connection, store {websocket: username} in memory

On message sent:
   → Server looks up sender's username
   → Broadcasts to all OTHER connected clients (loop + send_text)

On disconnect:
   → Server removes the connection from memory
   → Broadcasts "X has left" to remaining connected clients
```

## Key engineering decisions

- **In-memory connection tracking** — a dictionary (`{websocket: username}`) tracks all active connections. Using the connection object itself as the key made disconnect handling straightforward: FastAPI gives you the `websocket` object on disconnect, so the username lookup is a direct dictionary access rather than a search.
- **Duplicate username handling required understanding WebSocket lifecycle precisely** — closing a connection *before* it's been accepted causes an abrupt HTTP-level rejection (403) rather than a clean WebSocket close. The fix was to accept the connection first, then immediately check and close with a proper reason code if the username was taken — giving the client a clear, actionable error instead of a raw connection failure.
- **Async throughout** — every send/receive operation is awaited, so one slow client (e.g. a laggy connection) doesn't block the server from handling other connected users concurrently.
- **Defensive lookups** — disconnect handling uses `.get()` instead of direct dictionary indexing, to avoid a `KeyError` if a connection drops before it was fully registered.

## Known limitations

- Single shared room only — no support for multiple rooms or private (1-to-1) messaging yet.
- No message persistence — chat history is lost if the server restarts or a user refreshes.
- No authentication — usernames are self-reported and not verified.

## Running locally

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install fastapi uvicorn websockets
uvicorn main:app --reload
```

Then open `index.html` directly in your browser (open it in two tabs to test with multiple users). Make sure the server URL field matches your running server's address and port.

## Future improvements

- Multiple chat rooms
- Private (1-to-1) messaging
- Message persistence (store chat history in a database)
- User authentication