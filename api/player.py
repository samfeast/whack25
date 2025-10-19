import asyncio
from abc import ABC, abstractmethod
from typing import Any, Coroutine

from starlette.websockets import WebSocket

from api.card import Card

from gemini import analyze_bluff, move


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []
        self.last_discard = []
        self.cheated = False

    @abstractmethod
    async def play_turn(self) -> list[Card]:
        pass

    @abstractmethod
    async def play_turn_or_callout(self) -> "list[Card] | Player":
        pass

    @abstractmethod
    async def callout(self) -> "Player":
        pass


class HumanPlayer(Player):
    def __init__(self, websocket: WebSocket, name: str) -> None:
        super().__init__(name)
        self.websocket = websocket
        self.ready = False

    def ready_up(self) -> None:
        self.ready = True

    async def play_turn(self) -> list[Card]:
        while True:
            try:
                data = await self.websocket.receive_json()
                if "discard" in data:
                    discard: list[str] = data.get("discard")
                    self.last_discard = [Card.from_str(s) for s in discard]
                    return self.last_discard
            except Exception as e:
                print(e, f"try again, {self.name}")

    @abstractmethod
    async def play_turn_or_callout(self) -> list[Card] | Player:
        while True:
            try:
                data = await self.websocket.receive_json()
                if "discard" in data:
                    discard: list[str] = data.get("discard")
                    self.last_discard = [Card.from_str(s) for s in discard]
                    return self.last_discard
                elif "callout" in data:
                    callout: bool = data.get("callout")
                    if callout:
                        return self
            except Exception as e:
                print(e, f"try again, {self.name}")

    async def callout(self) -> Player:
        while True:
            try:
                data = await self.websocket.receive_json()
                if "callout" in data:
                    callout: bool = data.get("callout")
                    if callout:
                        return self
            except Exception as e:
                print(e, f"try again, {self.name}")


class BotPlayer(Player):
    def __init__(self) -> None:
        super().__init__("otis")

    async def play_turn(self) -> list[Card]:
        move()

    async def play_turn_or_callout(self) -> list[Card] | Player:
        pass

    async def callout(self) -> bool:
        while True:
            await asyncio.sleep(1)
