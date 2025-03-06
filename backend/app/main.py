from typing import Annotated
from fastapi import (
    FastAPI, 
    WebSocket, 
    Depends, 
    status,
    WebSocketDisconnect,
    WebSocketException,
    Cookie,
    Query,
    Request
    ) 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .models import models
from .db.db import get_async_db, engine, Base
from .routers import auth


# template = Jinja2Templates(directory=)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    lifespan=lifespan
)

app.include_router(auth.router)


# @app.get("/")
# async def root(db: AsyncSession = Depends(get_async_db)):
#     return {"message": " Hello"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, webscoket: WebSocket):
        await webscoket.accept()
        self.active_connections.append(webscoket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()    

@app.get("/")
async def get():
    return HTMLResponse(html)

async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token

# @app.websocket("/items/{item_id}/ws")
# async def websocket_endpoint(
#     *,
#     websocket: WebSocket,
#     item_id: str,
#     q: int | None = None,
#     cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
# ):
    # await websocket.accept()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(
    #         f"Session cookie or query token value is: {cookie_or_token}"
    #     )
    #     if q is not None:
    #         await websocket.send_text(f"Query parameter q is: {q}")
    #     await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You Wrote: {data}", websocket) // return ours message back to us, we do not need this as broadcast already send the message to us and the another user.
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} has left the chat")