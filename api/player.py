from starlette.websockets import WebSocket

from api.card import Card


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
