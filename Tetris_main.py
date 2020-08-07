import time
import sys
import random
import copy
import json
import win32api
import win32con

# the playing field:



class Arena(object):

    def __init__(self): # creating the arena
        self.height = 20
        self.width = 10
        self.playspace = []
        self.piece = None
        self.rows_cleared = 0
        self.points = [40, 100, 300, 1200]
        self.score = 0
        self.level = 0
        self.played = False
        self.removable = False # indicating wheter we reached the end of a blocks track
        for i in range(self.width):# each horizontal spot takes up 2 spots in the screen output
            self.playspace.append([])
            for j in range(self.height):
                self.playspace[i].append(' ')
        self.dynamic_playspace = None

    def Update_level(self):
        if self.level < 5:
            self.level += 1

    def is_on_floor(self):
        """
        Determines weher or not a piece has hit another piece or the
        bottom of the playspace

        :return:
        boolean value
        """
        try:
            for t in self.piece.get_space():
                if self.playspace[t[0]][t[1]+1] != ' ':
                    return True
        except IndexError:
            return True

    def is_within_boundaries(self, movement):
        """
        check wether an active object is within the bouadaries of the play space

        :param movement: the current action either left (west) or rigjt (east) or a rotation (w)

        :return: boolean value .
        """

        if movement == ord('A'):

            for i in self.piece.get_space():

                if i[0] == 0:
                    return False
                if self.playspace[i[0]-1][i[1]] != ' ': # check 1 move to the left
                    return False

        if movement == ord('D'):
            for i in self.piece.get_space():
                if i[0] == self.width-1:
                    return False
                if self.playspace[i[0]+1][i[1]] != ' ': # check 1 move to the right.
                    return False

        if movement == ord('W'):
            testing_piece = copy.deepcopy(self.piece)
            testing_piece.change_orientation_right()
            for i in testing_piece.get_space():
                if i[0] > self.width-1 or i[0] < 0:
                    return False
                if self.playspace[i[0]][i[1]] != ' ':
                    return False

        if movement == ord('S'):
            testing_piece = copy.deepcopy(self.piece)
            testing_piece.change_orientation_left()
            for i in testing_piece.get_space():
                if i[0] > self.width-1 or i[0] < 0:
                    return False
                if self.playspace[i[0]][i[1]] != ' ':
                    return False

        return True




    def draw_arena(self,removable):

        """
        will print out all the current elements in play and will remove any full rows.

        """

        sys.stdout.write('\n' * 10) #obscuring previous state

        # printing the playing field

        sys.stdout.write('# ' * 11 + ' '*5 +'Score: ' + str(self.score) + '\n')
        y = 0
        if removable:
            scoring_tier = 0
        for j in range(self.height):
            line = ''

            for i in self.dynamic_playspace:# looping over the play space on a row by row basis.

                line = line + i[j]*2
            if removable:
                if ' ' not in line:
                    self.rows_cleared += 1
                    scoring_tier += 1
                    sketx = copy.deepcopy(self.playspace)
                    self.playspace = []
                    if y == len(sketx[0])-1:
                        for i in sketx:
                            self.playspace.append([' '] + i[:y])

                    else:
                        for i in sketx:
                            self.playspace.append([' '] + i[:y] + i[(y+1):])


            sys.stdout.write('#' + line + '#\n')
            y += 1
        sys.stdout.write('# ' * 11)
        sys.stdout.write('\n ')
        if removable and scoring_tier > 0:
            self.score += self.points[scoring_tier-1]

    def add_shape(self, shapes):
        self.piece = random.choice(shapes)
        self.dynamic_playspace = copy.deepcopy(self.playspace)
        for i in self.piece.get_space():
            self.dynamic_playspace[i[0]][i[1]] = self.piece.get_character()


    def Update_playfield(self):

        """if no Objects are in the playfield add one and print result.
        if an object is in the playfield, shift all y coordinitaes one down (up)
        print resulting playspace """

        if self.piece == None:
            self.add_shape([Long_Boy('Long', (5, 0)), sqaureward('Square', (5, 0)), T_boy('tea', (5, 0)), squid_one('nrone', (5, 0)),
                            squid_two('nrtwo', (5, 0)), L_girl('lrig', (5, 0)), other_g_girl('ogl', (5, 0))])
            self.removable = False
            if self.is_on_floor():
                raise ValueError
        else:

            copy_play = copy.deepcopy(self.playspace)
            x, y = self.piece.get_positions()
            if self.played:
                self.piece.set_position(x, y)
            else:
                self.piece.set_position(x, y + 1)

            self.dynamic_playspace = copy_play

            for i in self.piece.get_space():
                self.dynamic_playspace[i[0]][i[1]] = self.piece.get_character()

            if self.is_on_floor():

                self.playspace = copy.deepcopy(self.dynamic_playspace)
                self.piece = None
                self.removable = True






class Shape(object):
    def __init__(self, name, position):
        self.name = name# name of the shape (id)
        self.position = position# a tuple contaiing the x and y coordinate of the lower right block
        self.figure_5_by_5 = None
        self.character = None
        self.orientation = 'North'
        self.space = []

    def get_character(self):
        return self.character

    def get_name(self):
        return self.name

    def get_positions(self):
        return self.position

    def get_space(self):
        return self.space

    def set_position(self, x, y):
        self.position = (x, y)
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):
                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j - 2, self.position[1] + i - 2))
        self.space = space

    def change_orientation_right(self):
        if self.orientation == 'North':
            self.orientation = 'East'
        elif self.orientation == 'East':
            self.orientation = 'South'
        elif self.orientation == 'South':
            self.orientation = 'West'
        elif self.orientation == 'West':
            self.orientation = 'North'

        unchanged_figure = copy.deepcopy(self.figure_5_by_5)

        self.figure_5_by_5 = [['     '],
                              ['     '],
                              ['     '],
                              ['     '],
                              ['     ']]

        for i in range(len(unchanged_figure)):
            for j in range(len(unchanged_figure)):
                if unchanged_figure[i][0][j] == 'x':
                    empty = []

                    if i == 4:
                        empty.append(self.figure_5_by_5[4 - j][0][:i] + 'x')
                        self.figure_5_by_5[4 - j] = empty
                    else:
                        empty.append(self.figure_5_by_5[4 - j][0][:i] + 'x' + self.figure_5_by_5[4 - j][0][i+1:])
                        self.figure_5_by_5[4 - j] = empty

    def change_orientation_left(self):
        if self.orientation == 'East':
            self.orientation = 'North'
        elif self.orientation == 'South':
            self.orientation = 'East'
        elif self.orientation == 'West':
            self.orientation = 'South'
        elif self.orientation == 'North':
            self.orientation = 'West'

        unchanged_figure = copy.deepcopy(self.figure_5_by_5)

        self.figure_5_by_5 = [['     '],
                              ['     '],
                              ['     '],
                              ['     '],
                              ['     ']]

        for i in range(len(unchanged_figure)):
            for j in range(len(unchanged_figure)):
                if unchanged_figure[i][0][j] == 'x':
                    empty = []

                    if i == 4:
                        empty.append(self.figure_5_by_5[4 - j][0][:i] + 'x')
                        self.figure_5_by_5[4 - j] = empty
                    else:
                        empty.append(self.figure_5_by_5[4 - j][0][:i] + 'x' + self.figure_5_by_5[4 - j][0][i+1:])
                        self.figure_5_by_5[4 - j] = empty





class Long_Boy(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'L'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              [' xxxx'],
                              ['     '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space


class T_boy(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'T'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              [' xxx '],
                              ['  x  '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space


class L_girl(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'H'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              [' xxx '],
                              [' x   '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space


class other_g_girl(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'G'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              [' xxx '],
                              ['   x '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space

class squid_one(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'Z'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              [' xx  '],
                              ['  xx '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space


class squid_two(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'S'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              ['  xx '],
                              [' xx  '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space

class sqaureward(Shape):
    def __init__(self, name, position):
        Shape.__init__(self, name, position)
        self.character = 'Q'
        self.figure_5_by_5 = [['     '],
                              ['     '],
                              ['  xx '],
                              ['  xx '],
                              ['     ']]
        space = []
        for i in range(len(self.figure_5_by_5)):
            for j in range(len(self.figure_5_by_5)):

                if self.figure_5_by_5[i][0][j] == 'x':
                    space.append((self.position[0] + j-2, self.position[1] + i-2))
        self.space = space

# player controls

keysofinterest = [ord('A'), ord('D'), ord('W'), ord('S'), ord('T')]

# create player field
new_world = Arena()


for z in keysofinterest:
    win32api.GetAsyncKeyState(z)

player_name = input('Welcome, Lets play some Tetris\nWhat is your name: ')


for i in range(3):
    print('\n'*40)
    print('Allright ' + player_name + ' goodluck!!\n')
    print(3-i)
    time.sleep(1)


go = True
level = [0.3, 0.20, 0.15, 0.075, 0.02]
while go:
    try:
        new_world.Update_playfield()
    except ValueError:
        for i in range(3):
            print('\n' * 40)
            time.sleep(0.5)
            new_world.draw_arena(new_world.removable)
            time.sleep(0.5)
        print('Game over,... your Final score: '+ str(new_world.score) + '\nThank you for playing')
        try:
            with open('Highscores.json', 'r') as file_obj:
                results_list = json.load(file_obj)
        except FileNotFoundError:
            with open('Highscores.json', 'w') as file_obj:
                results_list = [['None', '000'], ['None', '000'], ['None', '000'], ['None', '000'], ['None', '000']]
                results = json.dump(results_list, file_obj)

        k = 0

        copylist = copy.deepcopy(results_list)

        for i in range(4):

            if k == 0:
                if int(copylist[i][1]) < new_world.score:
                    k += 1
                    copylist[i] = [player_name, str(new_world.score)]
                    copylist[k+i] = results_list[i]
            elif k ==1:
                copylist[k+i] = results_list[i]

        file_obj.close()


        with open('Highscores.json', 'w') as f_obj:
            json.dump(copylist, f_obj)

        f_obj.close()

        print('\nHighscores:\n')
        for i in range(len(copylist)):
            print(str(i+1)+'. ' + copylist[i][0] + ':  ' + copylist[i][1] +'\n')



        break

    new_world.draw_arena(new_world.removable)

    if new_world.rows_cleared > 5:
        new_world.Update_level()
        new_world.rows_cleared = 0

    time.sleep(level[new_world.level])

    new_world.played = False

    for k in range(len(keysofinterest)):
        if bool(win32api.GetAsyncKeyState(keysofinterest[k])):
            try:
                if keysofinterest[k] == ord('A'):
                    if new_world.is_within_boundaries(ord('A')):
                        x, y = new_world.piece.get_positions()
                        new_world.piece.set_position(x-1, y)
                        new_world.played = True
                if keysofinterest[k] == ord('D'):
                    if new_world.is_within_boundaries(ord('D')):
                        x, y = new_world.piece.get_positions()
                        new_world.piece.set_position(x+1, y)
                        new_world.played = True
                if keysofinterest[k] == ord('W'):
                    if new_world.is_within_boundaries(ord('D')):
                        new_world.piece.change_orientation_right()
                        new_world.played = True
                if keysofinterest[k] == ord('S'):
                    if new_world.is_within_boundaries(ord('S')):
                        new_world.piece.change_orientation_left()
                        new_world.played = True

                if keysofinterest[k] == ord('T'):
                    go = False

            except AttributeError:
                pass





