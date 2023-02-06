from copy import deepcopy
from os import linesep

import random
from collections import namedtuple, deque

file = open("Ludo_board.txt", 'r')
Board_template = []

for i in file.readlines():
    lst = []
    for j in i:
        lst.append(j)
    lst.pop(-1)
    Board_template.append(lst)

Common_boxes = [
    (),
    (14, 2), (14, 8), (14, 14), (14, 20), (14, 26), (14, 32), (14, 38),
    (12, 38), (10, 38), (8, 38), (6, 38), (4, 38), (2, 38), (2, 44),
    (2, 50), (4, 50), (6, 50), (8, 50), (10, 50), (12, 50), (14, 50),
    (14, 56), (14, 62), (14, 68), (14, 74), (14, 80), (14, 86), (16, 86),
    (18, 86), (18, 80), (18, 74), (18, 68), (18, 62), (18, 56), (18, 50),
    (20, 50), (22, 50), (24, 50), (26, 50), (28, 50), (30, 50), (30, 44),
    (30, 38), (28, 38), (26, 38), (24, 38), (22, 38), (20, 38), (18, 38),
    (18, 32), (18, 26), (18, 20), (18, 14), (18, 8), (18, 2), (16, 2)
]

Coloured_boxes = {
    'yellow': [(), (16, 8), (16, 14), (16, 20), (16, 26), (16, 32), (16, 38)],
    'blue': [(), (4, 44), (6, 44), (8, 44), (10, 44), (12, 44), (14, 44)],
    'red': [(), (16, 80), (16, 74), (16, 68), (16, 62), (16, 56), (16, 50)],
    'green': [(), (28, 44), (26, 44), (24, 44), (22, 44), (20, 44), (18, 44)]
}

Rest_Area = {
    'yellow': [(), (6, 14), (6, 19), (8, 14), (8, 19)],
    'blue': [(), (6, 71), (6, 76), (8, 71), (8, 76)],
    'red': [(), (24, 71), (24, 76), (26, 71), (26, 76)],
    'green': [(), (24, 14), (24, 19), (26, 14), (26, 19)]
}

Pawn = namedtuple("Pawn", "index colour id")


class Game_board:

    def __init__(self):

        self.painter = Pawn_arrangements()
        self.size = 56
        self.Coloured_box_size = 7
        self.Colours = ['yellow', 'blue', 'red', 'green']
        self.Colour_distance = 14
        self.Pawns_position = {}

        self.Starting = {
            colour: 1 + index * self.Colour_distance for
            index, colour in enumerate(self.Colours)}

        self.Ending = {
            colour: index * self.Colour_distance
            for index, colour in enumerate(self.Colours)}
        self.Ending['yellow'] = self.size

        self.Board_position = (0, 0)

    def Place_pawn_on_board(self, pawn):
        self.Pawns_position[pawn] = self.Board_position

    def Pawn_position(self, pawn):
        return self.Pawns_position[pawn] == self.Board_position

    def Place_on_starting_point(self, pawn):
        start = self.Starting[pawn.colour.lower()]
        position = (start, 0)
        self.Pawns_position[pawn] = position

    def can_pawn_move(self, pawn, Dice_value):
        common_position, position = self.Pawns_position[pawn]

        if position + Dice_value > self.Coloured_box_size:
            return False

        return True

    def move_pawn(self, pawn, Dice_value):

        Common_position, position = self.Pawns_position[pawn]
        end = self.Ending[pawn.colour.lower()]

        if position > 0:
            position += Dice_value

        elif Common_position <= end < Common_position + Dice_value:
            position += Dice_value - (end - Common_position)
            Common_position = end

        else:
            Common_position += Dice_value

            if Common_position > self.size:
                Common_position = Common_position - self.size

        position = Common_position, position
        self.Pawns_position[pawn] = position

    def Check_for_end(self, pawn):
        common_position, position = self.Pawns_position[pawn]

        if position == self.Coloured_box_size:
            return True

        return False

    def Same_position(self, pawn):

        position = self.Pawns_position[pawn]
        lst = []
        for Current_pawn, Current_position in self.Pawns_position.items():
            if position == Current_position:
                lst.append(Current_pawn)

        return lst

    def paint_board(self):
        positions = {}

        for pawn, position in self.Pawns_position.items():
            common, private = position

            if not private == self.Coloured_box_size:
                positions.setdefault(position, []).append(pawn)

        return self.painter.paint(positions)


class Player:

    def __init__(self, colour, name=None, choose_pawn_delegate=None):

        self.name = name
        self.colour = colour
        self.choose_pawn_delegate = choose_pawn_delegate
        self.finished = False
        self.pawns = []

        if self.name is None and self.choose_pawn_delegate is None:
            self.name = "Computer"

        for i in range(4):
            self.pawns.append(Pawn(i + 1, colour, colour[0].upper() + str(i + 1)))

    def __str__(self):
        return "{}({})".format(self.name, self.colour)

    def choose_pawn(self, pawns):

        if len(pawns) == 1:
            index = 0
        elif len(pawns) > 1:
            if self.choose_pawn_delegate is None:
                index = random.randint(0, len(pawns) - 1)
            else:
                index = self.choose_pawn_delegate()
        return index


class dice:

    def __init__(self):
        self.Min = 1
        self.Max = 6

    def throw(self):
        return random.randint(self.Min, self.Max)

    def Display_dice(self, number, name=""):
        Template = [[" " * 20 + "|       |", " " * 20 + "|   #   |", " " * 20 + "|       |"],
                    [" " * 20 + "|       |", " " * 20 + "| #   # |", " " * 20 + "|       |"],
                    [" " * 20 + "|   #   |", " " * 20 + "|   #   |", " " * 20 + "|   #   |"],
                    [" " * 20 + "| #   # |", " " * 20 + "|       |", " " * 20 + "| #   # |"],
                    [" " * 20 + "| #   # |", " " * 20 + "|   #   |", " " * 20 + "| #   # |"],
                    [" " * 20 + "| #   # |", " " * 20 + "| #   # |", " " * 20 + "| #   # |"]]

        Dice = Template[number - 1]
        Dice[1] = Dice[1] + "  >>" + str(name)

        base = " " * 20 + "---------"
        print(base)
        for i in Dice:
            print(i)
        print(base)


class Pawn_arrangements:

    def __init__(self):
        self.Current_template = deepcopy(Board_template)

    def Place_pawns(self, position_pawns):
        for position, pawns in position_pawns.items():
            for index, pawn in enumerate(pawns):

                Common_position, Private_position = position
                colour = pawn.colour.lower()

                if Private_position > 0:
                    row, column = Coloured_boxes[colour][Private_position]

                elif Common_position == 0:
                    row, column = Rest_Area[colour][pawn.index]
                    index = 0

                else:
                    row, column = Common_boxes[Common_position]

                if index > 0:
                    self.Current_template[row - 1][column + index] = pawn.id[1]

                else:
                    self.Current_template[row - 1][column - 1] = pawn.id[0]
                    self.Current_template[row - 1][column] = pawn.id[1]

    def paint(self, position):

        self.Current_template = deepcopy(Board_template)
        self.Place_pawns(position)
        lst = []

        for i in self.Current_template:
            lst.append(''.join(i))

        return linesep.join(lst)


class Rules:

    def __init__(self):

        self.diceobj = dice()
        self.players = deque()
        self.board = Game_board()

        self.standing = []
        self.finished = False
        self.rolled_value = None
        self.Current_players = None
        self.allowed_pawns = []
        self.picked_pawn = None
        self.index = None
        self.jog_pawns = []

    def Add_player(self, player):
        self.players.append(player)
        for i in player.pawns:
            self.board.Place_pawn_on_board(i)

    def Available_colours(self):
        acquired = []
        for i in self.players:
            acquired.append(i.colour)

        available = set(self.board.Colours) - set(acquired)

        return sorted(available)

    def Next_turn(self):

        if self.rolled_value != self.diceobj.Max:
            self.players.rotate(-1)

        return self.players[0]

    def pullout_pawn(self, player):
        for i in player.pawns:
            if self.board.Pawn_position(i):
                return i

    def Allowed_moves(self, player, Dice_value):

        allowed_pawns = []

        if Dice_value == self.diceobj.Max:
            x = self.pullout_pawn(player)

            if x:
                allowed_pawns.append(x)

        for i in player.pawns:

            if not self.board.Pawn_position(i) and self.board.can_pawn_move(i, Dice_value):
                allowed_pawns.append(i)

        return sorted(allowed_pawns, key=lambda pawn: pawn.index)

    def Print_board(self):
        return self.board.paint_board()

    def Killer_move(self, pawn):

        for i in self.board.Same_position(pawn):

            if i.colour != pawn.colour:
                self.board.Place_pawn_on_board(i)
                self.jog_pawns.append(i)

    def Make_move(self, player, pawn):

        if self.rolled_value == self.diceobj.Max and self.board.Pawn_position(pawn):
            self.board.Place_on_starting_point(pawn)
            self.Killer_move(pawn)
            return

        self.board.move_pawn(pawn, self.rolled_value)

        if self.board.Check_for_end(pawn):
            player.pawns.remove(pawn)

            if not player.pawns:
                self.standing.append(player)
                self.players.remove(player)

                if len(self.players) == 1:
                    self.standing.extend(self.players)
                    self.finished = True

        else:
            self.Killer_move(pawn)

    def Play_turn(self, index=None, Dice_value=None):

        self.jog_pawns = []
        self.Current_players = self.Next_turn()

        if Dice_value is None:
            self.rolled_value = self.diceobj.throw()

        else:
            self.rolled_value = Dice_value
        self.allowed_pawns = self.Allowed_moves(self.Current_players, self.rolled_value)

        if self.allowed_pawns:

            if index is None:
                self.index = self.Current_players.choose_pawn(self.allowed_pawns)

            else:
                self.index = index
            self.picked_pawn = self.allowed_pawns[self.index]
            self.Make_move(self.Current_players, self.picked_pawn)

        else:
            self.index = -1
            self.picked_pawn = None


class Ludo:

    def __init__(self):
        self.game = Rules()
        self.diceobj = dice()
        self.prompted_for_pawn = False

    def Player_type(self):
        available_colours = self.game.Available_colours()

        print("Select player type to Continue:\n(a) Computer.\n(b) Human.")

        inputs = ['a', 'b']
        x = input("\nEnter the desired option number:")

        while x.lower() not in inputs:
            x = input("Invalid Input!!!\nEnter a correct option number:")

        if x.lower() == 'a':
            player = Player(available_colours.pop())
            self.game.Add_player(player)

        else:
            name = input("Enter player's name:")

            if len(available_colours) > 1:
                inputs = ['a', 'b', 'c', 'd']

                for i in range(len(available_colours)):
                    print("(", inputs[i], ")  ", available_colours[i], sep="")

                y = input("Enter an option number to choose a colour: ")

                while y.lower() not in inputs:
                    y = input("Invalid Input!!!\nEnter a correct option number:")

                colour = available_colours.pop(inputs.index(y))

            else:
                colour = available_colours.pop()

            player = Player(colour, name, self.Choose_move)
            self.game.Add_player(player)

    def Get_players(self):
        count = 0
        for i in range(2):
            print("\nAdd Player Number", count + 1)
            self.Player_type()
            print("Player has been Added to the Game.")
            count = count + 1

        print("\n\nSelect an option to Continue:\n(a) Add another Player.\n(b) Continue with the current players.")
        inputs = ['a', 'b']
        x = input("\nEnter the desired option number:")
        while x.lower() not in inputs:
            x = input("Invalid Input!!!\nEnter a correct option number:")

        while count < 4:
            if x.lower() == 'a':
                print("Add Player Number", count + 1)
                self.Player_type()
                print("Player has been Added to the Game.")
                count = count + 1
            else:
                break

    def Choose_move(self):

        inputs = ['a', 'b', 'c', 'd']

        print(self.diceobj.Display_dice(self.game.rolled_value, str(self.game.Current_players)))
        print("\nPlayer has more than one moves...\nChoose a move: ")
        for i in range(len(self.game.allowed_pawns)):
            print("(", inputs[i], ") ", self.game.allowed_pawns[i].id)

        x = input("Enter an option to choose a Move: ")

        while x.lower() not in inputs:
            x = input("Invalid Input!!!\nEnter a correct option number:")

        self.prompted_for_pawn = True
        return inputs.index(x)

    def Print_players(self):
        print("\n\nThe Game has the following", len(self.game.players), "players")

        for i in self.game.players:
            print(">>", i)

    def print_info_after_turn(self):

        pawns_id = []
        for i in self.game.allowed_pawns:
            pawns_id.append(i.id)

        if self.game.allowed_pawns:

            if self.prompted_for_pawn:
                self.prompted_for_pawn = False
                print(self.game.picked_pawn.id, "is moved.")
                return

            if self.game.jog_pawns:
                self.diceobj.Display_dice(self.game.rolled_value, str(self.game.Current_players))
                print("\nThere are", len(pawns_id), "possible moves as follows:\n.", "\n>>".join(pawns_id),
                      self.game.picked_pawn.id, "is moved.\nJog pawn.")

                for j in range(len(self.game.jog_pawns)):
                    print(self.game.jog_pawns[j].id, "\n")

        else:
            self.diceobj.Display_dice(self.game.rolled_value, str(self.game.Current_players))
            print("\n\nThere are no possible moves for This player.")

    def start(self):

        print("\nWelcome to Ludo Simulator\nThis Game can be played with 2 to 4 players where players can be Computer "
              "or Humans.\n To Start a New Game write *Start* or else write *Exit* to leave the simulator.")

        inputs = ['start', 'exit']

        x = input(">>>")

        while x.lower() not in inputs:
            x = input("Invalid Input!!!\nEnter a correct option number:")

        if x.lower() == 'start':
            self.Get_players()
            self.Print_players()
            while not self.game.finished:
                self.game.Play_turn()
                self.print_info_after_turn()
                print(self.game.Print_board())
                input("\n\nPress Enter to continue: \n")

            print(">>Game Finished<<")
        else:
            exit(0)


game = Ludo()
game.start()
