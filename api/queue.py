from api.player import Player


class Queue:
    def __init__(self) -> None:
        self.queue: list[Player] = []
        self.last_index = -1

    def __len__(self) -> int:
        return len(self.queue)

    @property
    def all(self) -> list[Player]:
        return self.queue

    @property
    def index(self) -> int:
        return (self.last_index + 1) % len(self)

    @property
    def current(self) -> Player:
        return self.queue[self.index]

    def add(self, player: Player) -> None:
        self.queue.append(player)

    def next(self) -> Player:
        current = self.current
        self.last_index = self.index
        return current
