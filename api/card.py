from enum import Enum
from typing import Any


class Suit(Enum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"


class Rank:
    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Rank must be int")

        if value < 1 or value > 13:
            raise ValueError("Rank must be between 1 and 13")

        self.value = value

    def __int__(self) -> int:
        return self.value

    def __lt__(self, other):
        return self.value < int(other)

    def __gt__(self, other):
        return self.value > int(other)

    def __eq__(self, other):
        return self.value == int(other)

    def __repr__(self) -> str:
        return str(self.value)

    def increment(self) -> None:
        if self.value == 13:
            self.value = 1
        else:
            self.value += 1

    def decrement(self) -> None:
        if self.value == 1:
            self.value = 13
        else:
            self.value -= 1

    @staticmethod
    def range():
        for i in range(1, 14):
            yield Rank(i)


class Card:
    def __init__(self, suit: Suit, rank: Rank) -> None:
        self.suit = suit
        self.rank = rank

    @staticmethod
    def create_deck() -> list["Card"]:
        return [Card(suit, rank) for suit in Suit for rank in Rank.range()]

    @staticmethod
    def from_str(s: str) -> "Card":
        suit = Suit(s[0].upper())
        rank = Rank(int(s[1:]))
        return Card(suit, rank)

    def __str__(self) -> str:
        return f"{self.suit.value}{self.rank}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))
