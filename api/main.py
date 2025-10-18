import asyncio
import random
from enum import Enum
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Any
import re

app = FastAPI()


class Suit(Enum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"


class Card:
    def __init__(self, suit: Suit, value: int) -> None:
        self.suit = suit
        self.value = value

    def __str__(self) -> str:
        return f"{self.suit.value}{self.value}"

    def __repr__(self) -> str:
        return f"{self.suit.value}{self.value}"


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []


class HumanPlayer(Player):
    def __init__(self, websocket: WebSocket, name: str) -> None:
        super().__init__(name)
        self.websocket = websocket
        self.ready = False

    def ready_up(self) -> None:
        self.ready = True


class BotPlayer(Player):
    def __init__(self) -> None:
        super().__init__("otis")


class Action(Enum):
    JOIN = 0
    DISCARD = 1
    CALLOUT = 2


def generate_deck() -> list[Card]:
    return [Card(suit, value) for suit in Suit for value in range(1, 14)]


class Cheat:
    def __init__(self):
        self.playing = False
        self.current_action = Action.JOIN
        self.current_player_index = 0
        self.players: list[Player] = []

    @property
    def human_players(self) -> list[HumanPlayer]:
        return list(
            filter(lambda player: isinstance(player, HumanPlayer), self.players)
        )

    def join(self, player: Player):
        self.players.append(player)

    @property
    def all_ready(self):
        return len(self.players) != 0 and all(map(lambda p: p.ready, self.players))

    async def broadcast(self, message: Any):
        for player in self.human_players:
            await player.websocket.send_json(message)

    @property
    def current_player(self):
        players = self.players
        return players[self.current_player_index]

    def increment_player(self):
        self.current_player_index += 1

    async def start(self):
        if not self.all_ready:
            return
        print("starting")

        # add bot
        self.players.append(BotPlayer())

        # create hands
        deck = generate_deck()
        random.shuffle(deck)
        hand_size = len(deck) // len(self.players)
        for player in self.players:
            for i in range(hand_size):
                player.hand.append(deck.pop())

        self.playing = True

        for player in self.players:
            print(player.name, player.hand)

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
        player = HumanPlayer(websocket, name)
        cheat.join(player)
        await cheat.broadcast({"message": f"Player {name} joined."})

        # ready
        await websocket.receive_text()
        player.ready_up()
        print(f"{player.name} ready")
        asyncio.create_task(cheat.start())

        while True:
            await asyncio.sleep(1)
            if cheat.playing:
                print(f"sending {player.name} the game data")
    except WebSocketDisconnect:
        print("Failed to join cheat")
