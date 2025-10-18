from enum import Enum
from typing import Any


class Suit(Enum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"


class Card:
    def __init__(self, suit: Suit, value: int) -> None:
        self.suit = suit
        self.value = value

    @staticmethod
    def from_str(s: str) -> "Card":
        suit = Suit(s[0].upper())
        value = int(s[1:])
        return Card(suit, value)

    def __str__(self) -> str:
        return f"{self.suit.value}{self.value}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


def generate_deck() -> list[Card]:
    return [Card(suit, value) for suit in Suit for value in range(1, 14)]
