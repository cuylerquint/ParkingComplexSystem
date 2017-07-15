# -*- coding: utf-8 -*-
"""
Tests module:
  Defines Tests class and tests Classes and park_unpark modules

"""

from park_unpark import *
import park_unpark
import unittest
import time
import datetime


class Tests(unittest.TestCase):

    def test_invalid_park_input(self):
        print "\n\n\nTest: invalid park input"
        print "*" * 145

        park_unpark.init()
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.park, 12, "nonboolean")
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.park, "compact_car", "nonbool")
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.park, "eletric_car", True)

    def test_invalid_unpark_input(self):
        print "\n\n\nTest: invalid unpark input"
        print "*" * 145

        park_unpark.init()
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, [1])
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, ("str", True, 1))
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, (-2, 0, -1))
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, (23, 1, 2))
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, (1, 14, 3))
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, (1, 1, 45))
        self.assertRaises(park_unpark.InvalidInputError, park_unpark.unpark, (1, 1, 1))

    def test_valid_park_unpark_output(self):
        print "\n\n\nTest: park unpark output"
        print "*" * 145

        # park return None
        park_unpark.init()
        for n in range(0, 220):
            location = park_unpark.park('compact_car', True)
        self.assertEqual(park_unpark.park('compact_car', True), None)

        # park return Tuple
        park_unpark.init()
        self.assertEqual(isinstance(park_unpark.park('compact_car', True), tuple), True)

        # park return float
        park_unpark.init()
        p = park_unpark.park('compact_car', True)
        self.assertEqual(isinstance(park_unpark.unpark(p), float), True)

    def test_first_park_unpark(self):
        print "\n\n\nTest: basic park unpark"
        print "*" * 145

        park_unpark.init()
        first_handicap_location = park_unpark.park('compact_car', True)
        first_handicap_rate = park_unpark.unpark(first_handicap_location)
        self.assertEqual(first_handicap_location, (1, 1, 1))
        self.assertEqual(first_handicap_rate, first_handicap_rate)

        first_compact_nonhandicap_location = park_unpark.park('compact_car', False)
        first_compact_nonhandicap_rate = park_unpark.unpark(first_compact_nonhandicap_location)
        self.assertEqual(first_compact_nonhandicap_location, (2, 1, 1))
        self.assertEqual(first_compact_nonhandicap_rate, 5)

        first_large_location = park_unpark.park('large_car', False)
        first_large_rate = park_unpark.unpark(first_large_location)
        self.assertEqual(first_large_location, (2, 5, 1))
        self.assertEqual(first_large_rate, 7.5)

    def test_spot_availble(self):
        print "\n\n\nTest: spot available"
        print "*" * 145

        # full complex
        park_unpark.init()
        for n in range(0, 220):
            location = park_unpark.park('compact_car', True)
        self.assertEqual(park_unpark.parking_complex.spot_available("compact_car", True), False)

        # test handicap and large
        park_unpark.init()
        for n in range(0, 20):
            location = park_unpark.park('large_car', True)
        for n in range(0, 80):
            location = park_unpark.park('large_car', False)
        self.assertEqual(park_unpark.parking_complex.spot_available("large_car", True), False)

        # test compact non-handicap
        park_unpark.init()
        for n in range(0, 200):
            location = park_unpark.park('compact_car', False)
        self.assertEqual(park_unpark.parking_complex.spot_available("compact_car", False), False)

        # test large non-handicap
        park_unpark.init()
        for n in range(0, 80):
            location = park_unpark.park('large_car', False)
        self.assertEqual(park_unpark.parking_complex.spot_available("large_car", False), False)

    def test_best_spot(self):
        print "\n\n\nTest: best spot"
        print "*" * 145

        # mixture of parking
        park_unpark.init()
        for n in range(0, 19):
            park_unpark.park('compact_car', True)
            park_unpark.park('compact_car', False)
            park_unpark.park('large_car', False)

        best_handicap_t = (park_unpark.parking_complex.best_spots[0].location.level,
                      park_unpark.parking_complex.best_spots[0].location.row,
                      park_unpark.parking_complex.best_spots[0].location.space)
        self.assertEqual(best_handicap_t, (1, 2, 10))

        best_compact_t = (park_unpark.parking_complex.best_spots[1].location.level,
                      park_unpark.parking_complex.best_spots[1].location.row,
                      park_unpark.parking_complex.best_spots[1].location.space)
        self.assertEqual(best_compact_t, (3, 1, 3))

        best_large_t = (park_unpark.parking_complex.best_spots[2].location.level,
                      park_unpark.parking_complex.best_spots[2].location.row,
                      park_unpark.parking_complex.best_spots[2].location.space)
        self.assertEqual(best_large_t, (2, 8, 2))

    def test_valid_rate_chargeing(self):
        print "\n\n\nTest: valid rate chargeing"
        print "*" * 145

        # handicap minmum
        park_unpark.init()
        p = park_unpark.park('compact_car', True)
        park_unpark.unpark(p)
        self.assertEqual(park_unpark.parking_complex.tickets[0].charge, 5)

        # compact minmum
        park_unpark.init()
        p = park_unpark.park('compact_car', False)
        park_unpark.unpark(p)
        self.assertEqual(park_unpark.parking_complex.tickets[0].charge, 5)

        # large minmum
        park_unpark.init()
        p = park_unpark.park('large_car', False)
        park_unpark.unpark(p)
        self.assertEqual(park_unpark.parking_complex.tickets[0].charge, 7.5)

        # compact in large
        park_unpark.init()
        for n in range(0, 121):
            p = park_unpark.park('compact_car', False)
        park_unpark.parking_complex.tickets[120].close()
        self.assertEqual(park_unpark.parking_complex.tickets[120].charge, 7.5)

        # handicap in large
        park_unpark.init()
        for n in range(0, 21):
            p = park_unpark.park('large_car', True)
        park_unpark.parking_complex.tickets[20].close()
        self.assertEqual(park_unpark.parking_complex.tickets[20].charge, 5)

        # handicap day charge
        park_unpark.init()
        p = park_unpark.park('large_car', True)
        future_date = park_unpark.parking_complex.tickets[0].start_t
        future_date += datetime.timedelta(days=1)
        park_unpark.parking_complex.tickets[0].end_t = future_date
        park_unpark.parking_complex.tickets[0].set_charge()
        self.assertEqual(park_unpark.parking_complex.tickets[0].charge, 480)

        # large non handicap day charge
        park_unpark.init()
        p = park_unpark.park('large_car', False)
        future_date = park_unpark.parking_complex.tickets[0].start_t
        future_date += datetime.timedelta(days=1)
        park_unpark.parking_complex.tickets[0].end_t = future_date
        park_unpark.parking_complex.tickets[0].set_charge()
        self.assertEqual(park_unpark.parking_complex.tickets[0].charge, 720)
        
if __name__ == '__main__':
    unittest.main()
