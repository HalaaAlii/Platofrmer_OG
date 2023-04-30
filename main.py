import pygame
import numpy
import os
import csv
import tkinter as tk
from PIL import ImageTk, Image

WIDTH = 700
HEIGHT = 700
LEVEL = 1
temp_back = pygame.image.load("background.jpg")
BACKGROUND = pygame.transform.scale(temp_back, (700, 700))
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')


class Sprite(pygame.sprite.Sprite):
    """ base level Sprite class as per lab. no changes needed """

    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(os.path.join(img_folder, image)).convert()

        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite):
    """ player is as per lab and doesn't require any changes """

    def __init__(self, startx, starty):
        super().__init__("p1_front.png", startx, starty)
        self.stand_image = self.image
        self.jump_image = pygame.image.load(
            os.path.join(img_folder, 'p1_jump.png')).convert()

        self.walk_cycle = [pygame.image.load(f"img/p1_walk{i:0>2}.png") for i in range(1, 11)]
        self.rect.bottomleft = (startx, starty)

        self.animation_index = 0
        self.facing_left = False
        self.score = 0

        self.speed = 4
        self.jumpspeed = 20
        self.vsp = 0
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()
        self.curr_file = "11boxes.csv"
        self.removed_boxes = pygame.sprite.Group()

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, boxes):
        hsp = 0
        onground = self.check_collision(0, 1, boxes)
        # check keys
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.facing_left = True
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:
            self.facing_left = False
            self.walk_animation()
            hsp = self.speed
        else:
            self.image = self.stand_image

        if key[pygame.K_UP] and onground:
            self.vsp = -self.jumpspeed

        # variable height jumping
        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.vsp < -self.min_jumpspeed:
                self.vsp = -self.min_jumpspeed

        self.prev_key = key

        # gravity
        if self.vsp < 10 and not onground:  # 9.8 rounded up
            self.jump_animation()
            self.vsp += self.gravity

        if onground and self.vsp > 0:
            self.vsp = 0

        # movement
        self.move(hsp, self.vsp, boxes)

    def move(self, x, y, boxes):
        dx = x
        dy = y

        while self.check_collision(0, dy, boxes):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy, boxes):
            dx -= numpy.sign(dx)

        self.rect.move_ip([dx, dy])

    def check_collision(self, x, y, grounds):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, [ground for ground in grounds if ground not in self.removed_boxes])
        self.rect.move_ip([-x, -y])
        return collide

class Trophy(Sprite):
    def __init__(self, startx, starty):
        super().__init__("trophy.png", startx, starty)
        self.rect.bottomleft = (startx, starty)

    def update(self, player):
        if pygame.sprite.collide_rect(self, player):
            if LEVEL == 1:
                pygame.quit()
                play_level_two()
            if LEVEL == 2:
                pygame.quit()
                play_level_three()
            if LEVEL == 3:
                pygame.quit()

class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("boxAlt.png", startx, starty)
        self.rect.bottomleft = (startx, starty)
        self.x = startx
        self.y = starty

class Rotating_box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("folding.png", startx, starty)
        self.rect.bottomleft = (startx, starty)


def create_boxes(file, boxes, folding_boxes):
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'box':
                boxes.add(Box(int(row[1]), int(row[2])))
            elif row[0] == 'rotating':
                x, y = int(row[1]), int(row[2])
                if not any(box.x == x and box.y == y for box in boxes):
                    folding_boxes.add(Rotating_box(x, y))


def rotate(player, boxes, folding_boxes):
    # Empty the old groups
    player.removed_boxes.add(boxes)
    boxes.empty()
    player.removed_boxes.add(folding_boxes)
    folding_boxes.empty()

    if int(player.curr_file[1]) == 4:
        new_file = player.curr_file[0] + player.curr_file[0] + player.curr_file[2:]
        create_boxes(new_file, boxes, folding_boxes)
        player.curr_file = new_file
    else:
        num = int(player.curr_file[1]) + 1
        new_file = player.curr_file[0] + str(num) + player.curr_file[2:]
        create_boxes(new_file, boxes, folding_boxes)
        player.curr_file = new_file


def play_level_one():
    LEVEL = 1
    pygame.init()
    pygame.mixer.init()
    MUSIC = pygame.mixer.Sound("sound.mp3")
    MUSIC.play(-1)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player(0, 630)
    trophy = Trophy(630, 70)

    """ create some boxes for player to jump on."""
    boxes = pygame.sprite.Group()
    folding_boxes = pygame.sprite.Group()
    create_boxes('11boxes.csv', boxes, folding_boxes)
    all_boxes = pygame.sprite.Group()


    while True:
        """ update all objects"""
        pygame.event.pump()
        all_boxes.add(boxes.sprites())
        all_boxes.add(folding_boxes.sprites())
        player.update(all_boxes)
        trophy.update(player)
        screen.blit(BACKGROUND, (0, 0))
        player.draw(screen)
        trophy.draw(screen)
        boxes.draw(screen)
        folding_boxes.draw(screen)
        pygame.display.flip()

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # close pygame window
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    rotate(player, boxes, folding_boxes)

def play_level_two():
    LEVEL = 2
    pygame.init()
    pygame.mixer.init()
    MUSIC = pygame.mixer.Sound("sound.mp3")
    MUSIC.play(-1)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player(0, 630)
    trophy = Trophy(630, 70)

    """ create some boxes for player to jump on."""
    boxes = pygame.sprite.Group()
    folding_boxes = pygame.sprite.Group()
    player.curr_file = "21boxes.csv"
    create_boxes('21boxes.csv', boxes, folding_boxes)
    all_boxes = pygame.sprite.Group()

    while True:
        """ update all objects"""
        pygame.event.pump()
        all_boxes.add(boxes.sprites())
        all_boxes.add(folding_boxes.sprites())
        player.update(all_boxes)
        trophy.update(player)
        screen.blit(BACKGROUND, (0, 0))
        player.draw(screen)
        trophy.draw(screen)
        boxes.draw(screen)
        folding_boxes.draw(screen)
        pygame.display.flip()

        clock.tick(60)
        if player.rect.bottom >= 700:
            pygame.quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # close pygame window
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    rotate(player, boxes, folding_boxes)

def play_level_three():
    LEVEL = 3
    pygame.init()
    pygame.mixer.init()
    MUSIC = pygame.mixer.Sound("sound.mp3")
    MUSIC.play(-1)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player(0, 630)
    trophy = Trophy(630, 70)

    """ create some boxes for player to jump on."""
    boxes = pygame.sprite.Group()
    folding_boxes = pygame.sprite.Group()
    player.curr_file = "31boxes.csv"
    create_boxes('31boxes.csv', boxes, folding_boxes)
    all_boxes = pygame.sprite.Group()

    while True:
        """ update all objects"""
        pygame.event.pump()
        all_boxes.add(boxes.sprites())
        all_boxes.add(folding_boxes.sprites())
        player.update(all_boxes)
        trophy.update(player)
        screen.blit(BACKGROUND, (0, 0))
        player.draw(screen)
        trophy.draw(screen)
        boxes.draw(screen)
        folding_boxes.draw(screen)
        pygame.display.flip()

        clock.tick(60)
        if player.rect.bottom >= 700:
            pygame.quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # close pygame window
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    rotate(player, boxes, folding_boxes)

# create the Tkinter window
root = tk.Tk()
root.geometry("600x600")

# set up the background image
image1 = ImageTk.PhotoImage(Image.open("background.jpg"))

# set up a flag to track whether the screen has been cleared
screen_cleared = False

# create the label widget for the second screen
label2 = tk.Label(root, image=image1)
label2.place(x=0, y=0)

def clear_screen():
    global screen_cleared
    for widget in root.winfo_children():
        widget.destroy()
    screen_cleared = True

    label4 = tk.Label(root, image=image1)
    label4.place(x=0, y=0)

    # show the new widgets for the second screen
    label3 = tk.Label(root, text="Select a Level", font=("Comic Sans MS", 20), width=35)
    label3.place(relx=0.5, rely=0.2, anchor="center")

    button1 = tk.Button(root, text="Level 1", font=("Comic Sans MS", 16), width=35, command=play_level_one)
    button1.place(relx=0.5, rely=0.4, anchor="center")

    button2 = tk.Button(root, text="Level 2", font=("Comic Sans MS", 16), width=35, command=play_level_two)
    button2.place(relx=0.5, rely=0.5, anchor="center")

    button3 = tk.Button(root, text="Level 3", font=("Comic Sans MS", 16), width=35, command=play_level_three)
    button3.place(relx=0.5, rely=0.6, anchor="center")

# create the "Start Game" button
button = tk.Button(root, text="Start Game", font=("Comic Sans MS", 35), command=clear_screen, width=100, height=5)
button.place(relx=0.5, rely=0.5, anchor="center")

# start the Tkinter event loop
root.mainloop()







