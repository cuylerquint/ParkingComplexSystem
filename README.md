# Parking Complex System

This code base is a solution to the task defined in *ParkingChallenge.txt*.
Before continuing please review the *ParkingChallenge.txt* to understand
the problem statement.

## Design/Assumptions
- Time definitions for customer tickets are stamped on call to park and unpark granted
there parameters are valid

- init() is called once per park_unpark module process

- Entrance Location/ Best Spot:
  The distance between the entrance is derived as a combination of the indexes in
  a location tuple.
  E.G.  location(1,1,1).distance_to_entrance -> 3
        location(2,1,1).distance_to_entrance -> 4
        location(3,1,1).distance_to_entrance -> 5
        ...

  With this design the cost to go in any direction is solely 1.
  E.g.
  First compact non-handicapped level 1 resides at location(1,3,1).dis -> 5
  First compact non-handicapped level 2 resides at location(2,1,1).dis -> 4

- Assumption: travel between spots and entrance/exit is not accounted for in this
  design

- Complex generation from text file:
  This design is dependent on a config text file to denote the size/type of parking
  rows and spaces as seen in *ParkingChallenge.txt*.  This backend is will parse
  a text in the following format a make a ParkingComplex with the values denoted.
  config_text_path proper format:
  line 1:(Str):'ParkingComplex Name',(Int): Number of levels wanted
  for level_line in range(0,line1[1]):
  next_line = (Int):level_line_rows,(Int):level_line_spaces
  for parking_space in range(0,row_space_line[0] * rows_space_line[1])
  next_line = (Str): Type of parking space at level[i][j] #this is limited to ["handicap","compact","large"]

  e.g. redwood.txt:
  Redwood,3 # complex name = redwood, levels = 3
  6,10      # rows = 6, spaces = 10 ,level_line 1 of 3
  handicap  # parking space line 1 of 60
  handicap  # parking space line 2 of 60
  ...
  compact   # parking space line 60 of 60
  8,10      # rows = 8, spaces = 10, level_line 2 of 3
  compact   # parking space line 1 of 80


## Running
  currently this is only configured to run from the Tests.py which
  utilizes the build in unittest module

  to run:
  python Tests.py

## Improvements
- Use a actual Database to store information about customers and complex
## Authors

- **Cuyler Quint** - [cuylerquint](https://github.com/cuylerquint)


======================
