from abc import ABC, abstractmethod
from api.card import Card
from api.player import Player


class Action(ABC):
    @abstractmethod
    def __repr__(self) -> str:
        pass


class Pass(Action):
    def __init__(self, player: Player) -> None:
        self.player = player

    def __repr__(self) -> str:
        return f"{self.player.name} passed."


class Discard(Action):
    def __init__(self, player: Player, cards: list[Card], claimed_rank: int) -> None:
        self.player = player
        self.cards = cards
        self.claimed_rank = claimed_rank

    def __repr__(self) -> str:
        return f"{self.player.name} discarded {len(self.cards)} '{self.claimed_rank}'s."


class CallBluff(Action):
    def __init__(self, caller: Player, callee: Player, correct: bool) -> None:
        self.caller = caller
        self.callee = callee
        self.correct = correct

    def __repr__(self) -> str:
        return f"{self.caller.name} {"correctly" if self.correct else "incorrectly"} called {self.callee.name}'s bluff."
