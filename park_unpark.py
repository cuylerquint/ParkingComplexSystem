# -*- coding: utf-8 -*-
"""
park_unpark module:
  entry point for Tests module

  Notes: this what the only file given in challege missing function/class bodys

"""
from Classes import *
import os, sys

#given global
MINIMUM_PARKING_INTERVAL_SECONDS = 15*60
#global complex for access across modules
global parking_complex


class InvalidInputError(Exception):
    """
    Raised if the provided API input is invalid.

    Args:
        args(tuple(*args)): a tuple of parameters geiven to said function
        funciton(str): function name that rasied exception
        detail(str): detail into why a exception was thrown

    Attributes:
        args(tuple(*args)): a tuple of parameters geiven to said function
        funciton(str): function name that rasied exception
        detail(str): detail into why a exception was thrown
    """
    def __init__(self, args, function, detail):
        self.args = args
        self.function = function
        self.detail = detail
        self.print_exception()

    def print_exception(self):
        """
        Utility function that updates size spot lists with parking spots on the given level
        """
        print "\nInvalidInputError: {}() : {} : Parameter given : {}".format(self.function, self.detail, self.args)


def park(size, has_handicapped_placard):
    """ **** Given Doc String ****
    Return the most appropriate available parking space for this vehicle. Refer to
    challenge description for explanation of how to determine the most appropriate space

    :param size: vehicle size. For now this is 'compact_car' or 'large_car'
    :type size: `str`
    :param has_handicapped_placard: if True, provide handicapped space (if available)
    :type has_handicapped_placard: `bool`
    :returns: parking location. tuple of (level, row, space), or None if no spaces available.
       Level, row and space numbers start at 1.
    :rtype: tuple(`int`,`int`,`int`)
    :raises InvalidInputError: if size invalid
    """
    input_parse = parking_complex.check_park_input(size, has_handicapped_placard)
    if(input_parse[0]):
        raise InvalidInputError((size, has_handicapped_placard), sys._getframe().f_code.co_name, input_parse[1])
    else:
        return parking_complex.park_customer(size, has_handicapped_placard)


def unpark(location):
    """ **** Given Doc String ****
    Return the charge for parking at this location based on location type and time spent.
    Refer to challenge description for details on how to calculate parking rates.

    :param location: parking space the vecicle was parked at as tuple (level, row, space)
    :type location: tuple(`int`,`int`,`int`)
    :returns: The total amount that the parker should be charged (eg: 7.5)
    :rtype: float
    :raises InvalidInputError: if location invalid or empty
    """
    input_parse = parking_complex.check_unpark_input(location)
    if(input_parse[0]):
        raise InvalidInputError(location, sys._getframe().f_code.co_name, input_parse[1])
    else:
        return parking_complex.unpark_customer(location)


def init():
    """ **** Given Doc String ****
    Called on system initialization before any park/unpark function is called.
    """
    global parking_complex
    parking_complex = ParkingComplex(os.path.abspath("redwood.txt"))
