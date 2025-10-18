import asyncio
from enum import Enum
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Any
import re

app = FastAPI()


class Player:
    def __init__(self, websocket: WebSocket, name: str):
        self.websocket = websocket
        self.name = name
        self.ready = False

    def ready_up(self):
        self.ready = True


class Action(Enum):
    JOIN = 0
    DISCARD = 1
    CALLOUT = 2


class Cheat:
    def __init__(self):
        self.current_action = Action.JOIN
        self.current_player = 0
        self.players: dict[str, Player] = {}

    def join(self, player: Player):
        self.players[player.name] = player

    @property
    def playing(self):
        return len(self.players) != 0 and all(
            map(lambda p: p.ready, self.players.values())
        )

    async def broadcast(self, message: Any):
        for player in self.players.values():
            await player.websocket.send_json(message)

    async def start(self):
        if not self.playing:
            return
        print("starting")
        while True:
            await asyncio.sleep(1)


cheat = Cheat()


@app.get("/")
async def root():
    return HTMLResponse("<html><body>Hello World</body></html>")


@app.websocket("/cheat")
async def websocket_endpoint(websocket: WebSocket):
    if cheat.playing:
        print("already playing")
        return

    await websocket.accept()

    try:
        # name
        data = await websocket.receive_text()
        name = re.sub(r"\s+", "", data)
        player = Player(websocket, name)
        cheat.join(player)
        await cheat.broadcast({"message": f"Player {name} joined."})

        # ready
        await websocket.receive_text()
        player.ready_up()
        print(f"{player.name} ready")
        await cheat.start()

        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Failed to join cheat")
