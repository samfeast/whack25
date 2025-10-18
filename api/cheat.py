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
        self.deck = generate_deck()
        self.current_value = 1

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

    @property
    def previous_player_index(self) -> int:
        return self.current_player_index - 1 % len(self.players)

    @property
    def previous_player(self) -> Player:
        return self.players[self.previous_player_index]

    @property
    def current_other_players(self) -> list[Player]:
        return list(filter(lambda p: p.name != self.current_player.name, self.players))

    def increment_player(self):
        self.current_player_index += 1
        self.current_player_index %= len(self.players)

    def increment_current_value(self):
        if self.current_value == 13:
            self.current_value = 1
        else:
            self.current_value += 1

    def pov_data(self, player: Player):
        return {
            "name": player.name,
            "hand": player.hand,
            "players": {
                p.name: {"hand": len(p.hand), "last_discard": len(p.last_discard)}
                for p in list(filter(lambda _p: _p.name != player.name, self.players))
            },
            "waiting_for": self.current_player.name,
            "previous_turn": None,
        }

    async def start(self):
        if not self.all_ready:
            return
        print("starting")

        # add bot
        self.players.append(BotPlayer())

        # create hands
        random.shuffle(self.deck)
        hand_size = len(self.deck) // len(self.players)
        for player in self.players:
            for i in range(hand_size):
                player.hand.append(self.deck.pop())

        self.playing = True

        # print player povs
        for player in self.players:
            print(player.name, self.pov_data(player))

        # await player discard
        discard_list = await self.current_player.play_turn()
        self.current_player.hand = list(
            set(self.current_player.hand) - set(discard_list)
        )
        print(f"{self.current_player.name} discarded {len(discard_list)} cards")
        self.deck += discard_list
        self.current_player.cheated = False
        for card in discard_list:
            if card.value != self.current_value:
                self.current_player.cheated = True
                break
        self.increment_current_value()

        # print player povs
        for player in self.players:
            print(player.name, self.pov_data(player))

        # next player
        self.increment_player()

        while True:
            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(self.current_player.play_turn()),
                ]
                + [
                    asyncio.create_task(p.callout()) for p in self.current_other_players
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            finished = done.pop()
            result = await finished

            if finished is self.current_player.play_turn:
                discard_list = result
                self.current_player.hand = list(
                    set(self.current_player.hand) - set(discard_list)
                )
                print(f"{self.current_player.name} discarded {len(discard_list)} cards")
                self.deck += discard_list
                self.current_player.cheated = False
                for card in discard_list:
                    if card.value != self.current_value:
                        self.current_player.cheated = True
                        break
                self.increment_current_value()

                # next player
                self.increment_player()
            else:
                print(f"{result.name} called {self.previous_player.name} a cheat")
                if self.previous_player.cheated:
                    self.previous_player.hand += self.deck
                else:
                    result.hand += self.deck
                self.deck = []
                self.current_value = 1

            # print player povs
            for player in self.players:
                print(player.name, self.pov_data(player))
