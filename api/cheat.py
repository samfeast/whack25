import asyncio
import json
import random
from typing import Any
from api.action import Action, Discard, CallBluff, Pass
from api.card import Card, Rank
from api.bot_player import BotPlayer
from api.human_player import HumanPlayer
from api.player import Player


class Queue:
    def __init__(self) -> None:
        self.queue: list[Player] = []
        self.index = -1

    def __len__(self) -> int:
        return len(self.queue)

    def add(self, player: Player) -> None:
        self.queue.append(player)

    def next(self) -> Player:
        self.index += 1
        self.index %= len(self)
        return self.queue[self.index]


class Cheat:
    def __init__(self):
        self.playing = False
        self.current_player_index = 0
        self.players: list[Player] = []
        self.deck = Card.create_deck()
        self.current_rank = Rank(1)
        self.log: list[Action] = []

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
    def last_action(self) -> Action:
        return self.log[-1]

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

    def pov_data(self, player: Player):
        return {
            "name": player.name,
            "hand": list(map(lambda c: str(c), sorted(player.hand))),
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
            "current_rank": repr(self.current_rank),
            "log": list(map(lambda a: repr(a), self.log)),
        }

    async def discard(self, player: Player, discard_list: list[Card]) -> None:
        for card in discard_list:
            player.hand.remove(card)
        self.deck += discard_list
        self.log.append(Discard(self.current_player, discard_list, self.current_rank))
        self.current_rank.increment()
        self.increment_player()
        await self.broadcast_povs()

    async def call_bluff(self, challenger: Player, action: Discard) -> None:
        bluffer = action.player
        cheated = not action.is_valid()
        print(cheated)
        if cheated:
            bluffer.hand += self.deck
        else:
            challenger.hand += self.deck

        self.deck = []
        print(self.deck)
        self.current_rank = Rank(1)
        self.log.append(CallBluff(challenger, action.player, cheated))
        await self.broadcast_povs()

    def print_povs(self) -> None:
        for player in self.players:
            print(player.name, json.dumps(self.pov_data(player), indent=4))

    async def broadcast_povs(self) -> None:
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
        await self.discard(self.current_player, discard_list)

        while True:
            tasks = []

            if isinstance(self.last_action, CallBluff):
                tasks.append(self.current_player.play_turn())
            else:
                tasks.append(self.current_player.play_turn_or_callout())
                for player in self.players:
                    if player == self.current_player or player == self.previous_player:
                        continue
                    tasks.append(player.callout())

            tasks = map(asyncio.create_task, tasks)

            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            finished = done.pop()
            result = await finished

            if isinstance(result, list):
                discard_list = result
                await self.discard(self.current_player, discard_list)
            elif isinstance(result, Player):
                player = result
                await self.call_bluff(player, self.last_action)
                discard_list = await self.current_player.play_turn()
                await self.discard(self.current_player, discard_list)
