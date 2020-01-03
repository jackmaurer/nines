import random
import itertools
import statistics

def maxima(iterable, key=None):
    max_value = None
    for item in iterable:
        value = key(item) if key else item
        if max_value is None or value > max_value:
            max_items = [item]
            max_value = value
        elif value == max_value:
            max_items.append(item)
    return max_items

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
        if cue == self.game.TURN_OVER:
            print("In which column (1-3) do you"
                  " want to turn over a card?")
            column = self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: 0 <= x <= 2
            )
            print("In which row (1-3) do you want to"
                  " turn over a card?")
            return column, self.get_user_input(
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
        elif cue == self.game.PLACE:
            new_card = args[0]
            if len(self.hand) > 1 or True:
                # It doesn't make sense to ask which column when
                # there's only one, but it always tripped me up when I
                # was rushing through test runs and it didn't, because
                # I would enter the column when it asked for the row.
                print(f"In which column (1-{len(self.hand)}) do you"
                      f" want to place your {new_card.rank.upper()}?")
                column = self.get_user_input(
                    filter_fn=lambda s: int(s) - 1,
                    validator=lambda x: 0 <= x <= len(self.hand) - 1
                )
            else:
                column = 0
            print("In which row (1-3) do you want to"
                  f" place your {new_card.rank.upper()}?")
            return column, self.get_user_input(
                filter_fn=lambda s: int(s) - 1,
                validator=lambda x: 0 <= x <= 2
            )

    def get_user_input(self, prompt="> ",
                       filter_fn=None,
                       validator=None):
        while 1:
            s = input(prompt)
            if filter_fn:
                try:
                    s = filter_fn(s)
                except ValueError:
                    continue
            if validator is None or validator(s): return s

class AIPlayer(Player):
    HAS_TWO_IN_COLUMN, LOW_ENOUGH, TOO_HIGH = range(3)

    def __init__(self, game, name):
        Player.__init__(self, game, name)
        self.mean_value = statistics.mean(game.point_values.values())
        self.column = None
        self.row = None

    def get_input(self, cue, *args):
        if cue == self.game.TURN_OVER:
            for column in range(3):
                if not self.hand[column][0].face_up:
                    return column, 0
        elif cue == self.game.DRAW_OR_DISCARD:
            discard = self.game.discard_pile[-1]
            wanted, reason = self.wants_card(discard)
            rank_upper = discard.rank.upper()
            if reason == self.HAS_TWO_IN_COLUMN:
                print(f"-I already have two {rank_upper} cards in a"
                     f" column, so I'm going to take this {rank_upper}.")
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
            wanted, reason = self.wants_card(new_card, from_discard=False)
            rank_upper = new_card.rank.upper()
            if reason == self.HAS_TWO_IN_COLUMN:
                print(f"-I already have two {rank_upper} cards in a"
                      f" column, so I'm going to keep this {rank_upper}.")
            elif reason == self.LOW_ENOUGH:
                print(f"-This {rank_upper} is only worth"
                      f" {self.game.point_values[new_card.rank]} points,"
                      " so I'm going to keep it.")
            elif reason == self.TOO_HIGH:
                print(f"-This {rank_upper} is worth"
                      f" {self.game.point_values[new_card.rank]} points,"
                      " which is too high for my taste.")
            return "keep" if wanted else "discard"
        elif cue == self.game.PLACE:
            position = self.column, self.row
            self.column, self.row = None, None
            return position

    def wants_card(self, new_card, from_discard=True):
        number_face_down = self.number_face_down()
        new_card_value = self.game.point_values[new_card.rank]
        min_score = self.min_score()
        min_opponent_score = self.min_opponent_score()
        columns_with_two = self.columns_with_two(new_card.rank)
        if columns_with_two:
            if (number_face_down > 1
                or self.game.out_player
                or (min_score - 2 * new_card_value) < min_opponent_score):
                self.column = self.max_column(columns_with_two)
            for i in columns_with_two:
                if all(card.face_up for card in self.hand[i]):
                    self.column = i
            if self.column is not None:
                for (i, card) in enumerate(self.hand[self.column]):
                    if card.rank != new_card.rank:
                        self.row = i
                        break
                assert self.row is not None
                return True, self.HAS_TWO_IN_COLUMN
        if from_discard and new_card_value > self.mean_value:
            return False, self.TOO_HIGH
        can_replace_face_down = (
            number_face_down > 1
            or self.game.out_player
            or (min_score + new_card_value < min_opponent_score)
        )
        columns = [
            (i, column) for (i, column) in enumerate(self.hand) if any(
                (card.face_up or can_replace_face_down)
                and self.expected_value(card.rank) > new_card_value
                for card in column
            )
        ]
        columns = []
        positions = []
        for (i, column) in enumerate(self.hand):
            for (j, card) in enumerate(column):
                if ((card.face_up or can_replace_face_down)
                        and self.expected_value(card.rank) > new_card_value):
                    if i not in columns: columns.append((i, column))
                    positions.append((i, j))
        if not positions: return False, self.TOO_HIGH
        columns_with_same_rank = [
            (i, column) for (i, column) in columns if any(
                card.rank == new_card.rank for card in column
            )
        ]
        if columns_with_same_rank:
            columns_toak = [self.column_toak(column)
                            for (i, column) in columns_with_same_rank]
            columns = [
                pair for (i, pair) in enumerate(
                    columns_with_same_rank
                ) if columns_toak[i] is None
            ] or [
                pair for (i, pair) in enumerate(
                    columns_with_same_rank
                ) if self.game.point_values[columns_toak[i]] > new_card_value
            ] or columns
        else:
            columns = [(i, column) for (i, column) in columns
                       if self.column_toak(column) is None] or columns
        columns = [i for (i, column) in columns]
        positions = [(i, j) for (i, j) in positions if i in columns]
        self.column, self.row = min(
            maxima(
                positions,
                key=lambda position: self.expected_value(
                    self.hand[position[0]][position[1]].rank
                )
            ),
            key=lambda position: sum(
                card.face_up for card in self.hand[position[0]]
            )
        )
        return True, self.LOW_ENOUGH

    def column_toak(self, column):
        column_ranks = []
        for card in column:
            if not card.face_up: continue
            if card.rank in column_ranks: return card.rank
            column_ranks.append(card.rank)

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

    def number_face_down(self):
        return sum(
            not card.face_up for column in self.hand for card in column
        )

    def min_score(self, player=None):
        # TODO: Account for possibility that a face-down card will
        # complete three of a kind?
        player = self if player is None else player
        return sum(self.game.point_values[card.rank]
                   for column in player.hand for card in column
                   if card.face_up)

    def min_opponent_score(self):
        return min(map(self.min_score, self.other_players()))

    def other_players(self):
        return (player for player in self.game.players if player is not self)


class Game:
    (TURN_OVER, DRAW_OR_DISCARD,
     KEEP_OR_DISCARD, PLACE) = range(4)

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
            AIPlayer(self, "computer 1"),
            AIPlayer(self, "computer 2")
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
                column, row = player.get_input(self.TURN_OVER)
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
                column, row = player.get_input(self.PLACE, new_card)
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
