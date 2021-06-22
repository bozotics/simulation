import math
from typing import Callable, List

import pymunk

import example
from tools import *


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

    relVec = rel_vec_to_point(
        robots[0].sprite.body, ballPosition, robots[0].orientation
    )
    robots[0].direction = vec_to_world(relVec)
    robots[0].speed = 500
    factor = min(0.002 * (math.e ** (6.7 * (1 - relVec.length / 850))), 1)
    robots[0].chaseState = 1
    robots[0].direction -= math.pi
    if robots[0].direction >= 0:
        offset = min(robots[0].direction * 1.0, math.pi / 2)
    else:
        offset = max(robots[0].direction * 1.0, -math.pi / 2)
    robots[0].move(
        robots[0].speed,
        robots[0].direction + math.pi + offset * factor + robots[0].orientation,
    )

    robots[0].turn(0)
    if robots[0].sprite.body.angle >= 0:
        robots[0].orientation = 2 * math.pi - math.fmod(
            robots[0].sprite.body.angle, 2 * math.pi
        )
    else:
        robots[0].orientation = -math.fmod(robots[0].sprite.body.angle, 2 * math.pi)

    example.out(robots[0], detectLine(robots[0]))

    dribble(robots[0])


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

    relVec = rel_vec_to_point(
        robots[1].sprite.body,
        (max(min(ballPosition.x, 335), SCREEN_WIDTH - 335), 600),
        robots[1].orientation,
    )
    robots[1].direction = vec_to_world(relVec)
    robots[1].speed = 300
    robots[1].move(robots[1].speed, robots[1].direction + robots[1].orientation)

    robots[1].turn(0)
    if robots[1].sprite.body.angle >= 0:
        robots[1].orientation = 2 * math.pi - math.fmod(
            robots[1].sprite.body.angle, 2 * math.pi
        )
    else:
        robots[1].orientation = -math.fmod(robots[1].sprite.body.angle, 2 * math.pi)

    # program.out(robot, detectLine(robot))
