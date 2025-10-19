import asyncio
from api.player import Player
from api.card import Card
from api.gemini import move, move_or_callout, analyze_bluff


class BotPlayer(Player):
    def __init__(self) -> None:
        super().__init__("otis")
        self.pov_board_state = None

    async def play_turn(self) -> list[Card]:
        response = move(self.pov_board_state)
        print(response)
        return [Card.from_str(c) for c in response.get("CardsToPlay")]

    async def play_turn_or_callout(self) -> list[Card] | Player:
        response = move_or_callout(self.pov_board_state, "pretty neutral")
        print(response.get("reasoning"))
        if response.get("call_bluff"):
            return self
        else:
            return [Card.from_str(c) for c in response.get("cards_to_play")]

    async def callout(self) -> Player:
        response = analyze_bluff(self.pov_board_state, "pretty neutral")
        print(response.get("Reasoning"))
        if response.get("Bluffing"):
            return self
        while True:
            await asyncio.sleep(1)

    async def update_pov(self, pov) -> None:
        self.pov_board_state = pov
