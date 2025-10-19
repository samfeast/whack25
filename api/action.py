from abc import ABC, abstractmethod
from api.card import Card, Rank
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
    def __init__(self, player: Player, cards: list[Card], claimed_rank: Rank) -> None:
        self.player = player
        self.cards = cards
        self.claimed_rank = claimed_rank

    def __repr__(self) -> str:
        return f"{self.player.name} discarded {len(self.cards)} '{repr(self.claimed_rank)}'s."

    def is_valid(self) -> bool:
        return all(self.claimed_rank == card.rank for card in self.cards)


class CallBluff(Action):
    def __init__(self, caller: Player, callee: Player, correct: bool) -> None:
        self.caller = caller
        self.callee = callee
        self.correct = correct

    def __repr__(self) -> str:
        return f"{self.caller.name} {"correctly" if self.correct else "incorrectly"} called {self.callee.name}'s bluff."
