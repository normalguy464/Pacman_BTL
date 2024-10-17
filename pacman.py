from imaplib import Flags
from symbol import power

from board import boards  # import boards từ thư viện board
import pygame
import math

pygame.init()

WIDTH = 900  # có 30 ô nên để chiều rộng chia hết cho 30
HEIGHT = 950

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)

level = boards  # 32 hàng và 30 cột, boards[active_level] khi cập nhật các level khác
color = 'blue'  # có thể đổi màu sắc theo từng level
PI = math.pi  # hằng số pi dùng để tính toán các góc trong hình học tròn, trong trường hợp này, PI giúp xác định góc khi làm việc với cung, đường tròn

player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (
    45, 45)))  # Thêm hình ảnh đã chỉnh kích thước vào danh sách player_images
blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

# Tọa độ hiện tại của nhân vật - khi thay đổi kích thước cần tính toán lại cái này
player_x = 450
player_y = 663
direction = 0 # hướng di chuyển, 0-RIGHT, 1- trái, 2 lên, 3 xuống
blinky_x = 56
blinky_y = 58
blinky_direction = 0
inky_x = 440
inky_y = 388
inky_direction = 2
pinky_x = 440
pinky_y = 438
pinky_direction = 2
clyde_x = 440
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
power_count = 0
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
startup_count=0
lives = 3
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
    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect
    def check_collisions(self):
        num1=((HEIGHT-50)//32)# khoảng cách dọc giữa các tile
        num2=(WIDTH//30)#khoảng các ngang
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

    def move_clyde(self):#cam
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
            elif self.turns[0]:#nếu có thể rẽ phải nhưng player không ở bên phải
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:#nếu đang hướng trái
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
        elif self.direction == 2:#nếu đang hướng trên
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
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
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
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:#nếu đi ra khỏi màn hình, cửa phải
            self.x_pos = 900
        elif self.x_pos > 900:#nếu ra khỏi màn hình, cửa trái
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction


def collision_checking(score, powerup, power_count, eaten_ghost):
    n1=(HEIGHT - 50)//32
    n2=(WIDTH//30)
    if 0<player_x<870:
        if level[center_y//n1][center_x//n2]==1:
            level[center_y//n1][center_x//n2] =0
            score+=10
        if level[center_y // n1][center_x // n2] == 2:
            level[center_y // n1][center_x // n2] = 0
            score += 50
            powerup = True
            power_count=0
            eaten_ghost=[False,False,False,False]
    return score, powerup, power_count, eaten_ghost

def misc_draw():
    score_text=font.render(f'Score:{score} ',True,'white')
    screen.blit(score_text, (10,920))

    if powerup:
        pygame.draw.circle(screen, 'cyan', (140,930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0],(30,30)), (650+i*40,915))

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


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x,
                                                  player_y))  ##player_images[counter // 5]: tạo ra hiệu ứng hoạt hình animation, đảm bảo nhân vật không bị đổi hình ảnh quá nhanh

    # Lật hình ảnh nhân vật
    if direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))

    # Xoay hình ảnh nhân vật - 90 độ
    if direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))

    # Xoay hình ảnh nhân vật 270 hoặc -90 độ
    if direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

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


run = True
while run:
    timer.tick(fps)

    # vòng lặp cái mồm nhấp nháy
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
        if powerup and power_count < 600:
            power_count +=1
        elif powerup and power_count >=600:
            power_count=0
            powerup=False
            eaten_ghost= [False, False, False, False]
    if startup_count < 180:
        moving= False
        startup_count +=1
    else:
        moving= True

    screen.fill('black')
    draw_board()
    draw_player()
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speed[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speed[1], inky_img, inky_direction, inky_dead, inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speed[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speed[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
    misc_draw()
    center_x = player_x + 23  # do đặt tỉ lệ ảnh là (45,45)
    center_y = player_y + 24
    pygame.draw.circle(screen,'white',(center_x,center_y),2)
    turns_allowed = check_position(center_x, center_y)
    if moving :
        player_x,player_y= move_player(player_x,player_y)
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
    score, powerup, power_count, eaten_ghost = collision_checking(score, powerup, power_count, eaten_ghost) # check điểm, power, ma đã ăn
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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    pygame.display.flip()

pygame.quit()
