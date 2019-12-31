import random
import itertools

class Card:
    def __init__(self, suit, rank, face_down=True):
        self.suit = suit
        self.rank = rank
        self.face_down = face_down

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

def make_deck():
    return [Card(suit, rank) for suit in [
        "clubs", "diamonds", "hearts", "spades"
    ] for rank in [
        "ace", "king", "queen", "jack",
        "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
    ]]

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = None

    def __repr__(self):
        return self.name

class Game:
    def __init__(self, num_players=2):
        self.draw_pile = sum((make_deck() for _ in range(2)), [])
        self.discard_pile = []
        self.players = [Player(f"player {i + 1}") for i in range(num_players)]
        self.players_cycle = itertools.cycle(self.players)
        random.shuffle(self.draw_pile)
        self.player = self.players_cycle.__next__()

    def draw_hands(self):
        for player in self.players:
            player.hand = [
                [self.draw_pile.pop() for _ in range(3)] for _ in range(3)
            ]

if __name__ == "__main__":
    game = Game()
    game.draw_hands()
    for player in game.players:
        print(f"{player.name}:")
        for i in range(3):
            print("\t".join(column[i].rank for column in player.hand))
