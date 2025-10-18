import asyncio
import random
from typing import Any

from api.card import generate_deck
from api.player import Player, HumanPlayer, BotPlayer


class Cheat:
    def __init__(self):
        self.playing = False
        self.current_player_index = 0
        self.players: list[Player] = []

    @property
    def human_players(self) -> list[HumanPlayer]:
        return list(
            filter(lambda player: isinstance(player, HumanPlayer), self.players)
        )

    def join(self, player: Player):
        self.players.append(player)

    @property
    def all_ready(self):
        return len(self.players) != 0 and all(map(lambda p: p.ready, self.players))

    async def broadcast(self, message: Any):
        for player in self.human_players:
            await player.websocket.send_json(message)

    @property
    def current_player(self):
        players = self.players
        return players[self.current_player_index]

    def increment_player(self):
        self.current_player_index += 1

    def pov_data(self, player: Player):
        return {
            "name": player.name,
            "hand": player.hand,
            "players": {
                p.name: len(p.hand)
                for p in list(filter(lambda _p: _p.name != player.name, self.players))
            },
        }

    async def start(self):
        if not self.all_ready:
            return
        print("starting")

        # add bot
        self.players.append(BotPlayer())

        # create hands
        deck = generate_deck()
        random.shuffle(deck)
        hand_size = len(deck) // len(self.players)
        for player in self.players:
            for i in range(hand_size):
                player.hand.append(deck.pop())

        self.playing = True

        for player in self.players:
            print(player.name, self.pov_data(player))

        while True:
            await asyncio.sleep(1)
