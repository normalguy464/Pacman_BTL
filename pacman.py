from board import boards # import boards từ thư viện board
import pygame
import math

pygame.init()

WIDTH = 900 # có 30 ô nên để chiều rộng chia hết cho 30
HEIGHT = 950 

screen = pygame.display.set_mode([WIDTH,HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf',20)

level = boards # 32 hàng và 30 cột, boards[active_level] khi cập nhật các level khác
color = 'blue' # có thể đổi màu sắc theo từng level
PI = math.pi # hằng số pi dùng để tính toán các góc trong hình học tròn, trong trường hợp này, PI giúp xác định góc khi làm việc với cung, đường tròn

player_images = []
for i in range(1,5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'),(45,45))) #Thêm hình ảnh đã chỉnh kích thước vào danh sách player_images

# Tọa độ hiện tại của nhân vật - khi thay đổi kích thước cần tính toán lại cái này
player_x = 450
player_y = 663 

direction = 0 # hướng di chuyển, 0-RIGHT
counter = 0
flicker = False # chấm to nhấp nháy
# lần lượt theo các hướng R , L, U , D
turns_allowed = [False, False, False, False]




def draw_board():
    num1 = ((HEIGHT - 50) // 32) #Chiều cao của 1 ô
    num2 = (WIDTH//30) #Chiều rộng của 1 ô

    for i in range(len(level)):
        for j in range(len(level[i])):

            #Vẽ các chấm tròn 1 là chấm nhỏ, 2 là chấm to
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white',(j*num2 + (0.5*num2), i*num1+(0.5*num1)),4) # vẽ vòng tròn màu trắng, đưa lên màn hình, ở vị trí trung tâm theo trục X và Y, bán kính = 4 
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white',(j*num2 + (0.5*num2), i*num1+(0.5*num1)),10) #j*num2 + (0.5*num2) là tọa độ X của điểm chính giữa ô thứ j trên trục ngang (X).
            
            # Vẽ đường thẳng đứng - pygame.draw.line(screen, color, start_pos, end_post)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j*num2 + (0.5*num2),i*num1), (j*num2 +(0.5*num2),i*num1 + num1), 3 )

            # Vẽ đường nằm ngang
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j*num2 ,i*num1+(0.5*num1)), (j*num2 +num2,i*num1 + (0.5*num1)), 3 )

            # Vẽ cổng ra cho quái
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j*num2 ,i*num1+(0.5*num1)), (j*num2 +num2,i*num1 + (0.5*num1)), 3 )

            #Vẽ vòng cung - pygame.draw.arc(surface, color, rect, start_angle, end_angle, width) - các góc tính bằng radian h
            
            if level[i][j] == 5: # sô 5 vòng cung bắt đầu từ giữa bên trái và kết thúc giữa phía dưới trong 1 ô - góc phần tư thứ 1 trong vòng tròn lượng giác
                pygame.draw.arc(screen,color,[(j*num2-(num2*0.4))-2, (i*num1+(0.5*num1)),num2,num1],0,PI/2,3)
            
            if level[i][j] == 6: # sô 6 - góc phần tư thứ 2 trong vòng tròn lượng giác
                pygame.draw.arc(screen,color,[(j*num2+(num2*0.5)), (i*num1+(0.5*num1)),num2,num1],PI/2,PI,3)

            if level[i][j] == 7: # sô 7 - góc phần tư thứ 3 trong vòng tròn lượng giác
                pygame.draw.arc(screen,color,[(j*num2+(num2*0.5)), (i*num1-(0.4*num1)),num2,num1],PI,3*PI/2,3)

            if level[i][j] == 8: # sô 8  - góc phần tư thứ 4 trong vòng tròn lượng giác
                pygame.draw.arc(screen,color,[(j*num2-(num2*0.4))-2, (i*num1-(0.4*num1)),num2,num1],3*PI/2,2*PI,3)

def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x,player_y) ) ##player_images[counter // 5]: tạo ra hiệu ứng hoạt hình animation, đảm bảo nhân vật không bị đổi hình ảnh quá nhanh
    
    # Lật hình ảnh nhân vật
    if direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5],True,False), (player_x,player_y) )
    
    # Xoay hình ảnh nhân vật - 90 độ
    if direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5],90), (player_x,player_y) )

    # Xoay hình ảnh nhân vật 270 hoặc -90 độ
    if direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5],270), (player_x,player_y) )

def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT-50)//32
    num2 = (WIDTH//30)
    num3 = 15
    # Kiểm tra va chạm dựa trên centerx và centery +/- 1 vài yếu tố
    if centerx //30 < 29: # ktra nếu centerx vẫn nằm trong boards (30 ô từ 0 - 29)
        if direction == 0:
            if level[centery//num1][(centerx-num3)//num2] < 3: #Kiểm tra xem ô tiếp theo (theo hướng đi) có thể di chuyển vào hay không
                turns[1] = True # Nhân vật có thể rẽ trái ở vị trí này
                #centery // num1: Tọa độ của nv trên trục Y, chia cho num1 để ra vị trí hàng tương ứng với ma trận level
        if direction == 1:
            if level[centery//num1][(centerx+num3)//num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery+num3)//num1][centerx//num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery-num3)//num1][centerx//num2] < 3:
                turns[2] = True
        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery+num3)//num1][centerx//num2]<3:
                    turns[3] = True
                if level[(centery-num3)//num1][centerx//num2]<3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[(centery)//num1][(centerx-num2)//num2]<3:
                    turns[1] = True
                if level[(centery)//num1][(centerx+num2)//num2]<3:
                    turns[0] = True
    
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery+num1)//num1][centerx//num2]<3:
                    turns[3] = True
                if level[(centery-num1)//num1][centerx//num2]<3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[(centery)//num1][(centerx-num3)//num2]<3:
                    turns[1] = True
                if level[(centery)//num1][(centerx+num3)//num2]<3:
                    turns[0] = True
    else: #nếu vượt ra ngoài boards thì chỉ được rẽ trái or phải
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

    screen.fill('black')
    draw_board()
    draw_player()
    center_x = player_x + 23 # do đặt tỉ lệ ảnh là (45,45)
    center_y = player_y + 24
    # pygame.draw.circle(screen,'white',(center_x,center_y),2)
    turns_allowed = check_position(center_x, center_y)
    for event in pygame.event.get():

        #khi nhấn nút đỏ góc trên thì sẽ tắt
        if event.type == pygame.QUIT: 
            run = False

        # di chuyển nhân vật theo các hướng mũi tên và ADWS
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                direction = 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                direction = 1
            if event.key== pygame.K_UP or event.key == pygame.K_w:
                direction = 2
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                direction = 3
                
    pygame.display.flip()

pygame.quit()
