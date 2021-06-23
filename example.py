from typing import Callable, List

import pymunk

from simulation import main
from tools import *

# import programs from other files
import examples.own  # isort:skip
import examples.opponent  # isort:skip

# config
CONFIG = {
    "ATK_AUTO_DRIBBLE": True,  # True for attack robot to dribble ball when it comes near
    "DEF_AUTO_DRIBBLE": True,  # True for defence robot to dribble ball when it comes near
    "O_ATK_AUTO_DRIBBLE": True,  # True for opponent attack robot to dribble ball when it comes near
    "O_DEF_AUTO_DRIBBLE": False,  # True for opponent defence robot to dribble ball when it comes near
}


# user programs
def out(robot: Robot, line: pymunk.Vec2d) -> None:
    """Makes the robot move away from the line and into the field.

    Args:
        robot: A Robot object to be moved and which has detected the lines.
        line: A pymunk.Vec2d object representing average direction of lines detected (from line()).
    """

    # sets the robot to move in whichever direction the TOFs detect is further away from the wall
    resultant = pymunk.Vec2d(
        0
        if line.x == 0
        else abs(line.x)
        if (robot.TOFReadings[1] > robot.TOFReadings[3] and robot.TOFReadings[3] < 120)
        or robot.TOFReadings[1] > 120
        else -abs(line.x),
        0
        if line.y == 0
        else abs(line.y)
        if robot.TOFReadings[0] > robot.TOFReadings[2]
        else -abs(line.y),
    )
    if resultant != pymunk.Vec2d(0, 0):
        robot.move(450, vec_to_world(resultant))


# the programs have been moved to separate files in the /examples for clarity


if __name__ == "__main__":
    main(
        CONFIG,
        examples.own.attack,
        examples.own.defend,
        examples.opponent.o_attack,
        examples.opponent.o_defend,
    )
