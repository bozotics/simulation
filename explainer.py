import arcade
import pymunk
import timeit
import time
import math
import os

SCREEN_WIDTH = 546
SCREEN_HEIGHT = 729
SCREEN_TITLE = "Cup"
DEFAULT_MASS = 1
DEFAULT_FRICTION = 0.8
DEFAULT_ELASTICITY = 0.6
ROBOT_MOVE_FORCE = 3000
ROBOT_SPIN_FORCE = 100
ROBOT_FRICTION_FORCE = 0.35 * 2.1 * 2943 #px s-2
MAX_VELOCITY = 600

class PymunkSprite(arcade.Sprite):
    # We need a Sprite and a Pymunk physics object. This class blends them together.
    def __init__(self,
                 filename,
                 center_x=0,
                 center_y=0,
                 scale=1,
                 mass=DEFAULT_MASS,
                 moment=None,
                 friction=DEFAULT_FRICTION,
                 body_type=pymunk.Body.DYNAMIC):

        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)
        width = self.texture.width * scale
        height = self.texture.height * scale

        if moment is None:
            moment = pymunk.moment_for_box(mass, (width, height))
        self.body = pymunk.Body(mass, moment, body_type=body_type)
        self.body.position = pymunk.Vec2d(center_x, center_y)
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = friction

def rel_vec_to_point(body, point=(0,0), angle=0):
    vect = point-body.position
    vect.rotate(angle)
    return vect

def Vec2D_to_World(vect=(0,0)):
    vectAngle = vect.angle
    if (vectAngle >=0 and vectAngle <= math.pi*0.5) or vectAngle < 0:
        vectAngle = math.pi*0.5 - vectAngle
    else:
        vectAngle = math.pi*2.5 - vectAngle
    return vectAngle

def make_vec_from_polar(mag=0, angle=0):
    angle = math.pi/2 - angle
    vect = (mag*math.cos(angle), mag*math.sin(angle))
    return vect

def make_vec_from_point(point1=(0,0), point2=(0,0)):
    return (point2-point1)
    

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)
        self.background = arcade.load_texture("images/field.jpg")

        self.space = pymunk.Space()
        self.space.gravity = (0,0)
        #self.space.damping = 0.4
        self.space.collision_slop = 0.1

        self.dynamic_sprite_list = arcade.SpriteList[PymunkSprite]()
        self.arrows_list = arcade.ShapeElementList()
        self.static_lines = []

        self.processing_time_text = None
        self.draw_time_text = None
        self.processing_time = 0
        self.draw_time = 0
        self.robotPos = (0,0)
        self.mousePos = (0,0)
        self.newPos = False
        self.keyNum = 0
        self.keyRelease = 0
        self.released = False
        self.pause = False
        self.arrowState = 0
        self.arrowStart = (0,0)
        self.arrowEnd = (0,0)
        self.dribble_state = [0,0,0,0]
        self.chase_state = [0,0,0,0]

        # walls
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        walls = [
            pymunk.Segment(body, [0, 0], [SCREEN_WIDTH, 0], 2.0),
            pymunk.Segment(body, [0, 0], [0, SCREEN_HEIGHT], 2.0),
            pymunk.Segment(body, [0, SCREEN_HEIGHT], [SCREEN_WIDTH, SCREEN_HEIGHT], 2.0),
            pymunk.Segment(body, [SCREEN_WIDTH, SCREEN_HEIGHT], [SCREEN_WIDTH, 0], 2.0),
            ]
        for line in walls:
            line.friction = 0.7
            line.elasticity = 0.6
            line.filter = pymunk.ShapeFilter(categories=1)
        self.space.add(walls)

        goals = [
            pymunk.Segment(body, [180, 78], [SCREEN_WIDTH-180, 78], 2.0),   #yellow crossbar
            pymunk.Segment(body, [180, SCREEN_HEIGHT-78], [SCREEN_WIDTH-180, SCREEN_HEIGHT-78], 2.0),   #blue crossbar
            pymunk.Segment(body, [180, 60], [SCREEN_WIDTH-180, 60], 2.0),
            pymunk.Segment(body, [180, 78], [180, 60], 2.0),
            pymunk.Segment(body, [SCREEN_WIDTH-180, 78], [SCREEN_WIDTH-180, 60], 2.0),
            pymunk.Segment(body, [180, SCREEN_HEIGHT-60], [SCREEN_WIDTH-180, SCREEN_HEIGHT-60], 2.0),
            pymunk.Segment(body, [180, SCREEN_HEIGHT-78], [180, SCREEN_HEIGHT-60], 2.0),
            pymunk.Segment(body, [SCREEN_WIDTH-180, SCREEN_HEIGHT-78], [SCREEN_WIDTH-180, SCREEN_HEIGHT-60], 2.0),
            ]
        for idx,line in enumerate(goals):
            line.elasticity = 0.9
            if idx < 2:
                line.friction = 0.2
                line.filter = pymunk.ShapeFilter(categories=2)
            else:
                line.friction = 1
                line.filter = pymunk.ShapeFilter(categories=1)
        self.space.add(goals)

        # white lines
        self.static_lines = [
            pymunk.Segment(body, [77, 77], [77, SCREEN_HEIGHT-77], 4.0),
            pymunk.Segment(body, [77, SCREEN_HEIGHT-77], [SCREEN_WIDTH-77, SCREEN_HEIGHT-77], 4.0),
            pymunk.Segment(body, [SCREEN_WIDTH-77, SCREEN_HEIGHT-77], [SCREEN_WIDTH-77, 77], 4.0),
            pymunk.Segment(body, [SCREEN_WIDTH-77, 77], [77, 77], 4.0),
            pymunk.Segment(body, [171, 77], [171, 112], 4.0),
            pymunk.Segment(body, [211, 152], [SCREEN_WIDTH-211, 152], 4.0),
            pymunk.Segment(body, [SCREEN_WIDTH-171, 77], [SCREEN_WIDTH-171, 112], 4.0),
            pymunk.Segment(body, [171, SCREEN_HEIGHT-77], [171, SCREEN_HEIGHT-112], 4.0),
            pymunk.Segment(body, [211, SCREEN_HEIGHT-152], [SCREEN_WIDTH-211, SCREEN_HEIGHT-152], 4.0),
            pymunk.Segment(body, [SCREEN_WIDTH-171, SCREEN_HEIGHT-77], [SCREEN_WIDTH-171, SCREEN_HEIGHT-112], 4.0),
        ]
        for line in self.static_lines:
            line.filter = pymunk.ShapeFilter(categories=4)
            line.collision_type = 3
        self.space.add(self.static_lines)

        self.arcs = [
            pymunk.Circle(body, 40, (210,110)),
            pymunk.Circle(body, 40, (210,SCREEN_HEIGHT-110)),
            pymunk.Circle(body, 40, (SCREEN_WIDTH-210,110)),
            pymunk.Circle(body, 40, (SCREEN_WIDTH-210,SCREEN_HEIGHT-110))
        ]
        for arc in self.arcs:
            arc.filter = pymunk.ShapeFilter(categories=4)
            arc.collision_type = 3
        self.space.add(self.arcs)

        self.direction = [0,0,0,0]
        self.speed = [500,500,500,500]
        self.angle = [0,0,0,0]
        self.robotAngle = [0,0,math.pi,math.pi]
        self.attackRobot = 0
        self.defenceRobot = 1
        self.robot = [PymunkSprite("images/robot.png", SCREEN_WIDTH/2, SCREEN_HEIGHT*17/40, 0.02176, 2.1),
                      PymunkSprite("images/robot.png", SCREEN_WIDTH/2, SCREEN_HEIGHT/6, 0.02176, 2.1),
                      PymunkSprite("images/enemy.png", SCREEN_WIDTH/2, SCREEN_HEIGHT*7/10, 0.01611170784103114930182599355532, 2.1), 
                      PymunkSprite("images/enemy.png", SCREEN_WIDTH/2, SCREEN_HEIGHT*5/6, 0.01611170784103114930182599355532, 2.1)]
        self.target_point_body = [pymunk.Body(pymunk.inf, pymunk.inf, pymunk.Body.STATIC), pymunk.Body(pymunk.inf, pymunk.inf, pymunk.Body.STATIC), pymunk.Body(pymunk.inf, pymunk.inf, pymunk.Body.STATIC), pymunk.Body(pymunk.inf, pymunk.inf, pymunk.Body.STATIC)]
        for i in range(4):        
            self.dynamic_sprite_list.append(self.robot[i])
            self.robot[i].shape.filter = pymunk.ShapeFilter(categories=8, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b100)
            self.robot[i].shape.collision_type = 1
            self.j1 = pymunk.constraint.PivotJoint(self.target_point_body[i], self.robot[i].body, (0,0), (0,0))
            self.j1.max_force = 7000
            self.j1.max_bias = 0
            self.j2 = pymunk.constraint.GearJoint(self.target_point_body[i], self.robot[i].body, 0, 1)
            self.j2.max_force = 50000
            self.j2_max_bias = 0
            self.space.add(self.robot[i].body, self.robot[i].shape, self.j1, self.j2)

        self.ball = PymunkSprite("images/ball.png", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 0.01897533206831119544592030360531, 0.07)
        self.dynamic_sprite_list.append(self.ball)
        self.ball.shape.filter = pymunk.ShapeFilter(categories=16, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b110)
        self.ball.shape.collision_type = 2
        self.space.add(self.ball.body, self.ball.shape)
        self.ballAngle = 0
        self.j1 = pymunk.constraint.PivotJoint(self.space.static_body, self.ball.body, (0,0), (0,0))
        self.j1.max_force = 10
        self.j1.max_bias = 0
        self.j2 = pymunk.constraint.GearJoint(self.space.static_body, self.ball.body, 0, 1)
        self.j2.max_force = 1000
        self.j2_max_bias = 0
        self.space.add(self.j1,self.j2)

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        draw_start_time = timeit.default_timer()
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      SCREEN_HEIGHT, SCREEN_WIDTH, self.background, 90)
        self.dynamic_sprite_list.draw()
        if self.arrows_list:
            self.arrows_list.draw()
        """
        if self.dribble_state[0]==0:
            arcade.draw_line(self.robot[0].body.position.x, self.robot[0].body.position.y, self.ball.body.position.x, self.ball.body.position.y, arcade.color.RED, 1)
        else:
            arcade.draw_line(self.robot[0].body.position.x, self.robot[0].body.position.y, SCREEN_WIDTH/2, SCREEN_HEIGHT-78, arcade.color.RED, 1)
        """
        # Print draw time
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE)
        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE)
        #output = f"Mouse: {self.mousePos}"
        #arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_update(self, delta_time):
        if self.pause:
            if self.newPos:
                self.newPos = False
                if self.keyNum == 0:
                    self.ball.body.position = self.mousePos
                    self.ball.body.velocity = (0,0)
                    print(self.ball.body.position)
                elif self.keyNum >= 1 and self.keyNum <= 4:
                    self.robot[self.keyNum-1].body.position = self.mousePos
                    self.robot[self.keyNum-1].body.velocity = (0,0)
                    print(self.robot[self.keyNum-1].body.position)
                elif self.keyNum == 5 or self.keyNum == 6:
                    self.robot[self.keyNum-5].body.position = (SCREEN_WIDTH/2,30)
                    self.robot[self.keyNum-5].body.velocity = (0,0)
                    self.robot[self.keyNum-5].body.angle = (math.pi/2)
                elif self.keyNum == 7 or self.keyNum == 8:
                    self.robot[self.keyNum-5].body.position = (SCREEN_WIDTH/2,SCREEN_HEIGHT-30)
                    self.robot[self.keyNum-5].body.velocity = (0,0)
                    self.robot[self.keyNum-5].body.angle = (math.pi/2)
            if self.arrowState == 2:
                self.arrowState = 0
                self.arrows_list.append(arcade.create_line(self.arrowStart[0], self.arrowStart[1], self.arrowEnd[0], self.arrowEnd[1],(255,0,0),2))
                print(self.arrows_list)
            elif self.arrowState == 3:
                self.arrowState = 0
                while self.arrows_list:
                    self.arrows_list.remove(self.arrows_list[0])
            for sprite in self.dynamic_sprite_list:
                sprite.center_x = sprite.shape.body.position.x
                sprite.center_y = sprite.shape.body.position.y
                sprite.angle = math.degrees(sprite.shape.body.angle)
            return None
        
        start_time = timeit.default_timer()
        
        if rel_vec_to_point(self.robot[0].body, self.ball.body.position, self.robotAngle[0]).length < rel_vec_to_point(self.robot[1].body, self.ball.body.position, self.robotAngle[1]).length:
            self.attackRobot = 0
            self.defenceRobot = 1
        else:
            self.attackRobot = 1
            self.defenceRobot = 0
        
        ##################################################################
        """ATTACK PROGRAM"""
        if self.dribble_state[self.attackRobot] == 0:
            relVect = rel_vec_to_point(self.robot[self.attackRobot].body, self.ball.body.position, self.robotAngle[self.attackRobot])
            self.direction[self.attackRobot] = Vec2D_to_World(relVect)
            self.speed[self.attackRobot] = 600
            factor = min(0.002*(math.e**(7.1*(1-relVect.length/850))), 1.4)
            #factor = min(0.01*(1-relVect.length/850)*(math.e**(5*(1-relVect.length/850))),1)

            #obstacle avoidance
            #ref: https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm
            d = self.ball.body.position - self.robot[self.attackRobot].body.position
            r = 30
            a = d.dot(d)
            f = self.robot[self.attackRobot].body.position - self.robot[2].body.position
            b = 2*(f.dot(d))
            c = f.dot(f) - r*r
            discriminant = b*b-4*a*c
            obstaclePos = None
            if( discriminant >= 0 ):
                discriminant = math.sqrt( discriminant )
                if a == 0:
                    t1 = 2
                    t2 = 2
                else:
                    t1 = (-b - discriminant)/(2*a)
                    t2 = (-b + discriminant)/(2*a)
                if( (t1 >= 0 and t1 <= 1) and (t2 >= 0 and t2 <= 1) ):
                    obstaclePos = self.robot[2].body.position
                    print("intersect", obstaclePos)
                else:
                    print("no intersect")
            
            if obstaclePos:
                self.chase_state[self.attackRobot] = 2
            else: #no obstacles
                #check catch with back dribbler
                if self.direction[self.attackRobot] <= math.pi*0.7 or self.direction[self.attackRobot] >= math.pi*1.3:    #front half
                    self.chase_state[self.attackRobot] = 0
                else:
                    self.chase_state[self.attackRobot] = 1 #BRUH 1

            #face forward
            #self.target_point_body[self.attackRobot].angle = 2*math.pi * round(self.robot[self.attackRobot].body.angle/(2*math.pi))
            if ((self.robot[3].body.position.x-30) - 180) > ((SCREEN_WIDTH-180) - self.robot[3].body.position.x+30): #if left goal gap bigger than right goal gap
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((self.robot[3].body.position.x-30)+180)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot])
            else:
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((SCREEN_WIDTH-180) + self.robot[3].body.position.x+30)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot])
            goaldirection= Vec2D_to_World(relVect)
            if(goaldirection>math.pi*1.85 or goaldirection<math.pi*0.15):
                self.angle[self.attackRobot] = goaldirection #centre of goal
                if self.angle[self.attackRobot] > math.pi:
                    self.angle[self.attackRobot] -= math.pi*2
                self.target_point_body[self.attackRobot].angle = 2*math.pi * round(self.robot[self.attackRobot].body.angle/(2*math.pi))-self.angle[self.attackRobot]
            else:
                self.target_point_body[self.attackRobot].angle = 2*math.pi * round(self.robot[self.attackRobot].body.angle/(2*math.pi))
            ##############
        elif self.dribble_state[self.attackRobot] == 1:
            if ((self.robot[3].body.position.x-30) - 180) > ((SCREEN_WIDTH-180) - self.robot[3].body.position.x+30): #if left goal gap bigger than right goal gap
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((self.robot[3].body.position.x-30)+180)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot])
            else:
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((SCREEN_WIDTH-180) + self.robot[3].body.position.x+30)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot])
            self.direction[self.attackRobot] = Vec2D_to_World(relVect)
            self.speed[self.attackRobot] = 500
            factor = min(0.007*(math.e**(5.6*(1-relVect.length/900))), 1)
            self.chase_state[self.attackRobot] = 0
            #face goal
            if(self.direction[self.attackRobot]>math.pi*1.6 or self.direction[self.attackRobot]<math.pi*0.4):
                self.angle[self.attackRobot] = self.direction[self.attackRobot] #centre of goal
                if self.angle[self.attackRobot] > math.pi:
                    self.angle[self.attackRobot] -= math.pi*2
                self.target_point_body[self.attackRobot].angle = 2*math.pi * round(self.robot[self.attackRobot].body.angle/(2*math.pi))-self.angle[self.attackRobot]
                #shoot ball if close to goal
                if (relVect.length < 250 and relVect.length > 80) and self.robot[self.attackRobot].body.position.y < SCREEN_HEIGHT-140:
                    self.kick()
                    print("kick")
            else:
                self.target_point_body[self.attackRobot].angle = 2*math.pi * round(self.robot[self.attackRobot].body.angle/(2*math.pi))
        elif self.dribble_state[self.attackRobot] == 2:
            if ((self.robot[3].body.position.x-30) - 180) > ((SCREEN_WIDTH-180) - self.robot[3].body.position.x+30): #if left goal gap SMALLER than right goal gap
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((self.robot[3].body.position.x-30)+180)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot]) #go for smaller gap
            else:
                relVect = rel_vec_to_point(self.robot[self.attackRobot].body, (((SCREEN_WIDTH-180) + self.robot[3].body.position.x+30)/2,SCREEN_HEIGHT-78), self.robotAngle[self.attackRobot]) #go for bigger gap
            self.chase_state[self.attackRobot] = 0
            self.direction[self.attackRobot] = Vec2D_to_World(relVect)
            self.speed[self.attackRobot] = 600
            if (relVect.length < 350 and relVect.length > 50):
                if self.robot[self.attackRobot].body.position.x < SCREEN_WIDTH*0.5:
                    self.flick(0)
                else:
                    self.flick(1)
            factor = 0.0

        if self.chase_state[self.attackRobot] == 0:
            if self.direction[self.attackRobot] < math.pi:
                #offset = min(self.direction[self.attackRobot]*0.8,math.pi/2)
                offset = min(2.0*(math.e**(0.2*self.direction[self.attackRobot])-1),math.pi/2)
            else:
                #offset = max((self.direction[self.attackRobot]-math.pi*2)*0.8,-math.pi/2)
                offset = max(2.0*(math.e**(0.2*(self.direction[self.attackRobot]-math.pi*2))-1),-math.pi/2)
            self.target_point_body[self.attackRobot].velocity = make_vec_from_polar(self.speed[self.attackRobot],self.direction[self.attackRobot] + offset*factor + self.robotAngle[self.attackRobot])
        elif self.chase_state[self.attackRobot] == 1:
            self.direction[self.attackRobot] -= math.pi
            if self.direction[self.attackRobot] >= 0:
                offset = min(self.direction[self.attackRobot]*1.0,math.pi/2)
            else:
                offset = max(self.direction[self.attackRobot]*1.0,-math.pi/2)
            self.target_point_body[self.attackRobot].velocity = make_vec_from_polar(self.speed[self.attackRobot],self.direction[self.attackRobot] + math.pi + offset*factor + self.robotAngle[self.attackRobot])
        elif self.chase_state[self.attackRobot] == 2:
            obsVect = rel_vec_to_point(self.robot[self.attackRobot].body, obstaclePos, self.robotAngle[self.attackRobot])
            obsDirection = Vec2D_to_World(obsVect)
            if d.cross(f)>=0: #clockwise
                self.direction[self.attackRobot] -= math.pi/4
                print("clock")
            else: #anti-clockwise
                self.direction[self.attackRobot] += math.pi/4
                print("anti")
            self.target_point_body[self.attackRobot].velocity = make_vec_from_polar(self.speed[self.attackRobot], self.direction[self.attackRobot]+self.robotAngle[self.attackRobot])
            #pass
        ##################################################################
        """DEFENCE PROGRAM"""
        # Standard goalie
        relVect = rel_vec_to_point(self.robot[self.defenceRobot].body, (max(min(self.ball.body.position.x, 335),SCREEN_WIDTH-335),130), self.robotAngle[self.defenceRobot])
        self.direction[self.defenceRobot] = Vec2D_to_World(relVect)
        self.speed[self.defenceRobot] = 300
        self.target_point_body[self.defenceRobot].velocity = make_vec_from_polar(self.speed[self.defenceRobot],self.direction[self.defenceRobot] + self.robotAngle[self.defenceRobot])

        self.target_point_body[self.defenceRobot].angle = 2*math.pi * round(self.robot[self.defenceRobot].body.angle/(2*math.pi))
        if self.robot[self.defenceRobot].body.angle >= 0:
            self.robotAngle[self.defenceRobot] = 2*math.pi - math.fmod(self.robot[self.defenceRobot].body.angle, 2*math.pi)
        else:
            self.robotAngle[self.defenceRobot] = -math.fmod(self.robot[self.defenceRobot].body.angle, 2*math.pi)
        
        # Chase opponent robot
        """relVect = rel_vec_to_point(self.robot[self.defenceRobot].body, self.robot[2].body.position, self.robotAngle[self.defenceRobot])
        self.direction[self.defenceRobot] = Vec2D_to_World(relVect)
        self.speed[self.defenceRobot] = 450
        factor = min(0.002*(math.e**(6.7*(1-relVect.length/850))), 1)
        if (self.robot[2].body.position.x<270): #if opp robot on left
            relVect = rel_vec_to_point(self.robot[self.defenceRobot].body, (0,SCREEN_HEIGHT), self.robotAngle[self.defenceRobot])
        else:
            relVect = rel_vec_to_point(self.robot[self.defenceRobot].body, (SCREEN_WIDTH, SCREEN_HEIGHT), self.robotAngle[self.defenceRobot])
        self.angle[self.attackRobot] = Vec2D_to_World(relVect)
        if self.angle[self.attackRobot] > math.pi:
            self.angle[self.attackRobot] -= math.pi*2
        self.target_point_body[self.defenceRobot].angle = 2*math.pi * round(self.robot[self.defenceRobot].body.angle/(2*math.pi))-self.angle[self.defenceRobot]
        if self.direction[self.defenceRobot] < math.pi:
            offset = min(self.direction[self.defenceRobot]*1.0,math.pi/2)
        else:
            offset = max((self.direction[self.defenceRobot]-math.pi*2)*1.0,-math.pi/2)
        self.target_point_body[self.defenceRobot].velocity = make_vec_from_polar(self.speed[self.defenceRobot],self.direction[self.defenceRobot] + offset*factor + self.robotAngle[self.defenceRobot])"""
        ##################################################################
        """DRIBBLERS"""
        for i in range(3):
            robot_to_ball = rel_vec_to_point(self.robot[i].body, self.ball.body.position, self.robotAngle[i])
            if (Vec2D_to_World(robot_to_ball)*180/math.pi > 346 or Vec2D_to_World(robot_to_ball)*180/math.pi < 14) and robot_to_ball.length < 40:
                force = 30*rel_vec_to_point(self.ball.body, self.robot[i].body.position, self.ballAngle)
                self.ball.body.apply_force_at_local_point(force,(0,0))
                self.dribble_state[i] = 1
            elif (Vec2D_to_World(robot_to_ball)*180/math.pi > 166 and Vec2D_to_World(robot_to_ball)*180/math.pi < 194) and robot_to_ball.length < 40:
                force = 31*rel_vec_to_point(self.ball.body, self.robot[i].body.position, self.ballAngle)
                self.ball.body.apply_force_at_local_point(force,(0,0))
                self.dribble_state[i] = 2
            else:
                self.dribble_state[i] = 0
        
        ##################################################################
        relVect = rel_vec_to_point(self.robot[2].body, self.ball.body.position, self.robotAngle[2])
        self.direction[2] = Vec2D_to_World(relVect)
        self.speed[2] = 500
        factor = min(0.002*(math.e**(6.7*(1-relVect.length/850))), 1)
        self.chase_state[2] = 1
        self.direction[2] -= math.pi
        if self.direction[2] >= 0:
            offset = min(self.direction[2]*1.0,math.pi/2)
        else:
            offset = max(self.direction[2]*1.0,-math.pi/2)
        self.target_point_body[2].velocity = make_vec_from_polar(self.speed[2],self.direction[2] + math.pi + offset*factor + self.robotAngle[2])
        
        self.target_point_body[2].angle = 0
        if self.robot[2].body.angle >= 0:
            self.robotAngle[2] = 2*math.pi - math.fmod(self.robot[2].body.angle, 2*math.pi)
        else:
            self.robotAngle[2] = -math.fmod(self.robot[2].body.angle, 2*math.pi)

        relVect = rel_vec_to_point(self.robot[3].body, (max(min(self.ball.body.position.x, 335),SCREEN_WIDTH-335),600), self.robotAngle[3])
        self.direction[3] = Vec2D_to_World(relVect)
        self.speed[3] = 300
        self.target_point_body[3].velocity = make_vec_from_polar(self.speed[3],self.direction[3] + self.robotAngle[3])
        
        self.target_point_body[3].angle = 0
        if self.robot[3].body.angle >= 0:
            self.robotAngle[3] = 2*math.pi - math.fmod(self.robot[3].body.angle, 2*math.pi)
        else:
            self.robotAngle[3] = -math.fmod(self.robot[3].body.angle, 2*math.pi)
        ###########################################
        
        #out detection
        out = False
        for line in self.static_lines:
            for i in range(4):
                if line.shapes_collide(self.robot[i].shape).points:
                    collideX_a = line.shapes_collide(self.robot[i].shape).points[0].point_a[0]
                    collideX_b = line.shapes_collide(self.robot[i].shape).points[0].point_b[0]
                    collideY_a = line.shapes_collide(self.robot[i].shape).points[0].point_a[1]
                    collideY_b = line.shapes_collide(self.robot[i].shape).points[0].point_b[1]
                    
                    if (min(collideX_a,collideX_b) < 74 or max(collideX_a,collideX_b)>472):  #side detect
                        out=True
                        if (min(collideY_a,collideY_b) < 75 or max(collideY_a, collideY_b)>655):    #front/back detect
                            self.direction[i] = Vec2D_to_World(rel_vec_to_point(self.robot[i].body,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2), self.robotAngle[i]))
                            self.target_point_body[i].velocity = make_vec_from_polar(self.speed[i]*0.9, self.direction[i] + self.robotAngle[i])
                        else:   #side only
                            self.direction[i] = Vec2D_to_World(rel_vec_to_point(self.robot[i].body,(SCREEN_WIDTH/2,self.robot[i].body.position.y), self.robotAngle[i]))
                            self.target_point_body[i].velocity = make_vec_from_polar(self.speed[i]*0.9, self.direction[i] + self.robotAngle[i])
                    elif (min(collideY_a,collideY_b) < 75 or max(collideY_a, collideY_b)>655):  #front/back only
                        out=True
                        self.direction[i] = Vec2D_to_World(rel_vec_to_point(self.robot[i].body,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2), self.robotAngle[i]))
                        self.target_point_body[i].velocity = make_vec_from_polar(self.speed[i]*0.9, self.direction[i] + self.robotAngle[i])
        for arc in self.arcs:
            if arc.shapes_collide(self.robot[0].shape).points:
                out=True
                break
        #print(out)

        if self.ball.body.angle >= 0:
            self.ballAngle = 2*math.pi - math.fmod(self.ball.body.angle, 2*math.pi)
        else:
            self.ballAngle = -math.fmod(self.ball.body.angle, 2*math.pi)
        if self.robot[0].body.angle >= 0:
            self.robotAngle[0] = 2*math.pi - math.fmod(self.robot[0].body.angle, 2*math.pi)
        else:
            self.robotAngle[0] = -math.fmod(self.robot[0].body.angle, 2*math.pi)

        #user interaction
        if self.newPos:
            self.newPos = False
            if self.keyNum == 0:
                self.ball.body.position = self.mousePos
                self.ball.body.velocity = (0,0)
            elif self.keyNum >= 1 and self.keyNum <= 4:
                self.robot[self.keyNum-1].body.position = self.mousePos
                self.robot[self.keyNum-1].body.velocity = (0,0)
            elif self.keyNum == 5 or self.keyNum == 6:
                self.robot[self.keyNum-5].body.position = (SCREEN_WIDTH/2,30)
                self.robot[self.keyNum-5].body.velocity = (0,0)
                self.robot[self.keyNum-5].body.angle = (math.pi/2)
            elif self.keyNum == 7 or self.keyNum == 8:
                self.robot[self.keyNum-5].body.position = (SCREEN_WIDTH/2,SCREEN_HEIGHT-30)
                self.robot[self.keyNum-5].body.velocity = (0,0)
                self.robot[self.keyNum-5].body.angle = (math.pi/2)
        if self.arrowState == 2:
            self.arrowState = 0
            self.arrows_list.append(arcade.create_line(self.arrowStart[0], self.arrowStart[1], self.arrowEnd[0], self.arrowEnd[1],(255,0,0),2))
            print(self.arrows_list)
        elif self.arrowState == 3:
            self.arrowState = 0
            while self.arrows_list:
                self.arrows_list.remove(self.arrows_list[0])

        #slopes
        if self.ball.body.position.x <= 35:
            force = rel_vec_to_point(self.ball.body, (35,self.ball.body.position.y), self.ballAngle)
            self.ball.body.apply_force_at_local_point(force,(0,0))
        if self.ball.body.position.x >= SCREEN_WIDTH-35:
            force = rel_vec_to_point(self.ball.body, (SCREEN_WIDTH-35,self.ball.body.position.y), self.ballAngle)
            self.ball.body.apply_force_at_local_point(force,(0,0))
        if self.ball.body.position.y <= 35:
            force = rel_vec_to_point(self.ball.body, (self.ball.body.position.x,35), self.ballAngle)
            self.ball.body.apply_force_at_local_point(force,(0,0))
        if self.ball.body.position.y >= SCREEN_HEIGHT-35:
            force = rel_vec_to_point(self.ball.body, (self.ball.body.position.x,SCREEN_HEIGHT-35), self.ballAngle)
            self.ball.body.apply_force_at_local_point(force,(0,0))

        self.space.step(1 / 60.0)

        for sprite in self.dynamic_sprite_list:
            sprite.center_x = sprite.shape.body.position.x
            sprite.center_y = sprite.shape.body.position.y
            sprite.angle = math.degrees(sprite.shape.body.angle)
        
        self.processing_time = timeit.default_timer() - start_time

    def kick(self):
        if self.dribble_state[self.attackRobot] == 1:
            self.ball.body.apply_impulse_at_local_point((0,15),(0,-5))
        #elif self.dribble_state[0] == 2:
            #self.ball.body.apply_impulse_at_world_point((self.ball.body.position-self.robot[0].body.position),(self.ball.body.position.x, self.ball.body.position.y+10))

    def flick(self, dir=0):
        if self.dribble_state[self.attackRobot] == 2:
            if dir == 0:
                self.robot[self.attackRobot].body.apply_impulse_at_local_point((-40,0),(0,20))
                self.robot[self.attackRobot].body.apply_impulse_at_local_point((40,0),(0,-20))
            else:
                self.robot[self.attackRobot].body.apply_impulse_at_local_point((40,0),(0,20))
                self.robot[self.attackRobot].body.apply_impulse_at_local_point((-40,0),(0,-20))

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousePos = (x,y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.newPos = True
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.keyNum = 0
        elif button == arcade.MOUSE_BUTTON_LEFT:
            self.keyNum = 9
            if self.arrowState == 0:
                self.arrowStart = (x,y)
            elif self.arrowState == 1:
                self.arrowEnd = (x,y)
            self.arrowState += 1

    def on_key_press(self, key, modifiers):
        self.newPos = True
        if key == arcade.key.P:
            self.newPos = False
            self.pause = not self.pause
        if key == arcade.key.B:
            self.keyNum = 0
        if key == arcade.key.KEY_1:
            self.keyNum = 1
        if key == arcade.key.KEY_2:
            self.keyNum = 2
        if key == arcade.key.KEY_3:
            self.keyNum = 3
        if key == arcade.key.KEY_4:
            self.keyNum = 4
        if key == arcade.key.Q:
            self.keyNum = 5
        if key == arcade.key.W:
            self.keyNum = 6
        if key == arcade.key.E:
            self.keyNum = 7
        if key == arcade.key.R:
            self.keyNum = 8
        if key == arcade.key.ESCAPE:
            self.newPos = False
            self.arrowState = 3

def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
