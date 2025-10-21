import asyncio
import json
import random
from api.action import Action, Discard, CallBluff
from api.card import Card, Rank
from api.bot_player import BotPlayer
from api.human_player import HumanPlayer
from api.player import Player
from api.queue import Queue


class Cheat:
    def __init__(self):
        self.playing = False
        self.deck = Card.create_deck()
        self.current_rank = Rank(1)
        self.log: list[Action] = []
        self.queue: Queue = Queue()

    # @property
    # def human_players(self) -> list[HumanPlayer]:
    #     return list(
    #         filter(lambda player: isinstance(player, HumanPlayer), self.players)
    #     )
    #
    # @property
    # def bot_players(self) -> list[BotPlayer]:
    #     return list(filter(lambda player: isinstance(player, BotPlayer), self.players))

    def join(self, player: Player) -> None:
        self.queue.add(player)

    @property
    def last_action(self) -> Action:
        return self.log[-1]

    @property
    def all_ready(self):
        return len(self.queue) != 0 and all(map(lambda p: p.ready, self.queue.all))

    # async def broadcast(self, message: Any):
    #     for player in self.human_players:
    #         await player.websocket.send_json(message)

    def pov_data(self, player: Player):
        current_player = self.queue.current
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
                for p in list(filter(lambda _p: _p.name != player.name, self.queue.all))
            ],
            "waiting-for": current_player.name,
            "own-turn": current_player.name == player.name,
            "current_rank": repr(self.current_rank),
            "log": list(map(lambda a: repr(a), self.log)),
        }

    async def discard(self, player: Player, discard_list: list[Card]) -> None:
        for card in discard_list:
            player.hand.remove(card)
        self.deck += discard_list
        self.log.append(Discard(player, discard_list, self.current_rank))
        self.current_rank.increment()
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
        for player in self.queue.all:
            print(player.name, json.dumps(self.pov_data(player), indent=4))

    async def broadcast_povs(self) -> None:
        for player in self.queue.all:
            if isinstance(player, HumanPlayer):
                await player.websocket.send_json(self.pov_data(player))
            elif isinstance(player, BotPlayer):
                await player.update_pov(self.pov_data(player))

    def create_hands(self) -> None:
        random.shuffle(self.deck)
        hand_size = len(self.deck) // len(self.queue)
        for player in self.queue.all:
            for i in range(hand_size):
                player.hand.append(self.deck.pop())
        player_iterator = iter(self.queue.all)
        while len(self.deck) > 0:
            next(player_iterator).hand.append(self.deck.pop())

    async def start(self):
        if not self.all_ready:
            return
        print("starting")

        self.queue.add(BotPlayer())
        self.create_hands()
        self.playing = True
        await self.broadcast_povs()

        # await first discard
        player = self.queue.next()
        discard_list = await player.play_turn()
        await self.discard(player, discard_list)

        while True:
            player = self.queue.next()
            tasks = []

            if isinstance(self.last_action, CallBluff):
                tasks.append(player.play_turn())
            else:
                tasks.append(player.play_turn_or_callout())
                for _player in self.queue.all:
                    if _player == player or _player == self.last_action.player:
                        continue
                    tasks.append(_player.callout())

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
                await self.discard(player, discard_list)
            elif isinstance(result, Player):
                player = result
                await self.call_bluff(player, self.last_action)
                discard_list = await player.play_turn()
                await self.discard(player, discard_list)
