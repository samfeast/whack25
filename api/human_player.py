from starlette.websockets import WebSocket
from api.player import Player
from api.card import Card


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
