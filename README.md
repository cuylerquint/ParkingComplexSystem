# Parking Complex System

This code base is a solution to the task defined in *ParkingChallenge.txt*.
Before continuing please review the *ParkingChallenge.txt* to understand
the problem statement.

## Design/Assumptions
- Time definitions for customer tickets are stamped on call to park and unpark granted their parameters are valid
 

- init() is called once per park_unpark module process

- Entrance Location/ Best Spot:<br />
  The distance between the entrance is derived as a combination of the indexes in
  a location tuple.<br />

  E.G.  location(1,1,1).distance-to-entrance -> 3<br />
        location(2,1,1).distance-to-entrance -> 4<br />
        location(3,1,1).distance-to-entrance -> 5<br />
        ...

  With this design the cost to go in any direction is solely 1<br />
  E.g.<br />
  First compact non-handicapped level 1 resides at location(1,3,1).dis -> 5<br />
  First compact non-handicapped level 2 resides at location(2,1,1).dis -> 4

- Assumption: travel between spots and entrance/exit is not accounted for in this
  design

- Complex generation from text file:
  This design is dependent on a config text file to denote the size/type of parking
  rows and spaces as seen in *ParkingChallenge.txt*.  This backend is will parse
  a text in the following format a make a ParkingComplex with the values denoted. <br />
  config-text-path proper format: <br />
  * first-line:(Str):'ParkingComplex Name',(Int): Number of levels wanted
  * for level-line in range(0,first-line[1]):
     * next-line = (Int):level-line-rows,(Int):level-line-spaces 
         * for parking-space in range(0,row-space-line[0] * rows-space-line[1]) 
             * next_line = (Str): Type of parking space at level[i][j] #this is limitedto["handicap","compact","large"]

  e.g. : redwood.txt: <br />
  Redwood,3 # complex name = redwood, levels = 3 <br />
  6,10      # rows = 6, spaces = 10 ,level_line 1 of 3 <br />
  handicap  # parking space line 1 of 60 <br />
  handicap  # parking space line 2 of 60 <br />
  ...<br />
  compact   # parking space line 60 of 60<br />
  8,10      # rows = 8, spaces = 10, level-line 2 of 3<br />
  compact   # parking space line 1 of 80<br />


## Running
  Currently this is only configured to run from the Tests.py which utilizes the unittest module

  to run:
  python Tests.py

## Improvements
- Use a actual Database to store information about customers and complex
## Author
- **Cuyler Quint** - [cuylerquint](https://github.com/cuylerquint)
