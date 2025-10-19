import asyncio
import json
import random
from typing import Any

from card import generate_deck, Card
from player import Player, HumanPlayer, BotPlayer


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

    @property
    def bot_players(self) -> list[BotPlayer]:
        return list(filter(lambda player: isinstance(player, BotPlayer), self.players))

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
            "hand": list(map(lambda c: str(c), player.hand)),
            "stack-size": len(self.deck),
            "player_info": [
                {
                    "name": p.name,
                    "cards": len(p.hand),
                    "last-discard": len(p.last_discard),
                }
                for p in list(filter(lambda _p: _p.name != player.name, self.players))
            ],
            "waiting-for": self.current_player.name,
            "own-turn": self.current_player.name == player.name,
            "current_rank": self.current_value,
        }

    async def discard(self, discard_list: list[Card]) -> None:
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
        self.increment_player()
        await self.broadcast_povs()

    async def callout(self, caller: Player) -> None:
        print(f"{caller.name} called {self.previous_player.name} a cheat")
        if self.previous_player.cheated:
            self.previous_player.hand += self.deck
        else:
            caller.hand += self.deck
        self.deck = []
        self.current_value = 1
        await self.broadcast_povs()

    def print_povs(self) -> None:
        for player in self.players:
            print(player.name, json.dumps(self.pov_data(player), indent=4))

    async def broadcast_povs(self) -> None:
        # todo: ai player
        for player in self.human_players:
            await player.websocket.send_json(self.pov_data(player))
        for player in self.bot_players:
            await player.update_pov(self.pov_data(player))

    def create_hands(self) -> None:
        random.shuffle(self.deck)
        hand_size = len(self.deck) // len(self.players)
        for player in self.players:
            for i in range(hand_size):
                player.hand.append(self.deck.pop())
        player_iterator = iter(self.players)
        while len(self.deck) > 0:
            next(player_iterator).hand.append(self.deck.pop())

    async def start(self):
        if not self.all_ready:
            return
        print("starting")

        self.players.append(BotPlayer())
        self.create_hands()
        self.playing = True
        await self.broadcast_povs()

        # await first discard
        discard_list = await self.current_player.play_turn()
        await self.discard(discard_list)

        while True:
            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(self.current_player.play_turn_or_callout()),
                ]
                + [
                    asyncio.create_task(p.callout())
                    for p in list(
                        filter(
                            lambda p: p.name != self.previous_player.name
                            and p.name != self.current_player.name,
                            self.players,
                        )
                    )
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            finished = done.pop()
            result = await finished

            if finished is self.current_player.play_turn_or_callout:
                if isinstance(result, list):
                    discard_list = result
                    await self.discard(discard_list)
                elif isinstance(result, Player):
                    player = result
                    await self.callout(player)
                    # await discard
                    discard_list = await self.current_player.play_turn()
                    await self.discard(discard_list)
            elif isinstance(result, Player):
                await self.callout(result)
                result: Player
                # await discard
                discard_list = await self.current_player.play_turn()
                await self.discard(discard_list)
