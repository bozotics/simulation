import math
import timeit
from typing import Dict, List, Optional, Tuple, Union

import arcade
import pymunk

from tools import *


class SimWin(arcade.Window):
    """Main Simulation Window"""

    def __init__(self, width, height, title):
        """create variables"""

        # init parent class
        super().__init__(width, height, title)

        # set up background
        self.drawTimeText = None
        arcade.set_background_color(arcade.color.AMAZON)
        self.background: Optional[arcade.texture.Texture] = None

        # pymunk space
        self.space: Optional[pymunk.Space] = None

        # lists/elements
        self.dynamicSpriteList: Optional[arcade.SpriteList] = None
        self.robots: Optional[List[Robot]] = None
        self.arrowsList: Optional[arcade.ShapeElementList] = None
        self.fieldLines: Optional[List[pymunk.Segment]] = None
        self.penaltyLines: Optional[List[Union[pymunk.Segment, pymunk.Circle]]] = None
        self.ball: Optional[PymunkSprite] = None
        self.ballAngle: float = 0  # ball info

        # debug info
        self.drawTime: float = 0
        self.processingTime: float = 0
        self.refreshRate: float = 0

        # controls
        self.mousePos: Tuple[float, float] = (0, 0)
        self.key: int = 0
        self.pause: bool = False

        # some arrow stuff
        self.arrowState: int = 0
        self.arrowStart: Tuple[float, float] = (0, 0)
        self.arrowEnd: Tuple[float, float] = (0, 0)

        # joints
        self.j1: Optional[pymunk.constraints.PivotJoint] = None
        self.j2: Optional[pymunk.constraints.GearJoint] = None

        # programs
        self.pconfig: Dict[str, bool] = {}
        self.attack: Optional[ProgramType] = None
        self.defend: Optional[ProgramType] = None
        self.o_attack: Optional[ProgramType] = None
        self.o_defend: Optional[ProgramType] = None

    def setup(
        self,
        config: Dict[str, bool],
        attack: ProgramType,
        defend: ProgramType,
        o_attack: ProgramType,
        o_defend: ProgramType,
    ):
        """set up everything"""

        # background
        self.background: arcade.Texture = arcade.load_texture("images/field.jpg")

        # pymunk space
        self.space: pymunk.Space = pymunk.Space()
        self.space.gravity = (0, 0)
        # self.space.damping = 0.4
        self.space.collision_slop = 0.1

        # lists
        self.dynamicSpriteList = arcade.SpriteList()
        self.arrowsList = arcade.ShapeElementList()

        # field elements
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.space.add(body)

        # walls
        walls = [
            pymunk.Segment(body, (0, 0), (SCREEN_WIDTH, 0), 2.0),
            pymunk.Segment(body, (0, 0), (0, SCREEN_HEIGHT), 2.0),
            pymunk.Segment(
                body, (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), 2.0
            ),
            pymunk.Segment(body, (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0), 2.0),
        ]
        for line in walls:
            line.friction = 0.7
            line.elasticity = 0.6
            line.filter = pymunk.ShapeFilter(categories=1)
        self.space.add(*walls)

        # goals
        goals = [
            pymunk.Segment(
                body, (180, 78), (SCREEN_WIDTH - 180, 78), 2.0
            ),  # yellow crossbar
            pymunk.Segment(
                body,
                (180, SCREEN_HEIGHT - 78),
                (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 78),
                2.0,
            ),  # blue crossbar
            pymunk.Segment(body, (180, 60), (SCREEN_WIDTH - 180, 60), 2.0),
            pymunk.Segment(body, (180, 78), (180, 60), 2.0),
            pymunk.Segment(
                body, (SCREEN_WIDTH - 180, 78), (SCREEN_WIDTH - 180, 60), 2.0
            ),
            pymunk.Segment(
                body,
                (180, SCREEN_HEIGHT - 60),
                (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 60),
                2.0,
            ),
            pymunk.Segment(
                body, (180, SCREEN_HEIGHT - 78), (180, SCREEN_HEIGHT - 60), 2.0
            ),
            pymunk.Segment(
                body,
                (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 78),
                (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 60),
                2.0,
            ),
        ]
        for idx, line in enumerate(goals):
            line.elasticity = 0.9
            if idx < 2:
                line.friction = 0.2
                line.filter = pymunk.ShapeFilter(categories=2)
            else:
                line.friction = 1
                line.filter = pymunk.ShapeFilter(categories=1)
        self.space.add(*goals)

        # white lines around the field
        self.fieldLines = [
            pymunk.Segment(body, (77, 77), (77, SCREEN_HEIGHT - 77), 4.0),
            pymunk.Segment(
                body,
                (77, SCREEN_HEIGHT - 77),
                (SCREEN_WIDTH - 77, SCREEN_HEIGHT - 77),
                4.0,
            ),
            pymunk.Segment(
                body,
                (SCREEN_WIDTH - 77, SCREEN_HEIGHT - 77),
                (SCREEN_WIDTH - 77, 77),
                4.0,
            ),
            pymunk.Segment(body, (SCREEN_WIDTH - 77, 77), (77, 77), 4.0),
        ]
        for line in self.fieldLines:
            line.filter = pymunk.ShapeFilter(categories=4)
            line.collision_type = 3
        self.space.add(*self.fieldLines)

        # penalty area lines
        self.penaltyLines = [
            pymunk.Circle(body, 40, (210, 110)),
            pymunk.Circle(body, 40, (210, SCREEN_HEIGHT - 110)),
            pymunk.Circle(body, 40, (SCREEN_WIDTH - 210, 110)),
            pymunk.Circle(body, 40, (SCREEN_WIDTH - 210, SCREEN_HEIGHT - 110)),
            pymunk.Segment(body, (171, 77), (171, 112), 4.0),
            pymunk.Segment(body, (211, 152), (SCREEN_WIDTH - 211, 152), 4.0),
            pymunk.Segment(
                body, (SCREEN_WIDTH - 171, 77), (SCREEN_WIDTH - 171, 112), 4.0
            ),
            pymunk.Segment(
                body, (171, SCREEN_HEIGHT - 77), (171, SCREEN_HEIGHT - 112), 4.0
            ),
            pymunk.Segment(
                body,
                (211, SCREEN_HEIGHT - 152),
                (SCREEN_WIDTH - 211, SCREEN_HEIGHT - 152),
                4.0,
            ),
            pymunk.Segment(
                body,
                (SCREEN_WIDTH - 171, SCREEN_HEIGHT - 77),
                (SCREEN_WIDTH - 171, SCREEN_HEIGHT - 112),
                4.0,
            ),
        ]
        for line in self.penaltyLines:
            line.filter = pymunk.ShapeFilter(categories=4)
            line.collision_type = 3
        self.space.add(*self.penaltyLines)

        # robots
        self.robots = [
            Robot(
                "images/robot.png",
                0.02176,
                2.1,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT * 17 / 40,
                orientation=0,
            ),
            Robot(
                "images/robot.png",
                0.02176,
                2.1,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 6,
                orientation=0,
            ),
            Robot(
                "images/enemy.png",
                0.01611170784103114930182599355532,
                2.1,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT * 7 / 10,
            ),
            Robot(
                "images/enemy.png",
                0.01611170784103114930182599355532,
                2.1,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT * 5 / 6,
            ),
        ]
        for i in range(4):
            self.dynamicSpriteList.append(self.robots[i].sprite)
            self.robots[i].sprite.shape.filter = pymunk.ShapeFilter(
                categories=8, mask=pymunk.ShapeFilter.ALL_MASKS() ^ 0b100
            )
            self.robots[i].sprite.shape.collision_type = 1
            self.j1 = pymunk.constraints.PivotJoint(
                self.robots[i].targetPointBody,
                self.robots[i].sprite.body,
                (0, 0),
                (0, 0),
            )
            self.j1.max_force = 7000
            self.j1.max_bias = 0
            self.j2 = pymunk.constraints.GearJoint(
                self.robots[i].targetPointBody, self.robots[i].sprite.body, 0, 1
            )
            self.j2.max_force = 50000
            self.space.add(
                self.robots[i].sprite.body,
                self.robots[i].sprite.shape,
                self.j1,
                self.j2,
            )

        # ball
        self.ball = PymunkSprite(
            "images/ball.png",
            0.01897533206831119544592030360531,
            0.07,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
        )
        self.dynamicSpriteList.append(self.ball)
        self.ball.shape.filter = pymunk.ShapeFilter(
            categories=16, mask=pymunk.ShapeFilter.ALL_MASKS() ^ 0b110
        )
        self.ball.shape.collision_type = 2
        self.space.add(self.ball.body, self.ball.shape)
        self.ballAngle = 0
        self.j1 = pymunk.constraints.PivotJoint(
            self.space.static_body, self.ball.body, (0, 0), (0, 0)
        )
        self.j1.max_force = 10
        self.j1.max_bias = 0
        self.j2 = pymunk.constraints.GearJoint(
            self.space.static_body, self.ball.body, 0, 1
        )
        self.j2.max_force = 1000
        self.space.add(self.j1, self.j2)

        # programs
        self.pconfig = config
        self.attack = attack
        self.defend = defend
        self.o_attack = o_attack
        self.o_defend = o_defend

    def on_draw(self):
        """called whenever we need to draw the window"""
        arcade.start_render()
        draw_start_time = timeit.default_timer()
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            SCREEN_HEIGHT,
            SCREEN_WIDTH,
            self.background,
            90,
        )
        self.dynamicSpriteList.draw()
        if self.arrowsList:
            self.arrowsList.draw()

        """if self.robots[0].dribbleState == 0:
            arcade.draw_line(
                self.robots[0].sprite.body.position.x,
                self.robots[0].sprite.body.position.y,
                self.ball.body.position.x,
                self.ball.body.position.y,
                arcade.color.RED,
                1,
            )
        else:
            arcade.draw_line(
                self.robots[0].sprite.body.position.x,
                self.robots[0].sprite.body.position.y,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - 78,
                arcade.color.RED,
                1,
            )"""

        # display timings
        output = f"Processing time: {self.processingTime:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE)
        output = f"Drawing time: {self.drawTime:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE)
        output = f"Estimated FPS: {self.refreshRate:.1f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE)
        # output = f"Mouse: {self.mousePos}"
        # arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE)

        self.drawTime = timeit.default_timer() - draw_start_time

    def on_update(self, delta_time: float):
        self.refreshRate = 1 / delta_time
        start_time = timeit.default_timer()

        # user interaction
        if self.key is not None and self.key > 0:
            if self.key == arcade.MOUSE_BUTTON_RIGHT or self.key == arcade.key.B:
                self.ball.body.position = pymunk.Vec2d(*self.mousePos)
                self.ball.body.velocity = (0, 0)
                print(self.ball.body.position)
            elif arcade.key.KEY_1 <= self.key <= arcade.key.KEY_4:
                self.robots[
                    self.key - arcade.key.KEY_1
                ].sprite.body.position = pymunk.Vec2d(*self.mousePos)
                self.robots[self.key - arcade.key.KEY_1].sprite.body.velocity = (0, 0)
                print(self.robots[self.key - arcade.key.KEY_1].sprite.body.position)
            elif self.key == arcade.key.Q or self.key == arcade.key.W:
                self.robots[
                    0 if self.key == arcade.key.Q else 1
                ].sprite.body.position = (
                    SCREEN_WIDTH / 2,
                    30,
                )
                self.robots[
                    0 if self.key == arcade.key.Q else 1
                ].sprite.body.velocity = (0, 0)
                self.robots[0 if self.key == arcade.key.Q else 1].sprite.body.angle = (
                    math.pi / 2
                )
            elif self.key == arcade.key.E or self.key == arcade.key.R:
                self.robots[
                    2 if self.key == arcade.key.E else 3
                ].sprite.body.position = (
                    SCREEN_WIDTH / 2,
                    SCREEN_HEIGHT - 30,
                )
                self.robots[
                    2 if self.key == arcade.key.E else 3
                ].sprite.body.velocity = (0, 0)
                self.robots[2 if self.key == arcade.key.E else 3].sprite.body.angle = (
                    math.pi / 2
                )
            self.key = 0

        if self.arrowState == 2:
            self.arrowState = 0
            self.arrowsList.append(
                arcade.create_line(
                    self.arrowStart[0],
                    self.arrowStart[1],
                    self.arrowEnd[0],
                    self.arrowEnd[1],
                    (255, 0, 0),
                    2,
                )
            )
            print(self.arrowsList)
        elif self.arrowState == 3:
            self.arrowState = 0
            while self.arrowsList:
                self.arrowsList.remove(self.arrowsList[0])

        # update sprite positions
        for sprite in self.dynamicSpriteList:
            sprite.center_x = sprite.shape.body.position.x
            sprite.center_y = sprite.shape.body.position.y
            sprite.angle = math.degrees(sprite.shape.body.angle)

        # update sensor readings
        for robot in self.robots:
            robot.TOFReadings = [
                SCREEN_HEIGHT - robot.sprite.body.position.y,
                SCREEN_WIDTH - robot.sprite.body.position.x,
                robot.sprite.body.position.y,
                robot.sprite.body.position.x,
            ]

        if self.pause:
            return

        self.programs()

        # convert between angles
        if self.ball.body.angle >= 0:
            self.ballAngle = 2 * math.pi - math.fmod(self.ball.body.angle, 2 * math.pi)
        else:
            self.ballAngle = -math.fmod(self.ball.body.angle, 2 * math.pi)
        if self.robots[0].sprite.body.angle >= 0:
            self.robots[0].orientation = 2 * math.pi - math.fmod(
                self.robots[0].sprite.body.angle, 2 * math.pi
            )
        else:
            self.robots[0].orientation = -math.fmod(
                self.robots[0].sprite.body.angle, 2 * math.pi
            )

        # slopes
        if self.ball.body.position.x <= 35:
            force = rel_vec_to_point(
                self.ball.body, (35, self.ball.body.position.y), self.ballAngle
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))
        if self.ball.body.position.x >= SCREEN_WIDTH - 35:
            force = rel_vec_to_point(
                self.ball.body,
                (SCREEN_WIDTH - 35, self.ball.body.position.y),
                self.ballAngle,
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))
        if self.ball.body.position.y <= 35:
            force = rel_vec_to_point(
                self.ball.body, (self.ball.body.position.x, 35), self.ballAngle
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))
        if self.ball.body.position.y >= SCREEN_HEIGHT - 35:
            force = rel_vec_to_point(
                self.ball.body,
                (self.ball.body.position.x, SCREEN_HEIGHT - 35),
                self.ballAngle,
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))

        self.space.step(1 / 60.0)

        self.processingTime = timeit.default_timer() - start_time

    def programs(self):
        robotPositions = [x.sprite.body.position for x in self.robots]

        # own programs
        self.attack(
            [self.robots[0], self.robots[1]],
            self.line,
            self.ball.body.position,
            robotPositions,
            self.dribble,
            self.kick,
        )
        self.defend(
            [self.robots[0], self.robots[1]],
            self.line,
            self.ball.body.position,
            robotPositions,
            self.dribble,
            self.kick,
        )

        # opponent programs
        self.o_attack(
            [self.robots[2], self.robots[3]],
            self.line,
            self.ball.body.position,
            robotPositions,
            self.dribble,
            self.kick,
        )
        self.o_defend(
            [self.robots[2], self.robots[3]],
            self.line,
            self.ball.body.position,
            robotPositions,
            self.dribble,
            self.kick,
        )

    # TODO: somehow make this in the program code (deals with field)
    def line(self, robot: Robot) -> pymunk.Vec2d:
        """Finds average direction (sum of all vectors of direction of line) of all lines detected.

        Args:
            robot: A Robot from which lines will be detected.

        Returns: A pymunk.Vec2d vector representing average **direction** of lines.
            Returns pymunk.Vec2d(0, 0) if no line is detected.
            HINT: Move in the opposite direction of this vector to move away from lines.
        """

        resultant = pymunk.Vec2d(0, 0)
        for line in self.fieldLines + self.penaltyLines:
            if line.shapes_collide(robot.sprite.shape).points:
                resultant += line.shapes_collide(robot.sprite.shape).normal
        return -resultant

    # TODO: somehow make this in the program code (deals with ball)
    def dribble(self, robot: Robot) -> None:
        robot_to_ball = rel_vec_to_point(
            robot.sprite.body,
            self.ball.body.position,
            robot.orientation,
        )
        if (
            vec_to_world(robot_to_ball) * 180 / math.pi > 346
            or vec_to_world(robot_to_ball) * 180 / math.pi < 14
        ) and robot_to_ball.length < 40:
            force = 30 * rel_vec_to_point(
                self.ball.body, robot.sprite.body.position, self.ballAngle
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))
            robot.dribbleState = 1
        elif (
            166 < vec_to_world(robot_to_ball) * 180 / math.pi < 194
        ) and robot_to_ball.length < 40:
            force = 31 * rel_vec_to_point(
                self.ball.body, robot.sprite.body.position, self.ballAngle
            )
            self.ball.body.apply_force_at_local_point(force, (0, 0))
            robot.dribbleState = 2
        else:
            robot.dribbleState = 0

    # TODO: somehow make this in the program code (deals with ball)
    def kick(self, robot: Robot) -> None:
        """Kicks ball in front dribbler of attack robot.

        Args:
            robot: A Robot whose kicker will be activated if its dribbleState is 1.
        """

        if robot.dribbleState == 1:
            self.ball.body.apply_impulse_at_local_point((0, 15), (0, -5))
        """elif self.robots[0].dribbleState == 2:
            self.ball.body.apply_impulse_at_world_point(
                (self.ball.body.position - self.robots[0].sprite.body.position),
                (self.ball.body.position.x, self.ball.body.position.y + 10),
            )"""

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousePos = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.arrowState == 0:
                self.arrowStart = (x, y)
            elif self.arrowState == 1:
                self.arrowEnd = (x, y)
            self.arrowState += 1
        else:
            self.key = button

    def on_key_press(self, key, modifiers):
        self.key = key
        if key == arcade.key.P:
            self.pause = not self.pause
        elif key == arcade.key.ESCAPE:
            self.arrowState = 3
        else:
            self.key = key


def main(
    config: Dict[str, bool],
    attack: ProgramType,
    defend: ProgramType,
    o_attack: ProgramType,
    o_defend: ProgramType,
):
    window = SimWin(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup(config, attack, defend, o_attack, o_defend)
    arcade.run()


if __name__ == "__main__":
    import program

    main(
        program.CONFIG,
        program.attack,
        program.defend,
        program.o_attack,
        program.o_defend,
    )
