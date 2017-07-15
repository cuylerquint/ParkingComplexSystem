# -*- coding: utf-8 -*-
"""
Classes module:
  Defines objects and backend that integrates with park_unpark

  Notes:  please view readme.md for design assumptions

"""
from park_unpark import *
import park_unpark
from datetime import datetime
from operator import attrgetter
import copy
import threading


class ParkingComplex():
    """
    Defines a ParkingComplex instance

    Args:
        config_text_path(str): path to config text file, default is redwood.txt in project

    Attributes:
        name (str): Name of the parking complex
        levels(list): contains a list of ParkingComplexLevel objects
        handicap_spots(list): contains a list of the currently open handicapped parking spots
        compact_spots(list): contains a list of the currently open compact parking spots
        large_spots(list): contains a list of the currently open large parking spots
        tickets(list): contains a list of all tickets that have been processed by this parking complex
        ticket_map(list): contains a list of ParkingComplexLevel objects
        ticket_count(int): ticket ID counter
        best_spots(list): holes
        resource_lock(threading.Lock): locking access to shared resources during critical sections

    """
    def __init__(self, config_text_path):
        self.name = None
        self.levels = []
        self.handicap_spots = []
        self.compact_spots = []
        self.large_spots = []
        self.tickets = []
        self.ticket_map = None
        self.ticket_count = 0
        self.best_spots = [None, None, None]
        self.resource_lock = threading.Lock()
        self.init_system_from_text(config_text_path)
        self.set_ticket_matrix()
        self.update_best_spots()

    def init_system_from_text(self, file_path):
        """
        Utility function that updates size spot lists with parking spots on the given level
        """
        lines = [line.rstrip('\n') for line in open(file_path)]
        name_levels_tup = lines[0].split(",")
        self.name = name_levels_tup[0]
        num_levels = name_levels_tup[1]
        row_space_index = 0
        for n in range(0, int(num_levels)):
            row_space_index = row_space_index + 1
            row_space_line = lines[row_space_index]
            row_space_tuple = tuple(row_space_line.split(','))
            rows = row_space_tuple[0]
            spaces = row_space_tuple[1]
            total_level_spaces = int(rows) * int(spaces)
            space_type_array = []
            for i in range(0, total_level_spaces):
                temp_index = row_space_index + i + 1
                space_type_array.append(lines[temp_index])
            level = int(n) + 1
            temp_level = ParkingComplexLevel(level, int(rows), int(spaces), space_type_array)
            self.update_spot_lists(temp_level)
            self.levels.append(temp_level)
            row_space_index = row_space_index + total_level_spaces

    def update_spot_lists(self, level):
        """
        Utility function that updates size spot lists with parking spots on the given level

        Args:
            level(ParkingComplexLevel): level to add parking spots from
        """
        for i in range(0, level.rows):
            for j in range(0, level.spaces):
                if(level.level_matrix[i][j].size_t == "handicap"):
                    self.handicap_spots.append(level.level_matrix[i][j])
                elif(level.level_matrix[i][j].size_t == "compact"):
                    self.compact_spots.append(level.level_matrix[i][j])
                elif(level.level_matrix[i][j].size_t == "large"):
                    self.large_spots.append(level.level_matrix[i][j])

    def update_best_spots(self):
        """
        Utility function that updates self.best_spots list to the next closet spot based off size

        Note: this funciton changes a shared resouce and exists in a crital section
        """
        h_full = all(spot.filled == True for spot in self.handicap_spots)
        c_full = all(spot.filled == True for spot in self.compact_spots)
        l_full = all(spot.filled == True for spot in self.large_spots)
        if(not h_full):
            self.best_spots[0] = self.get_closest_by_size("handicap")
        elif(not c_full):
            self.best_spots[0] = self.get_closest_by_size("compact")
        elif(not l_full):
            self.best_spots[0] = self.get_closest_by_size("large")
        else:
            self.best_spots[0] = None
        if(not c_full):
            self.best_spots[1] = self.get_closest_by_size("compact")
        elif(not l_full):
            self.best_spots[1] = self.get_closest_by_size("large")
        else:
            self.best_spots[1] = None
        if(not l_full):
            self.best_spots[2] = self.get_closest_by_size("large")
        else:
            self.best_spots[2] = None

    def get_closest_by_size(self, size):
        """
        Utility funtion to get the closest parking spot to entrance by size

        Args:
            size(str): size type
        """
        if size == "handicap":
            temp_list = self.handicap_spots
        elif size == "compact":
            temp_list = self.compact_spots
        else:
            temp_list = self.large_spots
        closest_spot = min(temp_list, key=attrgetter('distance_to_entrance'))
        return closest_spot

    def set_ticket_matrix(self):
        """
        Utility funtion to set self.ticket_map
        """
        self.ticket_map = copy.deepcopy(self.levels)
        for level in self.ticket_map:
            for i in range(0, level.rows):
                for j in range(0, level.spaces):
                    level.level_matrix[i][j] = None

    def spot_available(self, size, handicapped):
        """
        Utility funtion to display a unpark transaction

        Args:
            size(str): size type to be parked
            handicapped(bool): boolean of customer hanicapped privileges

        Returns:
            bool: a spot exists for this size and handicap privilege
        """
        h_full = all(spot.filled == True for spot in self.handicap_spots)
        c_full = all(spot.filled == True for spot in self.compact_spots)
        l_full = all(spot.filled == True for spot in self.large_spots)
        if h_full and c_full and l_full:
            return False
        if handicapped and size == "large_car" and h_full and l_full:
            return False
        if not handicapped and size == "compact_car" and c_full and l_full:
            return False
        if not handicapped and size == "large_car" and l_full:
            return False
        return True

    def get_best_spot(self, customer):
        """
        Utility funtion to display a unpark transaction

        Args:
            customer(Customer): the customer that needs a spot

        Returns:
            ParkingSpot object from self.best_spots list
        """
        if customer.handicapped:
            if customer.size == "large_car" and all(spot.filled == True for spot in self.handicap_spots):
                return self.best_spots[2]
            else:
                return self.best_spots[0]
        elif customer.size == "compact_car":
            return self.best_spots[1]
        else:
            return self.best_spots[2]

    def update_matrixs(self, ticket, parking):
        """
        Utility/Delegation function updates self.levels and self.ticket_map states with the given then displays

        Note: this funciton changes a shared resouce and exists in a crital section

        Args:
            ticket(Ticket): ticket to update matrixs with
            parking(bool): boolean of customer parking versus unparking
        """
        if parking:
            self.ticket_map[ticket.p_spot.location.level - 1].level_matrix[ticket.p_spot.location.row - 1][ticket.p_spot.location.space - 1] = ticket
            self.levels[ticket.p_spot.location.level - 1].level_matrix[ticket.p_spot.location.row - 1][ticket.p_spot.location.space - 1].filled = True
            if(ticket.p_spot.size_t == "handicap"):
                self.handicap_spots.remove(ticket.p_spot)
            elif(ticket.p_spot.size_t == "compact"):
                self.compact_spots.remove(ticket.p_spot)
            else:
                self.large_spots.remove(ticket.p_spot)
            self.display_park(ticket)
        else:
            self.ticket_map[ticket.p_spot.location.level - 1].level_matrix[ticket.p_spot.location.row - 1][ticket.p_spot.location.space - 1] = None
            self.levels[ticket.p_spot.location.level - 1].level_matrix[ticket.p_spot.location.row - 1][ticket.p_spot.location.space - 1].filled = False
            if(ticket.p_spot.size_t == "handicap"):
                self.handicap_spots.append(ticket.p_spot)
            elif(ticket.p_spot.size_t == "compact"):
                self.compact_spots.append(ticket.p_spot)
            else:
                self.large_spots.append(ticket.p_spot)
            self.display_unpark(ticket)

    def display_park(self, ticket):
        """
        Utility funtion to display a park transaction

        Args:
            ticket(Ticket): ticket to display
        """
        print "\n\n\n\nPark:"
        print "-"*148
        print "Welcome to the " + park_unpark.parking_complex.name + " Parking Complex"
        print "Here are your ticket details:\n"
        print "\tTicket ID:\t\t", ticket.id
        print "\tDetected Car Size:\t", ticket.customer.size
        print "\tStart Time:\t\t", ticket.start_t
        print "\tLocation:\t\tLevel:" + str(ticket.p_spot.location.level) + "   Row:" + str(ticket.p_spot.location.row) + "   Space:" + str(ticket.p_spot.location.space)
        print "\n\tLocate 'Park' in the complex map below for directions to your given spot"
        for level in self.ticket_map:
            print "\n\n\nLevel", level.level
            for n in range(0, level.spaces): print "S" + str(n+1), "\t\t",
            print "\n"
            for i in range(0, level.rows):
                print "\nR" + str(i + 1),
                for j in range(0, level.spaces):
                    if level.level_matrix[i][j] == ticket:
                        print "Park\t\t",
                    elif level.level_matrix[i][j] != None:
                        print str(level.level_matrix[i][j].description) + "\t\t",
                    else:
                        print "0\t\t",

    def display_unpark(self, ticket):
        """
        Utility funtion to display a unpark transaction

        Args:
            ticket(Ticket): ticket to display
        """
        print "\n\n\n\nUnpark:"
        print "-"*145
        print "Thank for parking at Lastline's " + park_unpark.parking_complex.name + " Complex"
        print "Here is your receipt Details:\n"
        print "\tTicket ID:\t\t", ticket.id
        print "\tDetected Car Size:\t", ticket.customer.size
        print "\tStart Time:\t\t", ticket.start_t
        print "\tFinish Time:\t\t", ticket.end_t
        m, s = divmod(ticket.delta_t, 60)
        h, m = divmod(m, 60)
        print "\tElapsed Time:\t\t%d:%02d:%02d" % (h, m, s)
        print "\tCharge Due:\t\t", ticket.format_charge()
        print "\n\tHave a good day!"
        for level in self.ticket_map:
            print "\n\n\nLevel", level.level
            for n in range(0, level.spaces): print "S" + str(n+1), "\t\t",
            print "\n"
            for i in range(0, level.rows):
                print "\nR" + str(i + 1),
                for j in range(0, level.spaces):
                    if level.level == ticket.p_spot.location.level and i == ticket.p_spot.location.row - 1 and j == ticket.p_spot.location.space - 1:
                        print "unparking\t",
                    elif level.level_matrix[i][j] != None:
                        print str(level.level_matrix[i][j].description) + "\t\t",
                    else:
                        print "0\t\t",

    def park_customer(self, size, handicapped):
        """
        Utility funtion to park a customer for a given size and handicap privilege

        Args:
            size(str): size type to be parked
            handicapped(bool): boolean of customer hanicapped privileges

        Returns:
            tuple(int,int,int): location of where to park customer
            or
            None: no spots available

        Returns:
            ticket.charge(float): the customers fee for parking
        """
        if(self.spot_available(size, handicapped)):
            self.ticket_count += 1
            new_customer = Customer(size, handicapped)
            best_spot = self.get_best_spot(new_customer)
            new_ticket = Ticket(best_spot, new_customer, self.ticket_count)
            self.tickets.append(new_ticket)
            self.resource_lock.acquire()
            self.update_matrixs(new_ticket, True)
            self.update_best_spots()
            self.resource_lock.release()
            return (int(best_spot.location.level), int(best_spot.location.row), int(best_spot.location.space))
        else:
            return None

    def unpark_customer(self, location):
        """
        Utility funtion to unpark a customer from a given location

        Args:
            location(tuple): contains the indexs of where to unpark a customer

        Returns:
            ticket.charge(float): the customers fee for parking
        """
        for level in self.ticket_map:
            for i in range(0, level.rows):
                for j in range(0, level.spaces):
                    if level.level_matrix[i][j] != None:
                        if(level.level == location[0] and level.level_matrix[i][j].p_spot.location.row == location[1] and level.level_matrix[i][j].p_spot.location.space == location[2]):
                            ticket = level.level_matrix[i][j]
        ticket.close()
    	self.resource_lock.acquire()
        self.update_matrixs(ticket, False)
        self.update_best_spots()
        self.resource_lock.release()
        return ticket.charge

    def check_park_input(self, size, handicapped):
        """
        Utility funtion to parse input given to park_park.unpark input for invalid exceptions

        Args:
            size(str): size type to be parked
            handicapped(bool): boolean of customer hanicapped privileges

        Returns:
            tuple:(bool:Valid input,str:exception detail)
        """
        if type(size) is not str:
            return (True, "Given 'size' parameter not of Type: Str")
        if type(handicapped) is not bool:
            return (True, "Given 'has_handicapped_placard' parameter not of Type: Bool")
        if(size not in ['compact_car', 'large_car']):
            return (True, "Given 'size' parameter not a defined as a option")
        return (False, None)

    def check_unpark_input(self, location):
        """
        Utility funtion to parse input given to park_unpark.unpark for invalid exceptions

        Args:
            location(tuple): contains the indexs of where to unpark a customer

        Returns:
            tuple:(bool:Valid input,str:exception detail)
        """
        if type(location) is not tuple:
            return (True, "Given 'location' parameter not of type: Tuple")
        if type(location[0]) is not int or type(location[1]) is not int or type(location[2]) is not int:
            return (True, "Given 'location' parameter tuple index's not of type: Int")
        if location[0] < 1 or location[1] < 1 or location[2] < 1:
            return (True, "Given 'location' parameter has a index below bounds")
        if location[0] > len(self.levels):
            return (True, "Given 'location' parameter level index above bounds")
        for level in self.levels:
            if location[1] > level.rows:
                return (True, "Given 'location' parameter row index above bounds")
            if location[2] > level.spaces:
                return (True, "Given 'location' parameter space index above bounds")
        if self.levels[location[0]-1].level_matrix[location[1]-1][location[2]-1].filled == False:
            return (True, "Given 'location' parameter is empty")
        return (False, None)


class ParkingComplexLevel():
    """
    Defines a ParkingComplexLevel instance inside of a ParkingComplex class

    Args:
        level(int): level number inside of parking complex
        rows(int): number of rows this level has
        spaces(int): number of rows this level has
        space_types(list): contains the type of each space for level matrix
            options:["handicap","compact","large"]

    Attributes:
        level(int): level number inside of parking complex
        rows(int): number of rows this level has
        spaces(int): number of rows this level has
        level_matrix([ParkingSpot][ParkingSpot]): matrix containg a ParkingSpot object at each index

    """
    def __init__(self, level, rows, spaces, space_types):
        self.level = level
        self.rows = rows
        self.spaces = spaces
        self.level_matrix = [[0 for i in range(spaces)] for i in xrange(rows)]
        self.set_level_matrix(space_types)

    def set_level_matrix(self, space_types):
        """
        Utility funtion to set self.level_matrix with ParkingSpot objects

        Args:
            spaces(int): number of rows this level has
        """
        for i in range(0, self.rows):
            for j in range(0, self.spaces):
                temp_location = Location(self.level, i+1, j+1)
                p_type = space_types[int(str(i) + str(j))]
                temp_p_spot = ParkingSpot(p_type, temp_location)
                self.level_matrix[i][j] = temp_p_spot


class Location():
    """
    Defines a Location instance inside of a ParkingSpot class

    Args:
        level(int): level number of this location
        row(int): row number of this location
        space(int): space number of this location

    Attributes:
        level(int): level number of this location
        row(int): row number of this location
        space(int): space number of this location

    """
    def __init__(self, level, row, space):
        self.level = level
        self.row = row
        self.space = space


class ParkingSpot():
    """
    Defines a ParkingSpot instance inside of a ParkingComplexLevel class

    Args:
        size_t(str): the size of the parking spot
            options:["handicap","compact","large"]
        location(Location): location of this parking spot in the complex

    Attributes:
        size_t(str): the size of the parking spot
            options:["handicap","compact","large"]
        location(Location): location of this parking spot in the complex
        filled(bool): boolean of parking spot being empty
        distance_to_entrance(int): the travel distance in complex from entrance to this parking spot
            Note: the distance is calculated logically by assumption of entrance location(1,1,1),
                    see readme.md for more details

    """
    def __init__(self, size_t, location):
        self.size_t = size_t
        self.location = location
        self.filled = False
        self.distance_to_entrance = 0
        self.set_distance_to_entrance()

    def set_distance_to_entrance(self):
        """
        Utility funtion to set self.distance_to_entrance
        """
        self.distance_to_entrance = self.location.level + self.location.row + self.location.space


class Customer():
    """
    Defines a ParkingSpot instance inside of a ParkingComplexLevel class

    Args:
        size(str): the size of the parking spot
            options:["compact_car","large_car"]
        handicapped(bool): boolean of customer handicapped privileges

    Attributes:
       size(str): the size of the parking spot
            options:["compact_car","large_car"]
        handicapped(bool): boolean of customer handicapped privileges

    """

    def __init__(self, size, handicapped):
        self.size = size
        self.handicapped = handicapped


class Ticket():
    """
    Defines a ParkingSpot instance inside of a ParkingComplexLevel class

    Args:
        p_spot(ParkingSpot): parking spot associated with this ticket
        customer(Customer): customer associated with this ticket
        id(int): ticket id number in this complex

    Attributes:
        p_spot(ParkingSpot): parking spot associated with this ticket
        customer(Customer): customer associated with this ticket
        id(int): ticket id number in this complex
        start_t(datetime): date of when this car parked
        end_t(datetime): date of when this car unparked
        delta_t(datetime.delta): elapsed time of self.start_t to self.end_t
        description(str): string to denoted a value in printed map
        charge(float): amount charged for park time
    """
    def __init__(self, p_spot, customer, id):
        self.p_spot = p_spot
        self.customer = customer
        self.id = id
        self.start_t = None
        self.end_t = None
        self.delta_t = None
        self.description = None
        self.charge = None
        self.set_start_t()
        self.set_description()

    def set_start_t(self):
        """
        Utility funtion to set self.start_t
        """
        self.start_t = datetime.now()

    def set_end_t(self):
        """
        Utility funtion to set self.end_t
        """
        self.end_t = datetime.now()

    def set_delta_t(self):
        """
        Utility funtion to set self.delta_t
        """
        self.delta_t = self.end_t - self.start_t
        self.delta_t = self.delta_t.total_seconds()

    def set_description(self):
        """
        Utility funtion to set description
        """
        if self.customer.handicapped and self.customer.size == "compact_car":
            d = "HC"
        elif self.customer.handicapped and self.customer.size == "large_car":
            d = "LHC"
        elif self.customer.size == "compact_car":
            d = "COM"
        elif self.customer.size == "large_car":
            d = "LAR"
        self.description = d

    def set_charge(self):
        """
        Utility/Delegation funtion to set self.delta_t and determind the rate then set self.charge
        """
        if(self.customer.handicapped or self.p_spot.size_t == "compact"):
            rate = 5.00
        else:
            rate = 7.50
        self.set_delta_t()
        if self.delta_t < park_unpark.MINIMUM_PARKING_INTERVAL_SECONDS:
            self.charge = rate
        else:
            intervals = self.get_intervals()
            self.set_rounded_charge(rate, intervals)

    def get_intervals(self):
        """
        Utility funtion to get the amount of rouned up 15 min intervals in self.delta_t
        """
        mins, s = divmod(self.delta_t, 60)
        return int((mins / 15) + (mins % 15 > 0))

    def set_rounded_charge(self, rate, intervals):
        """
        Utility funtion to set the total charge on ticket

        Args:
            rate(int): rate per hour of this ticket
            intervals(int): amount of 15 min intervals inside of self.delta_t
        """
        total = rate * intervals
        self.charge = float(round(total, 2))

    def close(self):
        """
        Delegation funtion to close a ticket by setting self.end_t and self.charge
        """
        self.set_end_t()
        self.set_charge()

    def format_charge(self):
        """
        Utility funtion to print self.charge in USD
        """
        print "${:.2f}".format(self.charge)
