import math
from typing import Callable, List

import pymunk

import example
from tools import *

attackRobot = 0
defenseRobot = 1


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

    global attackRobot, defenseRobot
    attackRobot = (
        0
        if (ballPosition - robotPositions[0]).length
        < (ballPosition - robotPositions[1]).length
        else 1
    )
    defenseRobot = (
        1
        if (ballPosition - robotPositions[0]).length
        < (ballPosition - robotPositions[1]).length
        else 0
    )

    if robots[attackRobot].dribbleState == 0:
        relVec = rel_vec_to_point(
            robots[attackRobot].sprite.body,
            ballPosition,
            robots[attackRobot].orientation,
        )
        robots[attackRobot].direction = vec_to_world(relVec)
        robots[attackRobot].speed = 600
        factor = min(0.002 * (math.e ** (7.1 * (1 - relVec.length / 850))), 1.4)
        # factor = min(0.01*(1-relVec.length/850)*(math.e**(5*(1-relVec.length/850))),1)

        # obstacle avoidance
        # ref: https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm
        d = ballPosition - robots[attackRobot].sprite.body.position
        r = 30
        a = d.dot(d)
        f = robots[attackRobot].sprite.body.position - robotPositions[2]
        b = 2 * (f.dot(d))
        c = f.dot(f) - r * r
        discriminant = b * b - 4 * a * c
        obstaclePos = None
        if discriminant >= 0:
            discriminant = math.sqrt(discriminant)
            if a == 0:
                t1 = 2
                t2 = 2
            else:
                t1 = (-b - discriminant) / (2 * a)
                t2 = (-b + discriminant) / (2 * a)
            if (0 <= t1 <= 1) and (0 <= t2 <= 1):
                obstaclePos = robotPositions[2]
                print("intersect", obstaclePos)

        if obstaclePos:
            robots[attackRobot].chaseState = 2
        else:  # no obstacles
            # check catch with back dribbler
            if (
                robots[attackRobot].direction <= math.pi * 0.7
                or robots[attackRobot].direction >= math.pi * 1.3
            ):  # front half
                robots[attackRobot].chaseState = 0
            else:
                robots[attackRobot].chaseState = 1  # BRUH 1

        # face forward
        # robots[attackRobot].turn(2*math.pi * round(robots[attackRobot].sprite.body.angle/(2*math.pi)))
        if ((robotPositions[3].x - 30) - 180) > (
            (SCREEN_WIDTH - 180) - robotPositions[3].x + 30
        ):  # if left goal gap bigger than right goal gap
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((robotPositions[3].x - 30) + 180) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )
        else:
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((SCREEN_WIDTH - 180) + robotPositions[3].x + 30) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )
        goaldirection = vec_to_world(relVec)
        if goaldirection > math.pi * 1.85 or goaldirection < math.pi * 0.15:
            robots[attackRobot].angle = goaldirection  # centre of goal
            if robots[attackRobot].angle > math.pi:
                robots[attackRobot].angle -= math.pi * 2
            robots[attackRobot].turn(
                2
                * math.pi
                * round(robots[attackRobot].sprite.body.angle / (2 * math.pi))
                - robots[attackRobot].angle
            )
        else:
            robots[attackRobot].turn(
                2
                * math.pi
                * round(robots[attackRobot].sprite.body.angle / (2 * math.pi))
            )
    ##############
    elif robots[attackRobot].dribbleState == 1:
        if ((robotPositions[3].x - 30) - 180) > (
            (SCREEN_WIDTH - 180) - robotPositions[3].x + 30
        ):  # if left goal gap bigger than right goal gap
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((robotPositions[3].x - 30) + 180) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )
        else:
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((SCREEN_WIDTH - 180) + robotPositions[3].x + 30) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )
        robots[attackRobot].direction = vec_to_world(relVec)
        robots[attackRobot].speed = 500
        factor = min(0.007 * (math.e ** (5.6 * (1 - relVec.length / 900))), 1)
        robots[attackRobot].chaseState = 0
        # face goal
        if (
            robots[attackRobot].direction > math.pi * 1.6
            or robots[attackRobot].direction < math.pi * 0.4
        ):
            robots[attackRobot].angle = robots[attackRobot].direction  # centre of goal
            if robots[attackRobot].angle > math.pi:
                robots[attackRobot].angle -= math.pi * 2
            robots[attackRobot].turn(
                2
                * math.pi
                * round(robots[attackRobot].sprite.body.angle / (2 * math.pi))
                - robots[attackRobot].angle
            )
            # shoot ball if close to goal
            if (250 > relVec.length > 80) and robots[
                attackRobot
            ].sprite.body.position.y < SCREEN_HEIGHT - 140:
                kick(robots[attackRobot])
                print("kick")
        else:
            robots[attackRobot].turn(
                2
                * math.pi
                * round(robots[attackRobot].sprite.body.angle / (2 * math.pi))
            )
    elif robots[attackRobot].dribbleState == 2:
        if ((robotPositions[3].x - 30) - 180) > (
            (SCREEN_WIDTH - 180) - robotPositions[3].x + 30
        ):  # if left goal gap SMALLER than right goal gap
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((robotPositions[3].x - 30) + 180) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )  # go for smaller gap
        else:
            relVec = rel_vec_to_point(
                robots[attackRobot].sprite.body,
                (
                    ((SCREEN_WIDTH - 180) + robotPositions[3].x + 30) / 2,
                    SCREEN_HEIGHT - 78,
                ),
                robots[attackRobot].orientation,
            )  # go for bigger gap
        robots[attackRobot].chaseState = 0
        robots[attackRobot].direction = vec_to_world(relVec)
        robots[attackRobot].speed = 600
        if 350 > relVec.length > 50:
            if robots[attackRobot].sprite.body.position.x < SCREEN_WIDTH * 0.5:
                robots[attackRobot].flick(0)
            else:
                robots[attackRobot].flick(1)
        factor = 0.0

    if robots[attackRobot].chaseState == 0:
        if robots[attackRobot].direction < math.pi:
            # offset = min(robots[attackRobot].direction*0.8,math.pi/2)
            offset = min(
                2.0 * (math.e ** (0.2 * robots[attackRobot].direction) - 1),
                math.pi / 2,
            )
        else:
            # offset = max((robots[attackRobot].direction-math.pi*2)*0.8,-math.pi/2)
            offset = max(
                2.0
                * (math.e ** (0.2 * (robots[attackRobot].direction - math.pi * 2)) - 1),
                -math.pi / 2,
            )
        robots[attackRobot].move(
            robots[attackRobot].speed,
            robots[attackRobot].direction
            + offset * factor
            + robots[attackRobot].orientation,
        )
    elif robots[attackRobot].chaseState == 1:
        robots[attackRobot].direction -= math.pi
        if robots[attackRobot].direction >= 0:
            offset = min(robots[attackRobot].direction * 1.0, math.pi / 2)
        else:
            offset = max(robots[attackRobot].direction * 1.0, -math.pi / 2)
        robots[attackRobot].move(
            robots[attackRobot].speed,
            robots[attackRobot].direction
            + math.pi
            + offset * factor
            + robots[attackRobot].orientation,
        )
    elif robots[attackRobot].chaseState == 2:
        obsVec = rel_vec_to_point(
            robots[attackRobot].sprite.body,
            obstaclePos,
            robots[attackRobot].orientation,
        )
        obsDirection = vec_to_world(obsVec)
        if d.cross(f) >= 0:  # clockwise
            robots[attackRobot].direction -= math.pi / 44 / 4 / 4 / 4 / 4 / 4 / 4
            print("clock")
        else:  # anti-clockwise
            robots[attackRobot].direction += math.pi / 4
            print("anti")
        robots[attackRobot].move(
            robots[attackRobot].speed,
            robots[attackRobot].direction + robots[attackRobot].orientation,
        )
    # pass

    dribble(robots[attackRobot])

    example.out(robots[attackRobot], detectLine(robots[attackRobot]))


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

    # Standard goalie
    relVec = rel_vec_to_point(
        robots[defenseRobot].sprite.body,
        (max(min(ballPosition.x, 335), SCREEN_WIDTH - 335), 130),
        robots[defenseRobot].orientation,
    )
    robots[defenseRobot].direction = vec_to_world(relVec)
    robots[defenseRobot].speed = 300
    robots[defenseRobot].move(
        robots[defenseRobot].speed,
        robots[defenseRobot].direction + robots[defenseRobot].orientation,
    )

    robots[defenseRobot].turn(
        2 * math.pi * round(robots[defenseRobot].sprite.body.angle / (2 * math.pi))
    )
    if robots[defenseRobot].sprite.body.angle >= 0:
        robots[defenseRobot].orientation = 2 * math.pi - math.fmod(
            robots[defenseRobot].sprite.body.angle, 2 * math.pi
        )
    else:
        robots[defenseRobot].orientation = -math.fmod(
            robots[defenseRobot].sprite.body.angle, 2 * math.pi
        )

    dribble(robots[defenseRobot])

    # program.out(robot, detectLine(robot))

    # Chase opponent robot
    """relVec = rel_vec_to_point(robots[defenseRobot].sprite.body, robotPositions[2], robots[defenseRobot].orientation)
	robots[defenseRobot].direction = vec_to_world(relVec)
	robots[defenseRobot].speed = 450
	factor = min(0.002*(math.e**(6.7*(1-relVec.length/850))), 1)
	if (robotPositions[2].x<270): #if opp robot on left
	    relVec = rel_vec_to_point(robots[defenseRobot].sprite.body, (0,SCREEN_HEIGHT), robots[defenseRobot].orientation)
	else:
	    relVec = rel_vec_to_point(robots[defenseRobot].sprite.body, (SCREEN_WIDTH, SCREEN_HEIGHT), robots[defenseRobot].orientation)
	robots[attackRobot].angle = vec_to_world(relVec)
	if robots[attackRobot].angle > math.pi:
	    robots[attackRobot].angle -= math.pi*2
	robots[defenseRobot].turn(2*math.pi * round(robots[defenseRobot].sprite.body.angle/(2*math.pi))-robots[defenseRobot].angle)
	if robots[defenseRobot].direction < math.pi:
	    offset = min(robots[defenseRobot].direction*1.0,math.pi/2)
	else:
	    offset = max((robots[defenseRobot].direction-math.pi*2)*1.0,-math.pi/2)
	robots[defenseRobot].move(robots[defenseRobot].speed,robots[defenseRobot].direction + offset*factor + robots[defenseRobot].orientation)"""
