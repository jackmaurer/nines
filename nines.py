import random
import itertools
import statistics

class Card:
    def __init__(self, suit, rank, face_up=False):
        self._suit = suit
        self._rank = rank
        self.face_up = face_up

    @property
    def suit(self):
        if self.face_up: return self._suit

    @property
    def rank(self):
        if self.face_up: return self._rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}" if self.face_up else "?"

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
    def __init__(self, game, name):
        self.game = game
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

    def score(self):
        return sum(self.game.point_values[card.rank]
                   for column in self.hand
                   for card in column)

    def get_input(self, cue, *args):
        if cue == self.game.TURN_OVER_COLUMN:
            print("In which column (1-3) do you"
                  " want to turn over a card?")
            return self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: 0 <= x <= 2
            )
        elif cue == self.game.TURN_OVER_ROW:
            print("In which row (1-3) do you want to"
                  " turn over a card?")
            column = args[0]
            return self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: (
                    0 <= x <= 2 and not self.hand[column][x].face_up
                )
            )
        elif cue == self.game.DRAW_OR_DISCARD:
            print("Do you want to take a card from the DRAW pile"
                  " or the DISCARD pile?")
            return self.get_user_input(
                filter_fn=lambda s: s.strip().lower(),
                validator=lambda s: s in ["draw", "discard"]
            )
        elif cue == self.game.KEEP_OR_DISCARD:
            new_card = args[0]
            print("Do you want to KEEP or DISCARD your"
                  f" {new_card.rank.upper()}?")
            return self.get_user_input(
                filter_fn=lambda s: s.strip().lower(),
                validator=lambda s: s in ["keep", "discard"]
            )
        elif cue == self.game.PLACE_COLUMN:
            new_card = args[0]
            num_columns = len(self.hand)
            if (num_columns == 1): return 0
            print(f"In which column (1-{num_columns}) do you"
                  f" want to place your {new_card.rank.upper()}?")
            return self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: 0 <= x <= len(self.hand) - 1
            )
        elif cue == self.game.PLACE_ROW:
            new_card = args[0]
            print("In which row (1-3) do you want to"
                  f" place your {new_card.rank.upper()}?")
            return self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: 0 <= x <= 2
            )

    def get_user_input(self, prompt="> ",
                       filter_fn=None,
                       validator=None):
        while 1:
            s = input(prompt)
            if filter_fn is not None:
                try:
                    s = filter_fn(s)
                except ValueError:
                    continue
            if validator is None or validator(s): return s


class ImpatientAI(Player):
    def __init__(self, game, name):
        Player.__init__(self, game, name)
        self.mean_value = statistics.mean(game.point_values.values())

    def get_input(self, cue, *args):
        if cue == self.game.TURN_OVER_COLUMN:
            return 0
        elif cue == self.game.TURN_OVER_ROW:
            column = args[0]
            for row in range(3):
                if not self.hand[column][row].face_up:
                    return row
        elif cue == self.game.DRAW_OR_DISCARD:
            discard = self.game.discard_pile[-1]
            if self.game.point_values[discard.rank] < self.mean_value:
                return "discard"
            return "draw"
        elif cue == self.game.KEEP_OR_DISCARD:
            new_card = args[0]
            if self.game.point_values[new_card.rank] < self.mean_value:
                return "keep"
            return "discard"
        elif cue == self.game.PLACE_COLUMN:
            new_card = args[0]
            for (i, column) in enumerate(self.hand):
                if not all(card.face_up for card in column):
                    return i
        elif cue == self.game.PLACE_ROW:
            new_card, column = args
            for (i, card) in enumerate(self.hand[column]):
                if not card.face_up:
                    return i


class PrudentAI(Player):
    HAS_TWO_IN_COLUMN = 0
    ALL_TOAK = 1
    LOW_ENOUGH = 2
    TOO_HIGH = 3

    def __init__(self, game, name):
        Player.__init__(self, game, name)
        self.mean_value = statistics.mean(game.point_values.values())

    def get_input(self, cue, *args):
        if cue == self.game.TURN_OVER_COLUMN:
            return 0
        elif cue == self.game.TURN_OVER_ROW:
            column = args[0]
            for row in range(3):
                if not self.hand[column][row].face_up:
                    return row
        elif cue == self.game.DRAW_OR_DISCARD:
            discard = self.game.discard_pile[-1]
            wanted, reason = self.wants_card(discard)
            rank_upper = discard.rank.upper()
            if reason == self.HAS_TWO_IN_COLUMN:
                print(f"-I already have two {rank_upper} cards in a"
                     f" column, so I'm going to take this {rank_upper}.")
            elif reason == self.ALL_TOAK:
                print("-I already have two of a kind in every column,"
                      f" so I'm going to pass on that {rank_upper}.")
            elif reason == self.LOW_ENOUGH:
                print(f"-This {rank_upper} is only worth"
                      f" {self.game.point_values[discard.rank]} points,"
                      " so I'm going to take it.")
            elif reason == self.TOO_HIGH:
                print(f"-That {rank_upper} is worth"
                      f" {self.game.point_values[discard.rank]} points,"
                      " which is too high for my taste.")
            return "discard" if wanted else "draw"
        elif cue == self.game.KEEP_OR_DISCARD:
            new_card = args[0]
            wanted, reason = self.wants_card(new_card)
            rank_upper = new_card.rank.upper()
            if reason == self.HAS_TWO_IN_COLUMN:
                print(f"-I already have two {rank_upper} cards in a"
                      f" column, so I'm going to keep this {rank_upper}.")
            elif reason == self.ALL_TOAK:
                print("-I already have two of a kind in every column,"
                      f" so I'm going to pass on this {rank_upper}.")
            elif reason == self.LOW_ENOUGH:
                print(f"-This {rank_upper} is only worth"
                      f" {self.game.point_values[new_card.rank]} points,"
                      " so I'm going to keep it.")
            elif reason == self.TOO_HIGH:
                print(f"-This {rank_upper} is worth"
                      f" {self.game.point_values[new_card.rank]} points,"
                      " which is too high for my taste.")
            return "keep" if wanted else "discard"
        elif cue == self.game.PLACE_COLUMN:
            new_card = args[0]
            return self.choose_column(new_card)
        elif cue == self.game.PLACE_ROW:
            new_card, column = args
            return self.choose_row(new_card, column)

    def wants_card(self, new_card):
        if self.has_two_in_column(new_card.rank):
            return (True, self.HAS_TWO_IN_COLUMN)
        columns_without_toak = self.columns_without_toak()
        if not columns_without_toak: return (False, self.ALL_TOAK)
        # TODO: Take into account if the only card we want to replace
        # with this one is the last face-down card
        # new_card_value = self.game.point_values[new_card.rank]
        # for i in columns_without_toak:
        #     for card in self.hand[i]:
        #         if self.expected_value(card.rank) > new_card_value:
        #             return (True, self.LOW_ENOUGH)
        if self.game.point_values[new_card.rank] < self.mean_value:
            return (True, self.LOW_ENOUGH)
        return (False, self.TOO_HIGH)

    # TODO: Prefer to put card in column where there is already a
    # face-up card of the same rank or where all cards are face-down.

    # TODO: If all rows have two of a kind, and more than one card
    # remains face-down, consider taking a card even if it will not
    # make three of a kind.

    def choose_column(self, new_card):
        columns_with_two = self.columns_with_two(new_card.rank)
        if columns_with_two: return self.max_column(columns_with_two)
        return max(
            self.columns_without_toak(),
            key=lambda i: max(self.expected_value(card.rank)
                              for card in self.hand[i])
        )

    def choose_row(self, new_card, column):
        return max(
            ((i, card) for (i, card) in enumerate(self.hand[column])
             if card.rank != new_card.rank),
            key=lambda pair: self.expected_value(pair[1].rank)
        )[0]

    def column_has_toak(self, column):
        column_ranks = []
        for card in column:
            if not card.face_up: continue
            if card.rank in column_ranks: return True
            column_ranks.append(card.rank)

    def has_two_in_column(self, rank):
        for column in self.hand:
            n = 0
            for card in column:
                if card.rank == rank:
                    n += 1
                    if n == 2:
                        return True

    # TODO: Only call this at most once per get_input call
    def columns_without_toak(self):
        return [i for (i, column) in enumerate(self.hand)
                if not self.column_has_toak(column)]

    # def opponents_max_turned_over(self):
    #     return max(
    #         sum(card.face_up for column in player.hand for card in column)
    #         for player in self.game.players if player is not self
    #     )

    def columns_with_two(self, rank):
        columns = []
        for (i, column) in enumerate(self.hand):
            n = 0;
            for card in column:
                if card.rank == rank:
                    n += 1
                    if n == 2:
                        columns.append(i)
                        break
        return columns

    def expected_value(self, rank):
        return (self.mean_value if rank is None
                else self.game.point_values[rank])

    def max_column(self, columns):
        return max(columns, key=lambda i: sum(
            self.expected_value(card.rank) for card in self.hand[i]
        ))


class Game:
    TURN_OVER_COLUMN = 0
    TURN_OVER_ROW = 1
    DRAW_OR_DISCARD = 2
    KEEP_OR_DISCARD = 3
    PLACE_COLUMN = 4
    PLACE_ROW = 5

    point_values = {
        "ace":  1,
        "king": 0,
        "queen": 10,
        "jack": 10,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    def __init__(self, players=None):
        self.deck = sum((make_deck() for _ in range(2)), [])
        self.draw_pile = []
        self.discard_pile = []
        self.players = [
            Player(self, "human"),
            PrudentAI(self, "computer")
        ] if players is None else players

    def draw_hands(self):
        for player in self.players:
            player.hand = [
                [self.draw_pile.pop() for _ in range(3)] for _ in range(3)
            ]

    def draw(self):
        card = self.draw_pile.pop()
        card.face_up = True
        return card

    def run(self):
        # TODO: Empty hands at end of game?
        random.shuffle(self.deck)
        self.draw_pile = [card for card in self.deck]
        self.discard_pile.append(self.draw())
        self.draw_hands()
        self.out_player = None
        for player in self.players:
            s = f"{player.name.upper()}'s turn"
            print(s)
            print("=" * len(s))
            input("Press ENTER to continue.")
            player.print_hand()
            for _ in range(2):
                column = player.get_input(self.TURN_OVER_COLUMN)
                row = player.get_input(self.TURN_OVER_ROW, column)
                card = player.hand[column][row]
                card.face_up = True
                print(f"{player.name.upper()} turned over a"
                      f" {card.rank.upper()}.")
                player.print_hand()
                print()
        for player in itertools.cycle(self.players):
            if player is self.out_player:
                break
            s = f"{player.name.upper()}'s turn"
            print(s)
            print("=" * len(s))
            input("Press ENTER to continue.")
            print(f"Discard pile: {self.discard_pile[-1].rank_abbrev()}")
            player.print_hand()
            action1 = player.get_input(self.DRAW_OR_DISCARD)
            new_card = {"draw": self.draw_pile,
                        "discard": self.discard_pile}[action1].pop()
            new_card.face_up = True
            if action1 == "draw":
                print(f"{player.name.upper()} drew a {new_card.rank.upper()}")
                action2 = player.get_input(self.KEEP_OR_DISCARD, new_card)
            else:
                print(f"{player.name.upper()} took a {new_card.rank.upper()}"
                      " from the discard pile")
                action2 = "keep"
            if action2 == "keep":
                column = player.get_input(self.PLACE_COLUMN, new_card)
                row = player.get_input(self.PLACE_ROW, new_card, column)
                old_card = player.hand[column][row]
                old_card.face_up = True
                self.discard_pile.append(old_card)
                player.hand[column][row] = new_card
            else:
                self.discard_pile.append(new_card)
            print(f"{player.name.upper()} discarded a"
                  f" {self.discard_pile[-1].rank.upper()}")
            for column in player.hand:
                if all(card.face_up and card.rank == column[0].rank
                       for card in column):
                    player.hand.remove(column)
            if self.out_player:
                for column in player.hand:
                    for card in column:
                        card.face_up = True
            else:
                if all(card.face_up for column in player.hand
                       for card in column):
                    print(f"{player.name.upper()} went out with"
                          f" {player.score()} points!")
                    self.out_player = player
            player.print_hand()
            print()
        self.print_results()

    def print_results(self):
        results = [(player, player.score()) for player in self.players]
        results.sort(key=lambda pair: pair[1])
        name_width = max(
            4, *(len(player.name) for player in self.players)
        )
        s = f"Rank  {'Name'.ljust(name_width)}  Score"
        print(s)
        print("=" * len(s))
        for (i, (player, score)) in enumerate(results):
            print(f"{str(i + 1).ljust(4)}"
                  f"  {player.name.ljust(name_width)}  {score}")

if __name__ == "__main__":
    game = Game()
    game.run()
