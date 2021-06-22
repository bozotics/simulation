from typing import Callable, List

import pymunk

from simulation import main
from tools import *

# config
CONFIG = {
    "ATK_AUTO_DRIBBLE": False,  # True for attack robot to dribble ball when it comes near
    "DEF_AUTO_DRIBBLE": False,  # True for defence robot to dribble ball when it comes near
    "O_ATK_AUTO_DRIBBLE": False,  # True for opponent attack robot to dribble ball when it comes near
    "O_DEF_AUTO_DRIBBLE": False,  # True for opponent defence robot to dribble ball when it comes near
}


# user programs
def attack(
    robots: List[Robot],
    detectLine: Callable[[Robot], pymunk.Vec2d],
    ballPosition: pymunk.Vec2d,
    robotPositions: List[pymunk.Vec2d],
    dribble: Callable[[Robot], None],
    kick: Callable[[Robot], None],
) -> None:
    """Program and logic for own attacking robot.

    Args:
        robots: A list of both Robots for own side.
        detectLine: Function returning a pymunk.Vec2d vector representing
            average **direction** of lines detected by robot passed as argument.
        ballPosition: pymunk.Vec2d object representing world coordinate position of ball.
        robotPositions: List of pymunk.Vec2d objects each representing the world coordinate position of a robot,
            in order [own attack robot, own defense robot, opponent attack robot, opponent defense robot].
        dribble: Function to dribble the ball (and sets robot.dribbleState)
        kick: Function to kick the ball in the front catchment area (if any).
    """

    return


def defend(
    robots: List[Robot],
    detectLine: Callable[[Robot], pymunk.Vec2d],
    ballPosition: pymunk.Vec2d,
    robotPositions: List[pymunk.Vec2d],
    dribble: Callable[[Robot], None],
    kick: Callable[[Robot], None],
) -> None:
    """Program and logic for own defending robot.

    Args:
        robots: A list of both Robots for own side.
        detectLine: Function returning a pymunk.Vec2d vector representing
            average **direction** of lines detected by robot passed as argument.
        ballPosition: pymunk.Vec2d object representing world coordinate position of ball.
        robotPositions: List of pymunk.Vec2d objects each representing the world coordinate position of a robot,
            in order [own attack robot, own defense robot, opponent attack robot, opponent defense robot].
        dribble: Function to dribble the ball (and sets robot.dribbleState)
        kick: Function to kick the ball in the front catchment area (if any).
    """

    return


def o_attack(
    robots: List[Robot],
    detectLine: Callable[[Robot], pymunk.Vec2d],
    ballPosition: pymunk.Vec2d,
    robotPositions: List[pymunk.Vec2d],
    dribble: Callable[[Robot], None],
    kick: Callable[[Robot], None],
) -> None:
    """Program and logic for opponent attacking robot.

    Args:
        robots: A list of both Robots for opponent side.
        detectLine: Function returning a pymunk.Vec2d vector representing
            average **direction** of lines detected by robot passed as argument.
        ballPosition: pymunk.Vec2d object representing world coordinate position of ball.
        robotPositions: List of pymunk.Vec2d objects each representing the world coordinate position of a robot,
            in order [own attack robot, own defense robot, opponent attack robot, opponent defense robot].
        dribble: Function to dribble the ball (and sets robot.dribbleState)
        kick: Function to kick the ball in the front catchment area (if any).
    """

    return


def o_defend(
    robots: List[Robot],
    detectLine: Callable,
    ballPosition: pymunk.Vec2d,
    robotPositions: List[pymunk.Vec2d],
    dribble: Callable[[Robot], None],
    kick: Callable[[Robot], None],
) -> None:
    """Program and logic for opponent defending robot.

    Args:
        robots: A list of both Robots for opponent side.
        detectLine: Function returning a pymunk.Vec2d vector representing
            average **direction** of lines detected by robot passed as argument.
        ballPosition: pymunk.Vec2d object representing world coordinate position of ball.
        robotPositions: List of pymunk.Vec2d objects each representing the world coordinate position of a robot,
            in order [own attack robot, own defense robot, opponent attack robot, opponent defense robot].
        dribble: Function to dribble the ball (and sets robot.dribbleState)
        kick: Function to kick the ball in the front catchment area (if any).
    """

    return


if __name__ == "__main__":
    main(CONFIG, attack, defend, o_attack, o_defend)
