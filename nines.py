import random
import itertools

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def rank_abbrev(self):
        return {
            "ace": "A",
            "king": "K",
            "queen": "Q",
            "jack": "J",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10"
        }[self.rank]

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

    def print_hand(self):
        for i in range(3):
            lines = [[], [], []]
            for column in self.hand:
                card = column[i]
                lines[0].append("+--+")
                if card.face_up:
                    lines[1].append(f"|{card.rank_abbrev().center(2)}|")
                else:
                    lines[1].append("|  |")
                lines[2].append("+--+")
            for line in lines:
                print(" ".join(line))

class Game:
    def __init__(self, num_players=2):
        self.draw_pile = sum((make_deck() for _ in range(2)), [])
        self.discard_pile = []
        self.players = [Player(f"player {i + 1}") for i in range(num_players)]

    def draw_hands(self):
        for player in self.players:
            player.hand = [
                [self.draw_pile.pop() for _ in range(3)] for _ in range(3)
            ]

    def run(self):
        # TODO: Put all cards in draw pile
        random.shuffle(self.draw_pile)
        self.discard_pile.append(self.draw_pile.pop())
        self.draw_hands()
        for player in self.players:
            s = f"{player.name}'s turn"
            print(s)
            print("=" * len(s))
            input("Press ENTER to continue.")
            player.print_hand()
            for _ in range(2):
                print("In which column (1-3) do you"
                      " want to turn over a card?")
                while 1:
                    column = input("> ")
                    try:
                        column = int(column)
                    except ValueError:
                        pass
                    else:
                        if 1 <= column <= 3:
                            break
                column -= 1
                print("In which row (1-3) do you want to"
                      " turn over a card?")
                while 1:
                    row = input("> ")
                    try:
                        row = int(row)
                    except ValueError:
                        pass
                    else:
                        if 1 <= row <= 3:
                            row -= 1
                            if not player.hand[column][row].face_up:
                                break
                card = player.hand[column][row]
                card.face_up = True
                print(f"You turned over a {card.rank.upper()}.")
                player.print_hand()
                print()
        for player in itertools.cycle(self.players):
            s = f"{player.name}'s turn"
            print(s)
            print("=" * len(s))
            input("Press ENTER to continue.")
            print(f"Discard pile: {self.discard_pile[-1].rank_abbrev()}")
            player.print_hand()
            print("Do you want to take a card from the DRAW pile"
                  " or the DISCARD pile?")
            while 1:
                action = input("> ").strip().lower()
                if action in ["draw", "discard"]:
                    break
            new_card = {"draw": self.draw_pile,
                        "discard": self.discard_pile}[action].pop()
            new_card.face_up = True
            # TODO: If you take a card from the discard pile, you should
            # only be allowed to keep it
            print(f"You have a {new_card.rank.upper()}.")
            print("Do you want to KEEP or DISCARD your"
                  f" {new_card.rank.upper()}?")
            while 1:
                action = input("> ").strip().lower()
                if action in ["keep", "discard"]:
                    break
            if action == "keep":
                print(f"In which column (1-{len(player.hand)}) do you"
                      f" want to place your {new_card.rank.upper()}?")
                while 1:
                    column = input("> ")
                    try:
                        column = int(column)
                    except ValueError:
                        pass
                    else:
                        if 1 <= column <= 3:
                            break
                column -= 1
                print("In which row (1-3) do you want to"
                      f" place your {new_card.rank.upper()}?")
                while 1:
                    row = input("> ")
                    try:
                        row = int(row)
                    except ValueError:
                        pass
                    else:
                        if 1 <= row <= 3:
                            break
                row -= 1
                self.discard_pile.append(player.hand[column][row])
                player.hand[column][row] = new_card
                print(f"You discarded a {self.discard_pile[-1].rank.upper()}")
            else:
                self.discard_pile.append(new_card)
                print(f"You discarded a {self.discard_pile[-1].rank.upper()}")
            player.print_hand()
            print()

if __name__ == "__main__":
    game = Game()
    game.run()
