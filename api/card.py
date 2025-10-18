from enum import Enum


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


def generate_deck() -> list[Card]:
    return [Card(suit, value) for suit in Suit for value in range(1, 14)]
