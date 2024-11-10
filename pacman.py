import copy
from board import boards  # import boards từ thư viện board
import pygame
import math

pygame.init()
#khai bao kích cỡ cửa sổ
WIDTH = 900
HEIGHT = 950

#đưa ra màn hình cửa sổ đã khởi tạo
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)

level = copy.deepcopy(boards)  # 32 hàng và 30 cột, boards[active_level] khi cập nhật các level khác
color = 'blue'  #màu của tường trong map
PI = math.pi

#Thêm âm thanh

pygame.mixer.init()

pacman_beginning = pygame.mixer.Sound(f'assets/sfx/game_start.wav')
pacman_munch1 = pygame.mixer.Sound(f'assets/sfx/munch_1.wav')
pacman_munch2 = pygame.mixer.Sound(f'assets/sfx/munch_2.wav')
eating_ghost = pygame.mixer.Sound(f'assets/sfx/pacman_eatghost.wav')
power_pellet = pygame.mixer.Sound(f'assets/sfx/power_pellet_7s.mp3')
pacman_death = pygame.mixer.Sound(f'assets/sfx/death_1.wav')
munch = 0
player_images = []

for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))
    blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))
    pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
    inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
    clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))
    spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
    dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

# Tọa độ hiện tại của nhân vật
player_x = 430
player_y = 663
direction = 0 # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
blinky_x = 440
blinky_y = 330
blinky_direction = 1
inky_x = 440
inky_y = 388
inky_direction = 2
pinky_x = 440
pinky_y = 438
pinky_direction = 2
clyde_x = 390
clyde_y = 438
clyde_direction = 2
counter = 0
flicker = False  # chấm to nhấp nháy
# lần lượt theo các hướng R , L, U , D
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost=[False,False,False,False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False
moving= False
ghost_speed = [2,2,2,2]
startup_counter = 0
moving_time = 0
lives = 3
game_over = False
game_won = False

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
    def draw(self): #Vẽ hình Ghost
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect
    def check_collisions(self): #Kiểm tra va chạm với tường
        num1=((HEIGHT-50)//32)
        num2=(WIDTH//30)
        num3=15
        self.turns= [False,False,False,False]#mảng các hướng có thể di chuyển: phải, trái lên,xuống
        if 0<self.center_x//30<29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True #turn trái
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[1] = True#check có thể sang trái
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True#check có thể sang phải
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True#check có thể đi xuống
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True#check có thể đi lên

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:#check nếu gần giữa theo chiều ngang
                    #kiểm tra lại khả năng di chuyển lên xuống:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:#check nếu gần giữa theo chiều dọc
                    #kiểm tra lại khả năng di chuyển sang trái phải:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:#nếu đang di chuyển sang trái hoặc phải
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:#ktra xem có ở trong hộp không
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self): # Cam
        #Clyde sẽ rẽ theo bất kỳ hướng nào có lợi cho việc truy đuổi
        if self.direction == 0: #nếu đang hướng phải
            if self.target[0] > self.x_pos and self.turns[0]: # nếu player ở bên phải và có thể rẽ phải
                self.x_pos += self.speed
            elif not self.turns[0]: #nếu không thể rẽ phải, check các hướng di chuyển theo thứ tự:dưới(3)->trên(2)->trái(1)
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                # nếu player không nằm trong 4 hướng trên(chéo), chọn theo thứ tự 3->2->1
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: #nếu có thể đi sang phải nhưng player không ở bên phải
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1: #nếu đang hướng trái
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: #nếu có thể đi sang trái nhưng player không ở bên trái
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2: #nếu đang hướng trên
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: #nếu có thể đi lên nhưng player không ở bên trên
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3: #nếu đang hướng dưới
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: #nếu có thể đi xuống nhưng player không ở bên dưới
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30: #nếu đi ra khỏi màn hình, cửa phải
            self.x_pos = 900
        elif self.x_pos > 900: #nếu ra khỏi màn hình, cửa trái
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self): #Đỏ
        '''Blinky sẽ rẽ ngay khi va chạm với tường, và sẽ tiếp tục đi hết đoạn đường đó cho tới lần
        va chạm kế tiếp'''
        if self.direction == 0:#nếu đang hướng phải
            if self.target[0] > self.x_pos and self.turns[0]:# nếu player ở bên phải và có thể rẽ phải
                self.x_pos += self.speed
            elif not self.turns[0]:#nếu không thể rẽ phải, check các hướng di chuyển theo thứ tự:dưới(3)->trên(2)->trái(1)
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                # nếu player không nằm trong 4 hướng trên(chéo), chọn theo thứ tự 3->2->1
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]: #đi sang phải cho đến khi va chạm
                self.x_pos += self.speed
        elif self.direction == 1:#nếu đang hướng trái
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: #Đi sang trái cho đến khi va chạm
                self.x_pos -= self.speed
        elif self.direction == 2:#nếu đang hướng trên
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: #đi lên trên cho đến khi va chạm
                self.y_pos -= self.speed
        elif self.direction == 3:#nếu đang hướng dưới
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: #đi xuống dưới cho đến khi va chạm
                self.y_pos += self.speed
        if self.x_pos < -30: #nếu đi ra khỏi màn hình, cửa phải
            self.x_pos = 900
        elif self.x_pos > 900: #nếu ra khỏi màn hình, cửa trái
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self): #Xanh dương
        '''Inky có thể tự do di chuyển lên hoặc xuống để truy đuổi Pacman. Nếu không gặp vật cản,
        Inky sẽ không chủ động di chuyển theo chiều ngang'''
        if self.direction == 0:  # nếu đang hướng phải
            if self.target[0] > self.x_pos and self.turns[0]:  # nếu player ở bên phải và có thể rẽ phải
                self.x_pos += self.speed
            elif not self.turns[
                0]:  # nếu không thể rẽ phải, check các hướng di chuyển theo thứ tự:dưới(3)->trên(2)->trái(1)
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                # nếu player không nằm trong 4 hướng trên(chéo), chọn theo thứ tự 3->2->1
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # nếu có thể đi sang phải nhưng player không ở bên phải
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:  # nếu đang hướng trái
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: #Tiếp tục đi lên
                self.y_pos -= self.speed
        elif self.direction == 3:  # nếu đang hướng dưới
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: #Tiếp tục đi xuống
                self.y_pos += self.speed
        if self.x_pos < -30:  # nếu đi ra khỏi màn hình, cửa phải
            self.x_pos = 900
        elif self.x_pos > 900:  # nếu ra khỏi màn hình, cửa trái
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self): #Hồng
        '''Pinky sẽ rẽ theo hướng trái phải có lợi cho việc truy đuổi. Nếu không gặp vật cản
        Pinky sẽ không chủ động di chuyển theo chiều dọc (Ngược lại với inky)'''
        if self.direction == 0:  # nếu đang hướng phải
            if self.target[0] > self.x_pos and self.turns[0]:  # nếu player ở bên phải và có thể rẽ phải
                self.x_pos += self.speed
            elif not self.turns[
                0]:  # nếu không thể rẽ phải, check các hướng di chuyển theo thứ tự:dưới(3)->trên(2)->trái(1)
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                # nếu player không nằm trong 4 hướng trên(chéo), chọn theo thứ tự 3->2->1
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # nếu có thể đi sang phải nhưng player không ở bên phải
                self.x_pos += self.speed
        elif self.direction == 1:  # nếu đang hướng trái
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]: # nếu có thể đi sang trái nhưng player không ở bên trái
                self.x_pos -= self.speed
        elif self.direction == 2:  # nếu đang hướng trên
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]: #Nếu có thể đi lên nhưng player ko ở bên trên
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:  # nếu đang hướng dưới
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]: #nếu có thể đi xuống nhưng player không ở bên dưới
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:  # nếu đi ra khỏi màn hình, cửa phải
            self.x_pos = 900
        elif self.x_pos > 900:  # nếu ra khỏi màn hình, cửa trái
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

#Kiểm tra va chạm với các Pac-dot để ăn điểm
def collision_checking(scor, power, power_count, eaten_ghost):
    global munch
    n1=(HEIGHT - 50)//32
    n2=(WIDTH//30)
    if 0<player_x<870:
        if level[center_y//n1][center_x//n2] == 1:
            munch += 1
            if munch % 2 != 0:
                pacman_munch1.play()
            else:
                pacman_munch2.play()
            level[center_y//n1][center_x//n2] = 0
            scor += 10
        if level[center_y // n1][center_x // n2] == 2:
            munch += 1
            if munch % 2 != 0:
                pacman_munch1.play()
            else:
                pacman_munch2.play()
            level[center_y // n1][center_x // n2] = 0
            scor += 50
            power_pellet.play()
            power = True
            power_count=0
            eaten_ghost=[False,False,False,False]
    return scor, power, power_count, eaten_ghost

#In ra điểm, số mạng, trạng thái powerup
def misc_draw():
    score_text=font.render(f'Score:{score} ',True,'white')
    screen.blit(score_text, (10,920))

    if powerup:
        pygame.draw.circle(screen, 'cyan', (140,930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0],(30,30)), (650+i*40,915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10);
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10);
        gameover_text = font.render('Game over! Space bar to restart', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10);
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10);
        gameover_text = font.render('Victory! Space bar to restart', True, 'green')
        screen.blit(gameover_text, (100, 300))

#Vẽ ra map chơi
def draw_board():
    num1 = ((HEIGHT - 50) // 32)  # Chiều cao của 1 ô
    num2 = (WIDTH // 30)  # Chiều rộng của 1 ô

    for i in range(len(level)):
        for j in range(len(level[i])):

            # Vẽ các chấm tròn 1 là chấm nhỏ, 2 là chấm to
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                                   4)  # vẽ vòng tròn màu trắng, đưa lên màn hình, ở vị trí trung tâm theo trục X và Y, bán kính = 4
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                                   10)  # j*num2 + (0.5*num2) là tọa độ X của điểm chính giữa ô thứ j trên trục ngang (X).

            # Vẽ đường thẳng đứng - pygame.draw.line(screen, color, start_pos, end_post)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)

            # Vẽ đường nằm ngang
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

            # Vẽ cổng ra cho quái
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

            # Vẽ vòng cung - pygame.draw.arc(surface, color, rect, start_angle, end_angle, width) - các góc tính bằng radian h

            if level[i][
                j] == 5:  # sô 5 vòng cung bắt đầu từ giữa bên trái và kết thúc giữa phía dưới trong 1 ô - góc phần tư thứ 1 trong vòng tròn lượng giác
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)

            if level[i][j] == 6:  # sô 6 - góc phần tư thứ 2 trong vòng tròn lượng giác
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                PI / 2, PI, 3)

            if level[i][j] == 7:  # sô 7 - góc phần tư thứ 3 trong vòng tròn lượng giác
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)

            if level[i][j] == 8:  # sô 8  - góc phần tư thứ 4 trong vòng tròn lượng giác
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                3 * PI / 2, 2 * PI, 3)

#Vẽ nhân vật - Pacman
def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))

    # Lật hình ảnh nhân vật
    if direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))

    # Xoay hình ảnh nhân vật - 90 độ
    if direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))

    # Xoay hình ảnh nhân vật 270 hoặc -90 độ
    if direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

#di chuyển người chơi
def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y

#Xác định target cho các Ghost
def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:
        runaway_x = 900 #nếu người chơi đang ở bên trái bản đồ,ma sẽ chạy sang phải
    else:
        runaway_x = 0 #ngược lại sẽ chạy sang trái
    if player_y < 450:
        runaway_y = 900 #nếu người chơi đang ở phía dưới bản đồ,ma sẽ chạy lên trên
    else:
        runaway_y = 0 #ngược lại sẽ chạy xuống dưới
    return_target = (380, 400) #nếu bị ăn, ma sẽ trở về hộp
    if powerup:

        #blinky
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        #inky
        if not inky.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        #pinky
        if not pinky.dead:
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        #clyde
        if not clyde.dead and not eaten_ghost[3]:
            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        if not blinky.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]

#Kiểm tra va chạm của người chơi với tường
def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 15
    # Kiểm tra va chạm dựa trên centerx và centery +/- 1 vài yếu tố
    if centerx // 30 < 29:  # ktra nếu centerx vẫn nằm trong boards (30 ô từ 0 - 29)
        if direction == 0:
            if level[centery // num1][(
                                              centerx - num3) // num2] < 3:  # Kiểm tra xem ô tiếp theo (theo hướng đi) có thể di chuyển vào hay không
                turns[1] = True  # Nhân vật có thể rẽ trái ở vị trí này
                # centery // num1: Tọa độ của nv trên trục Y, chia cho num1 để ra vị trí hàng tương ứng với ma trận level
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True
        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[(centery) // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[(centery) // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[(centery) // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[(centery) // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:  # nếu vượt ra ngoài boards thì chỉ được rẽ trái or phải
        turns[0] = True
        turns[1] = True

    return turns


#phát âm thanh khi bắt đầu chơi
# pacman_beginning.play()
pacman_beginning.play()
run = True
while run:
    timer.tick(fps)

    # animation nhấp nháy của Pacman
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True

    # Bộ đếm thời gian khi bắt đầu và khi powerup
    if powerup and power_counter < 420:
            power_counter += 1
    elif powerup and power_counter >= 420:
            power_counter = 0
            powerup=False
            eaten_ghost= [False, False, False, False]

    if startup_counter < 300 and not game_over and not game_won:
        moving= False
        startup_counter +=1
    else:
        moving= True
    screen.fill('black')
    draw_board()

    #xác định tâm của Pacman
    center_x = player_x + 23
    center_y = player_y + 23

    #Tốc độ của Ghosts trong các trạng thái khác nhau
    if powerup:
        ghost_speed = [1, 1, 1, 1]
    else:
        ghost_speed = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speed[0] = 2
    if eaten_ghost[1]:
        ghost_speed[1] = 2
    if eaten_ghost[2]:
        ghost_speed[2] = 2
    if eaten_ghost[3]:
        ghost_speed[3] = 2
    if blinky_dead:
        ghost_speed[0] = 6
    if inky_dead:
        ghost_speed[1] = 6
    if pinky_dead:
        ghost_speed[2] = 6
    if clyde_dead:
        ghost_speed[3] = 6

    #Kiểm tra xem còn chấm nào trên màn hình không
    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False
    #Vẽ hình tròn hitbox của Pacman
    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 21, 2);
    draw_player()

    #Thiết lập thuộc tính của các Ghost
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speed[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speed[1], inky_img, inky_direction, inky_dead, inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speed[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speed[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)

    misc_draw()
    #Thiết lập mục tiêu cho các Ghost
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)
    pygame.draw.circle(screen,'white',(center_x,center_y),2)
    turns_allowed = check_position(center_x, center_y)

    if moving :
        player_x,player_y = move_player(player_x,player_y)
        moving_time += 1 #Thiết lập thời gian giãn cách giữa các Ghost
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()

        if moving_time > 180:
            if not pinky_dead and not pinky.in_box:
                pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
            else:
                pinky_x, pinky_y, pinky_direction = pinky.move_clyde()

        if moving_time > 360:
            if not inky_dead and not inky.in_box:
                inky_x, inky_y, inky_direction = inky.move_inky()
            else:
                inky_x, inky_y, inky_direction = inky.move_clyde()

        if moving_time > 540:
            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
    score, powerup, power_counter, eaten_ghost = collision_checking(score, powerup, power_counter, eaten_ghost) # check điểm, power, ma đã ăn

    #Nếu đang không ở trạng thái powerup mà va chạm với các Ghost, Pacman sẽ mất máu
    if not powerup:
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
            (player_circle.colliderect(inky.rect) and not inky.dead) or \
            (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
            (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 1:
                power_pellet.stop()
                pacman_death.play()
                lives -= 1
                moving_time = 0
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 430
                player_y = 663
                direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
                direction_command = 0
                blinky_x = 440
                blinky_y = 330
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 390
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
            else:
                game_over = True
                moving = False
                startup_counter = 0

    #Nếu trong trạng thái powerup mà ăn được Ghost, Pacman sẽ được điểm
    if powerup and player_circle.colliderect(blinky.rect) and not blinky_dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        eating_ghost.play()
        score += 200
    if powerup and player_circle.colliderect(inky.rect) and not inky_dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        eating_ghost.play()
        score += 200
    if powerup and player_circle.colliderect(pinky.rect) and not pinky_dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        eating_ghost.play()
        score += 200
    if powerup and player_circle.colliderect(clyde.rect) and not clyde_dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        eating_ghost.play()
        score += 200

    '''Sau khi đã ăn Ghost trong trạng thái powerup, các ghost sẽ trở về trạng thái bình thường,
    nếu lúc này Pacman va chạm với Ghost vẫn sẽ mất máu dù đang ở trạng thái powerup'''
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky_dead:
        if lives > 1:
            power_pellet.stop()
            pacman_death.play()
            lives -= 1
            moving_time = 0
            startup_counter = 0
            powerup = False
            power_counter = 0
            player_x = 430
            player_y = 663
            direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
            direction_command = 0
            blinky_x = 440
            blinky_y = 330
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 390
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky_dead:
        if lives > 1:
            power_pellet.stop()
            pacman_death.play()
            lives -= 1
            moving_time = 0
            startup_counter = 0
            powerup = False
            power_counter = 0
            player_x = 430
            player_y = 663
            direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
            direction_command = 0
            blinky_x = 440
            blinky_y = 330
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 390
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky_dead:
        if lives > 1:
            power_pellet.stop()
            pacman_death.play()
            lives -= 1
            moving_time = 0
            startup_counter = 0
            powerup = False
            power_counter = 0
            player_x = 430
            player_y = 663
            direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
            direction_command = 0
            blinky_x = 440
            blinky_y = 330
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 390
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde_dead:
        if lives > 1:
            power_pellet.stop()
            pacman_death.play()
            lives -= 1
            moving_time = 0
            startup_counter = 0
            powerup = False
            power_counter = 0
            player_x = 430
            player_y = 663
            direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
            direction_command = 0
            blinky_x = 440
            blinky_y = 330
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 390
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    for event in pygame.event.get():

        # khi nhấn nút đỏ góc trên thì sẽ tắt
        if event.type == pygame.QUIT:
            run = False

        # di chuyển nhân vật theo các hướng mũi tên và ADWS
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                direction_command = 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                direction_command = 1
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                direction_command = 2
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                direction_command = 3

            #Nhấn nút Space để restart game
            if event.key == pygame.K_SPACE and (game_over or game_won):
                moving_time = 0
                pacman_beginning.play()
                lives -= 1
                moving_time = 0
                power_pellet.stop()
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 430
                player_y = 663
                direction = 0  # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
                direction_command = 0
                blinky_x = 440
                blinky_y = 330
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 390
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False

    #Điều hướng Pacman
    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    #Đặt lại tọa độ của Pacman khi đi qua đường hầm
    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    #Reset trạng thái của các Ghost khi ở trong hộp (sau khi bị ăn)
    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde:
        clyde_dead  = False

    pygame.display.flip()

pygame.quit()
