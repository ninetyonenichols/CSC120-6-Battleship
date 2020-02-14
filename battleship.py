'''
File: battleship.py
Author: Justin Nichols
Purpose: Models a one-sided game of Battleship. Reads two input files (one for
         p1's ship locations and one for p2's guesses). Prints output indicating
         the result of each guess. 
CSC120, Section 1, Fall 18
'''


# importing sys to use the 'exit' function later
import sys


class Board:
    '''
    Purpose: Manages game-pieces. Handles one ship-placements file and one
                 guesses-file
    Returns: none, but inifializes self._grid (a 10X10 grid of GridPos objects),
             self._ships_on_board (a set of Ship objects), and
             self._ship_placement_file_it_obj                 
    '''
    def __init__(self):
        self._grid = [[GridPos(x, y) for x in range(10)] for y in range(10)]
        self._ships_on_board = set()
        self._ship_placement_file_it_obj = None

    def process_ship_placement_file(self):
        '''
        Purpose: Accepts one input file containing info about ship-placements.
                 Makes sure all placements are legal. Keeps records of
                 placements in the appropriate Ship and / or GridPos objects
        '''
        
        # trying to open the input file
        ship_placement_file_name = input()
        try:
            self._ship_placement_file_it_obj = open(ship_placement_file_name)
        except FileNotFoundError:
            print("ERROR: Could not open file: " + ship_placement_file_name)
            sys.exit(1)


        # variables to help test legality of ship collection
        legal_ships_list = ['A', 'B', 'D', 'P', 'S']
        actual_ships_list = []

        # processing each line of ship-placement-info
        for ship_placement_info_line in self._ship_placement_file_it_obj:
            ship_placement_info_list = ship_placement_info_line.split()
            ship_type = ship_placement_info_line[0]
            # making sure that each ship is a valid type of ship
            # and that no ship-type appears more than once
            if (ship_type not in legal_ships_list) or \
               (ship_type in actual_ships_list):
                print('ERROR: fleet composition incorrect')
                sys.exit(1)
            # counting number of each type of ship
            actual_ships_list.append(ship_type)
            
            # making appropriate Ship object, adding to collection
            correct_ship_sizes = {'A': 5, 'B': 4, 'D': 3, 'P': 2, 'S': 3}
            ship_type = Ship(ship_placement_info_line, correct_ship_sizes)
            self._ships_on_board.add(ship_type)

            self.update_pos_occupations(ship_type, ship_placement_info_line)
            
                        
        # making sure number of each type of ship is correct
        actual_ships_list.sort()
        if actual_ships_list != legal_ships_list:
            print('ERROR: fleet composition incorrect')
            sys.exit(1)


    def get_grid(self):
        return self._grid


    def update_pos_occupations(self, ship, ship_placement_info_line):
        '''
        Purpose: keeps records of which positions a ship-object occupies.
        Independent records are stored in both the ship-object
        and the appropriate GridPos-objects for use in later computations
        Parameters: ship, a Ship obj. The ship currently being managed
                    ship_placement_info_line, a str. Contains info about the
                        current ship's placement on the board
        '''
   
        # getting needed attributes of ship
        x_start, x_stop, y_start, y_stop = ship.get_coords()
        orientation = ship.get_orientation()

        # creating list of grid_pos objects corresponding to positions
        # occupied by the ship
        if orientation == 'horz':
            list_of_grid_pos_objects = [self._grid[i][y_start] for \
                i in range(x_start, x_stop + 1)]
        else:
            list_of_grid_pos_objects = [self._grid[x_start][j] for \
                j in range(y_start, y_stop + 1)]
                
        ship.set_grid_positions_occupied(list_of_grid_pos_objects)

        # updating the grid_pos objects to reflect them being occupied
        for grid_pos_object in list_of_grid_pos_objects:
            ship_present = grid_pos_object.get_ship_present()
            if ship_present != None:
                print('ERROR: overlapping ship: ' + ship_placement_info_line)
                sys.exit(1)
            else:
                grid_pos_object.set_ship_present(ship)



    def process_guesses_file(self):
        '''
        Purpose: Accepts one input file containing info about the player's
                     guesses. Responds to each one
        '''
        
        #trying to open guesses-file
        guesses_file_name = input()
        try:
            guesses_file_it_obj = open(guesses_file_name)
        except FileNotFoundError:
            print('ERROR: Could not open file: ' + guesses_file_name)
            sys.exit(1)

        sunken_ships = []

        # responding to each guess
        for guess_info_line in guesses_file_it_obj:
            guess = guess_info_line.split()
            guessed_x, guessed_y = int(guess[0]), int(guess[1])
            
            # responding to illegal guesses
            if (guessed_x not in range(10)) or (guessed_y not in range(10)):
                print('illegal guess')
            # responding to legal guesses
            else:    
                guessed_pos = self._grid[guessed_x][guessed_y]
                ship_hit = guessed_pos.get_ship_present()
                prev_guessed = guessed_pos.get_prev_guessed()
                if ship_hit == None:
                    # responding to first miss at a location
                    if prev_guessed == False:
                        print('miss')
                    # repeated miss at location
                    else:
                        print('miss (again)')
                else:
                    hits_remaining = ship_hit.get_num_spots_not_yet_hit()

                    # first hit at location
                    if prev_guessed == False:
                        # case where ship sinks
                        if hits_remaining == 1:
                            ship_type = ship_hit.get_ship_type()
                            print('{} sunk'.format(ship_type))
                            sunken_ships.append(ship_hit)
                            # checking whether all ships have been sunk
                            if len(sunken_ships) == 5:
                                print('all ships sunk: game over')
                                sys.exit(1)
                        # first hit at location, but ship doesn't sink
                        else:
                            print('hit')
                        ship_hit.indicate_ship_hit()
                                            
                    # repeated hit at location
                    else:
                        print('hit (again)')

                # making note that location has now been guessed
                self._grid[guessed_x][guessed_y].indicate_prev_guessed()
        

    def __str__(self):
        return 'Board object. Handles input files. Manages game-pieces.'


class GridPos:
    '''
    Purpose: Keeps track of whether the corresponding position on the board has
             has a ship on it as well as whether or not it has been guessed
    '''
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._ship_present = None
        self._prev_guessed = False

    # getters
    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_ship_present(self):
        return self._ship_present

    def get_prev_guessed(self):
        return self._prev_guessed
    

    # setters
    def set_ship_present(self, ship):
        self._ship_present = ship

    def indicate_prev_guessed(self):
        self._prev_guessed = True
        
    def __str__(self):
        return 'x = {}, y = {}'.format(str(self._x), str(self._y))


class Ship:
    '''
    Purpose: Keeps track of relevant info about one ship (i.e. size, placement,
                 how many more hits it can take before sinking).
    Parameters: ship_placement_info_line, a str. Contains info about the ship
                    and its placement on the board
                correct_ship_sizes, a dict. Keys are all possible ship-types.
                    Values are corresponding sizes
    '''
    def __init__(self, ship_placement_info_line, correct_ship_sizes):
        self._grid_positions_occupied = []
        self._ship_placement_info_line = ship_placement_info_line
        ship_placement_info_list = ship_placement_info_line.split()
        self._ship_type = ship_placement_info_list[0]

        self._x1 = int(ship_placement_info_list[1])
        self._y1 = int(ship_placement_info_list[2])
        self._x2 = int(ship_placement_info_list[3])
        self._y2 = int(ship_placement_info_list[4])

        x_coords = {self._x1, self._x2}
        y_coords = {self._y1, self._y2}

        # making sure all coordinates actually on grid 
        all_coords = x_coords.union(y_coords)
        min_coord, max_coord = min(all_coords), max(all_coords)
        if (min_coord < 0 or max_coord > 9):
            print('ERROR: ship out-of-bounds: ' + ship_placement_info_line)
            sys.exit(1)
                 
        # auxillary variables
        self._x_min = min(x_coords)
        self._x_max = max(x_coords)
        self._y_min = min(y_coords)
        self._y_max = max(y_coords)

        dx = self._x_max - self._x_min
        dy = self._y_max - self._y_min

        # determining ship size and orientation
        if dx == 0 and dy > 0:
            self._orientation = 'vert'
            self._ship_size = dy + 1
        elif dy == 0:
            self._orientation = 'horz'
            self._ship_size = dx + 1
        else:
            print('ERROR: ship not horizontal or vertical: ' + \
                  ship_placement_info_line)
            sys.exit(1)

        # making sure ship-size is correct
        if self._ship_size != correct_ship_sizes[self._ship_type]:
            print('ERROR: incorrect ship size: ' + \
                  ship_placement_info_line)
            sys.exit(1)
        
        self._num_spots_not_yet_hit = self._ship_size


    # getters
    def get_ship_type(self):
        return self._ship_type
    
    def get_coords(self):
        return self._x_min, self._x_max, self._y_min, self._y_max

    def get_orientation(self):
        return self._orientation

    def get_num_spots_not_yet_hit(self):
        return self._num_spots_not_yet_hit


    # setters
    def set_grid_positions_occupied(self, list_of_grid_pos_objects):
        self._grid_positions_occupied = list_of_grid_pos_objects

    def indicate_ship_hit(self):
        self._num_spots_not_yet_hit -= 1
        
    def __str__(self):
        return self._ship_placement_info_line


def main():
    board = Board()
    board.process_ship_placement_file()
    board.process_guesses_file()


main()
