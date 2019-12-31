import random
import itertools

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

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

    def __repr__(self):
        return self.name

class Game:
    def __init__(self, num_players=2):
        self.deck = sum((make_deck() for _ in range(2)), [])
        self.players = itertools.cycle(
            Player(f"player {i + 1}") for i in range(num_players)
        )
        self.player = self.players.__next__()

if __name__ == "__main__":
    game = Game()
    print(len(game.deck))
