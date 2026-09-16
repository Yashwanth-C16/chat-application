from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

active_connections = {}  # {websocket: username}

@app.get("/")
def root():
    return {"message":"server open"}


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
   
    await websocket.accept()
    is_taken=False
    for value in active_connections.values():
        if value==username:
            is_taken=True
            break

    if is_taken:
        await websocket.close(code=4000,reason="Username already taken,choose different Username")
        return
    
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
        left_user=active_connections.get(websocket)
        if left_user is None:
            return
        
        del active_connections[websocket]
        for connection in active_connections:
            await connection.send_text(f"{left_user} has left")

        