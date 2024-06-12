import pygame
import math
import random
import pymunk


'''global vars'''
WIDTH = 400
HEIGHT = 400
SUGAR_PHEREOMONE_RATE = 0.2
DEPOSIT_PHEROMONE = False
collided = False
ANT_COLLISION_DICT = {}
PHEROMONE_COLLISION_DICT= {}
SUGAR_COLLISION_DICT = {}
COLONY_COLLISION_DICT = {}
#colours
BROWN1 = (124,88,53)        #rgb(124,88,53)
BROWN2 = (102,68,44)        #rgb(102,68,44)
BROWN3 = (76,43,33)         #rgb(76,43,33)
BROWN4 = (46,25,21)         #rgb(46,25,21)

class Pheromone():
    def __init__(self, strength, state, loc, angle, colour = BROWN3, expiry = 80000, ant = 0):
        self.strength = strength
        self.state = state
        self.location = loc
        self.angle = angle
        
        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = self.location
        self.shape = pymunk.Circle(self.body, 3)
        self.shape.collision_type = 2
        space.add(self.body, self.shape)

        self.creation_time = pygame.time.get_ticks()
        self.ant = ant
        
        if self.state == 'food':
            self.expiry = expiry*2
        else:
            self.expiry = expiry/2
        self.colour = colour

    def age(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.expiry:
            space.remove(self.shape, self.body)
            return 'dead'

    def draw(self):
        if self.state == 'food':
            self.colour = (255,0,0)
        pygame.draw.circle(screen, self.colour, self.location, 1)

class Sugar():
    def __init__(self, location, size):
        self.size = size
        self.location = location

        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = self.location
        self.shape = pymunk.Circle(self.body, self.size)
        self.shape.collision_type = 4
        space.add(self.body, self.shape)

    def draw(self):
        pygame.draw.circle(screen, (0,255,0), self.location, self.size+10)
    

class Ant():
    def __init__(self, colony_ID, pheromone_intensity=1, p_detect_range=1, exploration=1, speed=20, img='/Users/danielfussey/Programming/python3/simulations/ant_simulator/images/ant1.png', loc = (WIDTH/2, HEIGHT/2), angle = 0, p_state = 'exploring'):
        #global ANT_COLLISION_DICT
        self.pheromone_intensity = pheromone_intensity
        self.pheromone_detection_range = p_detect_range #max dist that pheronome can be detected
        self.exploration = exploration #how 
        self.speed = speed
        self.img = pygame.image.load(img).convert_alpha()
        self.location = loc#(WIDTH/2, HEIGHT/2)
        self.angle = angle
        self.colour = (random.randrange(66,86), random.randrange(33,53), random.randrange(23,43))
        self.colony_ID = colony_ID
        self.collided = False
        self.pheromone_state = p_state
        self.last_detected_p = pygame.time.get_ticks()
        self.collision_colour = (0,50,0)
        self.return_home = False
        self.lost_counter = pygame.time.get_ticks()
        self.away_counter = pygame.time.get_ticks() + random.randrange(-24000, 24000)
        self.following_p = 'n/a'
        self.prev_p = 'n/a'

        self.body = pymunk.Body(mass = 10, moment = 10)
        self.body.position = self.location
        self.shape = pymunk.Circle(self.body, self.pheromone_detection_range+10)
        self.shape.sensor = True
        self.shape.collision_type = 1

        self.shape2 = pymunk.Circle(self.body, self.pheromone_detection_range+3)
        self.shape2.collision_type = 3
        #self.shape.body.angle = math.radians(self.angle)
        space.add(self.body, self.shape, self.shape2)

    def update(self):
        self.move()        
        self.draw()

    def move(self):
        global colony_dict
        if self.following_p == 'n/a':#not collided:
            angle_adjust = random.randrange(-5,6)
        else:
            angle_adjust = 0#random.randrange(-1,2)
        self.location = (round(int(self.shape.body.position.x)), round(int(self.shape.body.position.y)))
        if round(math.sqrt(((colony_dict[self.colony_ID].location[0]-self.location[0])**2)+((colony_dict[self.colony_ID].location[1]-self.location[1])**2))) > WIDTH/2 or self.return_home: #add later, or if returning home
                rel_x, rel_y = colony_dict[self.colony_ID].location[0] - self.location[0], colony_dict[self.colony_ID].location[1] - self.location[1]
                angle = math.degrees(math.atan2(rel_y, rel_x))
                self.angle = (180 / math.pi) * math.degrees(math.atan2(rel_y, rel_x))
                angle_adjust = 0
                #self.colour = (255,0,0)
                
        self.angle += angle_adjust
        self.shape.body.angle = math.radians(self.angle)
        self.body.apply_impulse_at_local_point((self.speed+10, 0))

    def draw(self):
        pass
        
        pygame.draw.line(screen, (0,0,0), self.location, (self.location[0]+(math.cos(math.radians(self.angle))*50), self.location[1]+(math.sin(math.radians(self.angle))*50)))
        self.location = (round(int(self.shape.body.position.x)), round(int(self.shape.body.position.y)))
        screen.blit(pygame.transform.rotate(self.img, -self.angle+180), (self.location[0]-5, self.location[1]-3.5))
        if self.collided:
            pygame.draw.circle(screen, self.collision_colour, self.location, self.pheromone_detection_range+10, width = 1)
        if self.following_p == 'n/a':
            pygame.draw.circle(screen, (255,255,255), self.location, self.pheromone_detection_range+10, width = 2)


class Ant_Colony():
    def __init__(self, loc=(int(WIDTH/2), int(HEIGHT/2)), ID=0):
        self.size = 1
        self.total_sugar = 0
        self.ants = []
        self.pheromone_dict = {}
        self.pheromone_list = []
        self.location = loc
        self.ID = ID

        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = self.location
        self.shape = pymunk.Circle(self.body, self.total_sugar+10)
        self.shape.collision_type = 5
        space.add(self.body, self.shape)
        
    def add_ant(self, angle = 0, p_state='exploring', speed = 20):
        global ANT_COLLISION_DICT
        angle = random.randrange(0,360)
        self.ants.append(Ant(angle = angle, colony_ID = self.ID, p_state=p_state, speed = speed))
        self.size += 1
        ANT_COLLISION_DICT[self.ants[-1].shape] = [self.ants[-1]]

    def update(self):
        global DEPOSIT_PHEROMONE, PHEROMONE_COLLISION_DICT, ANT_FORGET_LAST_PHEROMONE
        dead_list = []
        for pheromone in self.pheromone_dict:
            pheromone.draw()
            if pheromone.age() == 'dead':
                dead_list.append(pheromone)
        for i in dead_list:
            self.pheromone_dict.pop(i)
        for ant in self.ants:
            
            if ant.pheromone_state != 'food' and pygame.time.get_ticks() - ant.lost_counter > 1000:
                ant.following_p = 'n/a'
                

            if pygame.time.get_ticks() - ant.away_counter > 48000 and ant.pheromone_state != 'food':
                ant.return_home = True
                #ant.last_detected_p = pygame.time.get_ticks()
                ant.pheromone_state = 'exploring'
                #print("yes", pygame.time.get_ticks(), ant.away_counter)
            #else:
            #    ant.lost = False

                #print("lost... ", ant)
            #if ANT_FORGET_LAST_PHEROMONE:
            #    ant.last_detected_p = pygame.time.get_ticks()
            ant.update()
            if DEPOSIT_PHEROMONE:
                pheromone =  Pheromone(ant.pheromone_intensity, ant.pheromone_state, (int(ant.location[0]),int(ant.location[1])), ant.angle, colour = ant.colour, ant = ant)
                self.pheromone_dict[pheromone] = [ant, ant.location, ant.colony_ID]
                PHEROMONE_COLLISION_DICT[pheromone.shape] = [pheromone]
                #self.pheromone_list.append(self.pheromone_dict[ant.location])
        pygame.draw.circle(screen, BROWN4, self.location, self.total_sugar+20)

def collide(arbiter, space, data):
    global ANT_COLLISION_DICT, PHEROMONE_COLLISION_DICT, collided
    #print(arbiter.shapes)
    ant = ANT_COLLISION_DICT[arbiter.shapes[0]][0]
    pheromone = PHEROMONE_COLLISION_DICT[arbiter.shapes[1]][0]

    if pheromone.state == 'food' and ant.pheromone_state != 'food':
    
        if ant.following_p == 'n/a':
            if ant.pheromone_state != 'food' and pheromone.state == 'food':
                ant.following_p = pheromone.ant
            elif ant.pheromone_state == 'food' and pheromone.ant == ant:
                ant.following_p = ant
            if ant.following_p != 'n/a':
                ant.prev_p = pheromone
                ant.last_detected_p = pygame.time.get_ticks()
                print("found")
                angle = pheromone.angle +180
                ant.location = pheromone.location
        else:
            angle = 'nothing'
        if ant.following_p == pheromone.ant:
            if ant.last_detected_p <= pheromone.creation_time:
                ant.last_detected_p = pheromone.creation_time
                pmone = pheromone
                ant.prev_p = pheromone
                rel_x, rel_y = ant.location[0] - pmone.location[0], ant.location[1] - pmone.location[1]
                rads = math.atan2(-rel_y, rel_x)
                rads %= 2*math.pi
                ant.angle = math.degrees(rads)
                if angle != 'nothing':
                    ant.angle = angle
            #else:
                #pmone = ant.prev_p
                #ant.angle = ant.prev_p.angle
            ant.collision_colour = (0,0,50)
            print("angle change")
        #    else:
                
                #ant.angle += 180
                #print("180")
            ant.return_home = False
        ant.collided = True
        ant.collision_colour = (50,00,0)
    #elif ant.pheromone_state == 'food':
        #
    else:
        ant.collided = False
    
    #pygame.draw.line(screen, (0,0,0), ant.location, (ant.location[0]+(math.sin(ant.angle)*50), ant.location[1]+(math.cos(ant.angle)*50)))
    return False
'''
    if pheromone.state == 'food' and ant.pheromone_state != 'food':
            ant.collided=True
            ant.collision_colour = (0,0,50)
        #if ant.last_detected_p > pheromone.creation_time:
            ant.last_detected_p = pheromone.creation_time
            ant.angle = pheromone.angle+180
            #changex = (ant.body.position.x-pheromone.body.position.x)/20
            #changey = (ant.body.position.y-pheromone.body.position.y)/20
            #ant.body.position = (ant.body.position.x-changex, ant.body.position.y-changey)
        #print("collided")
    #elif colony_dict[ant.colony_ID].pheromone_dict[pheromone][0] != ant:
    #    ant.collision_colour = (0,50,0)
    #    ant.collided=True

    elif ant.pheromone_state == 'food':
        if colony_dict[ant.colony_ID].pheromone_dict[pheromone][0] == ant and pheromone.state != 'food':
            ant.collided = True
            ant.collision_colour = (50,0,0)
            ant.lost_counter = pygame.time.get_ticks()
            ant.return_home = False
            #if ant.last_detected_p > pheromone.creation_time:# and pheromone.state != 'food':
            ant.angle = pheromone.angle+180
            changex = (ant.body.position.x-pheromone.body.position.x)/20
            changey = (ant.body.position.y-pheromone.body.position.y)/20
            ant.body.position = (ant.body.position.x-changex, ant.body.position.y-changey)
        #else:
        #    ant.pheromone_state = 'exploring'
    else:
        ant.collided=False
    return False'''

def dont_collide(arbiter, space, data):
    return False

def sugar_collide(arbiter, space, data):
    global ANT_COLLISION_DICT, SUGAR_COLLISION_DICT
    ant = ANT_COLLISION_DICT[arbiter.shapes[0]][0]
    sugar = SUGAR_COLLISION_DICT[arbiter.shapes[1]][0]
    if ant.pheromone_state != 'food':
        #sugar.size -=1
        ant.pheromone_state = 'food'
        #ant.last_detected_p = pygame.time.get_ticks()
        ant.angle += 180
        ant.following_p == 'n/a'
        #ant.lost_counter = pygame.time.get_ticks()
    return False

def colony_collide(arbiter, space, data):
    global ANT_COLLISION_DICT, COLONY_COLLISION_DICT
    ant = ANT_COLLISION_DICT[arbiter.shapes[0]][0]
    colony = COLONY_COLLISION_DICT[arbiter.shapes[1]][0]
    if ant.pheromone_state == 'food':
        ant.following_p = 'n/a'
        #colony.total_sugar += 1
        ant.pheromone_state = 'exploring'
        #ant.last_detected_p = pygame.time.get_ticks()
        ant.angle += 180
    ant.return_home = False
    ant.away_counter = pygame.time.get_ticks()
    return False

def draw_sugar():
    for sugar in SUGAR_COLLISION_DICT:
        SUGAR_COLLISION_DICT[sugar][0].draw()

colony_dict = {}

'''initialise'''
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
img = font.render("waiting...", True, BROWN4)
space = pymunk.Space()
space.damping = 0.00001


#handler.separate = exit_collision

colony = Ant_Colony(ID=1)
colony_dict[1] = (colony)
COLONY_COLLISION_DICT[colony.shape] = [colony]

#colony_dict[1].add_ant(p_state = 'food')
#colony_dict[1].add_ant(p_state = 'food', speed = 50)
for i in range(2):
    colony_dict[1].add_ant()

quarter_sec_timer = pygame.USEREVENT
pygame.time.set_timer(quarter_sec_timer, 250)
ten_sec_timer = pygame.USEREVENT +1
pygame.time.set_timer(ten_sec_timer, 10000)


handler = space.add_collision_handler(1,2)
handler.begin = collide

handler2 = space.add_collision_handler(3,2)
handler2.begin = dont_collide
handler3 = space.add_collision_handler(3,5)
handler3.begin = dont_collide

sugar_handler = space.add_collision_handler(1,4)
sugar_handler.begin = sugar_collide

colony_handler = space.add_collision_handler(1,5)
colony_handler.begin = colony_collide

#add sugar
for i in range(2):
    sugar = Sugar((WIDTH/2 +random.randrange(-(WIDTH/2)+50,(WIDTH/2) -50),HEIGHT/2 +random.randrange(-(WIDTH/2)+50, (WIDTH/2) -50)), 5)
    SUGAR_COLLISION_DICT[sugar.shape] = [sugar]

while True:
    screen.fill(BROWN2)
    pygame.draw.circle(screen, BROWN1, colony_dict[1].location, WIDTH/2, width = 3)
    DEPOSIT_PHEROMONE = False
    ANT_FORGET_LAST_PHEROMONE = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            colony_dict[1].add_ant(angle = 0)
        #if event.type == pygame.MOUSEWHEEL:
            #colony_dict[1].add_ant(p_state = 'food')
            #colony_dict[1].add_ant(angle = 90)
            #colony_dict[1].add_ant(angle = 180)
            #colony_dict[1].add_ant(angle = 270)
        if event.type == quarter_sec_timer:
            DEPOSIT_PHEROMONE = True
        if event.type == ten_sec_timer:
            ANT_FORGET_LAST_PHEROMONE = True
    img = font.render("fps:" +str(round(clock.get_fps()))+"    ants: "+str(len(colony_dict[1].ants))+"     Pheromone: "+str(len(colony_dict[1].pheromone_dict))+"   "+str(DEPOSIT_PHEROMONE), True, BROWN4)
    screen.blit(img, (20,20))
    colony_dict[1].update()
    draw_sugar()
    pygame.display.update()
    clock.tick(120)
    space.step(1/120)
