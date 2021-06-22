# vector functions
import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union

import arcade
import pymunk

__all__ = [
    "SCREEN_WIDTH",
    "SCREEN_HEIGHT",
    "SCREEN_TITLE",
    "PymunkSprite",
    "Robot",
    "ProgramType",
    "rel_vec_to_point",
    "vec_to_world",
    "make_vec_from_polar",
]

# constants
SCREEN_WIDTH = 546
SCREEN_HEIGHT = 729
SCREEN_TITLE = "Cup"

# classes
# We need a Sprite and a Pymunk physics object. This class blends them together.
class PymunkSprite(arcade.Sprite):
    """An arcade.Sprite object that contains a pymunk object"""  # TODO: not sure if this is correct

    def __init__(
        self,
        filename: str,
        scale: float,
        mass: float,
        center_x: float = 0,
        center_y: float = 0,
    ):
        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)
        width = self.texture.width * scale
        height = self.texture.height * scale

        moment = pymunk.moment_for_box(mass, (width, height))
        self.body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
        self.body.position = pymunk.Vec2d(center_x, center_y)
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = 0.8


@dataclass
class Robot:  # TODO: improve docstring, especially attributes
    """A container for robots.

    This class represents a robot and contains a PymunkSprite object.
    It also has some useful attributes where information about the robot are stored.
    (only useful attributes are listed below, [actually even for those i'm not very sure...])

    Attributes:
        direction: Direction robot is facing, referenced in code.
        speed: Speed robot is travelling at, referenced in code.
        angle: Angle robot is travelling at, referenced in code.
        orientation: Orientation of robot, referenced in code.
        dribbleState: State of dribbler, 0 for none, 1 for front, 2 for back, referenced in code.
        chaseState: Chase state for programming purposes, referenced in code.
        TOFReadings: (fake) TOF sensor readings, clockwise starting from front. [front, right, back, left]
            Currently calculated based on coordinate position of the robot.
            # TODO: Make TOF sensor readings more realistic, maybe add some noise 🙃
    """

    filename: str
    scale: float
    mass: float
    center_x: float = 0
    center_y: float = 0
    direction: float = 0
    speed: float = 500
    angle: float = 0
    orientation: float = math.pi
    dribbleState: int = 0
    chaseState: int = 0
    TOFReadings: Optional[List[float]] = None
    targetPointBody: Optional[pymunk.Body] = None

    def __post_init__(self):
        self.sprite = PymunkSprite(
            self.filename, self.scale, self.mass, self.center_x, self.center_y
        )
        self.TOFReadings = [
            SCREEN_HEIGHT - self.center_y,
            SCREEN_WIDTH - self.center_x,
            self.center_y,
            self.center_x,
        ]
        self.targetPointBody = pymunk.Body(
            float("inf"), float("inf"), pymunk.Body.STATIC
        )

        # temporary workaround for https://youtrack.jetbrains.com/issue/PY-28549
        self.direction = self.direction
        self.speed = self.speed
        self.angle = self.angle
        self.orientation = self.orientation
        self.dribbleState = self.dribbleState
        self.chaseState = self.chaseState

    def flick(self, direction: int) -> None:
        """Makes the robot flick the ball in the back dribbler.

        Args:
            direction: A int representing direction of flick. 0 will cause the robot to spin counterclockwise,
                hence flicking the ball to the right, while 1 (or any non-zero int) will cause the robot to
                spin clockwise, hence flicking the ball to the left.
        """

        if self.dribbleState == 2:
            if direction == 0:
                self.sprite.body.apply_impulse_at_local_point((-40, 0), (0, 20))
                self.sprite.body.apply_impulse_at_local_point((40, 0), (0, -20))
            else:
                self.sprite.body.apply_impulse_at_local_point((40, 0), (0, 20))
                self.sprite.body.apply_impulse_at_local_point((-40, 0), (0, -20))

    def move(self, speed: float = 0, direction: float = 0) -> None:
        """Moves the robot at a velocity defined by the speed and direction provided.

        Args:
            speed: A float representing the speed that the robot should travel at (in arbitrary units).
            direction: A float representing the direction that the robot should travel in (in radians).
        """

        self.targetPointBody.velocity = make_vec_from_polar(
            speed,
            direction,
        )

    def turn(self, angle: float) -> None:
        """Turns the robot to face a certain angle.

        Args:
            angle: A float representing the angle that the robot should face (in radians).
        """

        self.targetPointBody.angle = angle


# types
ProgramType = (
    Callable[
        [
            List[Robot],
            Callable[[Robot], pymunk.Vec2d],
            pymunk.Vec2d,
            List[pymunk.Vec2d],
            Callable[[Robot], None],
            Callable[[Robot], None],
        ],
        None,
    ],
)


# functions
def rel_vec_to_point(
    body: pymunk.Body,
    point: Union[pymunk.Vec2d, Tuple[float, float]] = pymunk.Vec2d(0, 0),
    angle: float = 0,
) -> pymunk.Vec2d:
    """Returns a pymunk.Vec2d object representing relative position of a point from the position of a body.

    Args:
        body: The reference pymunk.Body, usually a robot.
        point: Any pymunk.Vec2d (also accepts a tuple) point in the world,
            could be position of another robot or the ball.
        angle: Orientation of the robot (in radians), to get a relative position from the front of the robot.
    """

    vec = point - body.position
    vec.rotated(angle)
    return vec


def vec_to_world(vec: pymunk.Vec2d = pymunk.Vec2d(0, 0)) -> float:
    """Returns the angle of the vector (clockwise bearing in radians, north or 0 being the positive vertical direction).

    Args:
        vec: A pymunk.Vec2d vector from which the angle is derived from.
    """

    return (math.pi / 2 - vec.angle) % (2 * math.pi)


def make_vec_from_polar(mag: float = 0, angle: float = 0) -> pymunk.Vec2d:
    """Returns a pymunk.Vec2d vector coordinate from a polar coordinate.

    Args:
        mag: A float representing radial distance.
        angle: A float representing polar angle (in radians).
    """

    angle = math.pi / 2 - angle
    vec = pymunk.Vec2d(mag * math.cos(angle), mag * math.sin(angle))
    return vec
