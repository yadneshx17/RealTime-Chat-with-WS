import json
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
    Header,
    Body
    ) 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from backend.app.core.oauth import get_current_user
from .models import models
from .db.db import get_async_db, engine, Base
from .routes import auth
import random

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
            var client_id = Math.floor(Math.random() * 10000);
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    # async def connect(self, websocket: WebSocket, user_id: int):
    #     await websocket.accept()
    #     self.active_connections[user_id] = websocket
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket): # user_id: int
        """
        If a client disconnects unexpectedly, self.active_connections.remove(websocket) may cause an error if the connection is already removed.
        if websocket in self.activek_connections:
        """
        # self.active_connections.pop(user_id, None)
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections: # .values()
            await connection.send_text(message)

manager = ConnectionManager()    

# @app.get("/")
# async def root(db: AsyncSession = Depends(get_async_db)):
#     return {"message": " Hello"}

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
    """get_async_db() returns an AsyncGenerator, so you cannot use await get_async_db()"""
    # async with get_async_db() as db:
    #     user = await get_current_user(websocket, db)

    # await manager.connect(websocket, user.id)
    await manager.connect(websocket)
    try: 
        while True:
            data = await websocket.receive_text()
            # await manager.broadcast(f"User #{user.id} says: {data}")
            await manager.broadcast(f"Use says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"User #{user.id} has left the chat")
        await manager.broadcast(f"User #{client_id} has left the chat")


@app.get("/items")
async def read_items(
    cookie_id: str | None = Cookie(None),
    accept_encoding: str | None = Header(None)
):
    return {"cookie": cookie_id, "accept_encoding": accept_encoding}

@app.post("/createposts")
def create_posts(payload: dict = Body()): #  designed to extract data from the body of a POST request in a FastAPI application.
    """ Body of the Request
    {
        "title": "Top Cities,,
        "content": "Delhi"
    }
    """

    print(payload)

    return {"new_post": f"title {payload['title']} ',' content:{payload['content']}"} # send it back to the user