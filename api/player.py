from abc import ABC, abstractmethod
from api.card import Card


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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.name == other.name
