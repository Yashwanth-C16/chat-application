from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

active_connections = {}  # {websocket: username}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[websocket] = username

    # broadcast that someone joined
    for connection in active_connections:
        await connection.send_text(f"{username} joined")

    #new user
    curr_list=[]
    for web_soc,user in active_connections.items():
        if web_soc!=websocket:
            curr_list.append(user)
    await websocket.send_text(f"{", ".join(curr_list)} in the room")

    try:
        while True:
            data = await websocket.receive_text()

            sender_name=active_connections[websocket]
            for web_soc,connection in active_connections.items():
                if web_soc!=websocket:
                    await web_soc.send_text(f"{sender_name}:{data}")

    except WebSocketDisconnect:
        # TODO: remove this connection and broadcast that they left
        left_user=active_connections[websocket]
        del active_connections[websocket]
        for connection in active_connections:
            await connection.send_text(f"{left_user} has left")
        