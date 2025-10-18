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
        self.playing = False
        self.current_action = Action.JOIN
        self.current_player_index = 0
        self.players: dict[str, Player] = {}

    def join(self, player: Player):
        self.players[player.name] = player

    @property
    def all_ready(self):
        return len(self.players) != 0 and all(
            map(lambda p: p.ready, self.players.values())
        )

    async def broadcast(self, message: Any):
        for player in self.players.values():
            await player.websocket.send_json(message)

    @property
    def current_player(self):
        players = list(self.players.values())
        return players[self.current_player_index]

    def increment_player(self):
        self.current_player_index += 1

    async def start(self):
        if not self.all_ready:
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
    if cheat.all_ready:
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
            await asyncio.sleep(0.5)
            if cheat.playing:
                print(f"sending {player.name} the game data")
    except WebSocketDisconnect:
        print("Failed to join cheat")
