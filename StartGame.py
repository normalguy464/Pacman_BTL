import pygame
import sys
import os
# Initialize Pygame
pygame.init()

# Set up display
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pac-Man Menu')

# Set up fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
HOVER_COLOR = (255, 255, 153)

# Load character images
blinky_img = pygame.image.load(f'assets/ghost_images/red.png')
pinky_img = pygame.image.load(f'assets/ghost_images/pink.png')
inky_img = pygame.image.load(f'assets/ghost_images/blue.png')
clyde_img = pygame.image.load(f'assets/ghost_images/orange.png')

# Resize images if necessary
blinky_img = pygame.transform.scale(blinky_img, (40, 40))
pinky_img = pygame.transform.scale(pinky_img, (40, 40))
inky_img = pygame.transform.scale(inky_img, (40, 40))
clyde_img = pygame.transform.scale(clyde_img, (40, 40))

# Menu options
menu_items = ['Start Game', 'Options', 'Character Info', 'Quit']
selected_item = 0  # Start with "Start Game" selected

# Button class for rounded rectangles
class MenuItem:
    def __init__(self, text, x, y, width, height, base_color, hover_color, font, radius=20):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = hover_color
        self.font = font
        self.radius = radius
        self.hovered = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=self.radius)
            self.hovered = True
        else:
            pygame.draw.rect(screen, self.base_color, self.rect, border_radius=self.radius)
            self.hovered = False

        # Render text
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_hovered(self):
        return self.hovered

# Function to render text
def render_text(text, font, color, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

# Function to display characters and their nicknames
def display_ghosts():
    ghost_list = [
        {"name": "SHADOW", "nickname": '"BLINKY"', "color": RED, "img": blinky_img},
        {"name": "SPEEDY", "nickname": '"PINKY"', "color": PINK, "img": pinky_img},
        {"name": "BASHFUL", "nickname": '"INKY"', "color": CYAN, "img": inky_img},
        {"name": "POKEY", "nickname": '"CLYDE"', "color": ORANGE, "img": clyde_img},
    ]

    # Display the header
    render_text("CHARACTER / NICKNAME", small_font, WHITE, (SCREEN_WIDTH // 2, 50))

    # Display each ghost
    for idx, ghost in enumerate(ghost_list):
        y_offset = 100 + idx * 60  # Adjust the vertical position
        screen.blit(ghost["img"], (100, y_offset))  # Display the ghost image
        render_text(ghost["name"], small_font, ghost["color"], (250, y_offset + 20))
        render_text(ghost["nickname"], small_font, ghost["color"], (400, y_offset + 20))

# Function to display points
def display_points():
    render_text("10 PTS", small_font, WHITE, (300, 400))
    render_text("50 PTS", small_font, WHITE, (300, 450))

# Menu screen function
def menu_screen():
    global selected_item

    # Create menu items with rounded corners
    menu_buttons = [
        MenuItem('Start Game', 200, 250, 200, 50, YELLOW, HOVER_COLOR, small_font),
        MenuItem('Options', 200, 310, 200, 50, YELLOW, HOVER_COLOR, small_font),
        MenuItem('Character Info', 200, 370, 200, 50, YELLOW, HOVER_COLOR, small_font),
        MenuItem('Quit', 200, 430, 200, 50, YELLOW, HOVER_COLOR, small_font)
    ]

    while True:
        screen.fill(BLACK)
        
        # Display the game title
        render_text("PAC-MAN", font, YELLOW, (SCREEN_WIDTH // 2, 100))
        
        # Draw menu items
        for button in menu_buttons:
            button.draw(screen)

        # Check for mouse click on buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_buttons)
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_buttons)
                if event.key == pygame.K_RETURN:  # Enter key pressed
                    if menu_buttons[0].is_hovered():  # Start Game
                        return 'start_game'
                    elif menu_buttons[1].is_hovered():  # Options
                        return 'Options'
                    elif menu_buttons[2].is_hovered():  # Character Info
                        return 'Character Info'
                    elif menu_buttons[3].is_hovered():  # Quit
                        pygame.quit()
                        sys.exit()

        # Check for mouse clicks
        if pygame.mouse.get_pressed()[0]:  # Left click
            for idx, button in enumerate(menu_buttons):
                if button.is_hovered():
                    if idx == 0:
                        return 'start_game'
                    elif idx == 1:
                        return 'Options'
                    elif idx == 2:
                        return 'Character Info'
                    elif idx == 3:
                        pygame.quit()
                        sys.exit()

        pygame.display.update()

# Display Options
# Tùy chọn trong game
volume = 5  # Giá trị từ 0 - 10
difficulty = 'Normal'  # Các mức độ khó có thể là 'Easy', 'Normal', 'Hard'

# Hàm hiển thị các tùy chọn trong menu Options
def show_Options():
    global volume, difficulty

    # Vị trí và kích thước của các tùy chọn
    volume_rect = pygame.Rect(150, 230, 300, 50)
    difficulty_rect = pygame.Rect(150, 290, 300, 50)
    back_rect = pygame.Rect(150, 350, 300, 50)

    selected_option = 0
    options_items = ['Volume', 'Difficulty', 'Back']
    
    while True:
        screen.fill(BLACK)
        render_text("OPTIONS", font, YELLOW, (SCREEN_WIDTH // 2, 100))

        # Hiển thị các tùy chọn
        render_text(f"Volume: {volume}", small_font, WHITE, (SCREEN_WIDTH // 2, 250))
        render_text(f"Difficulty: {difficulty}", small_font, WHITE, (SCREEN_WIDTH // 2, 310))
        render_text("Back", small_font, WHITE, (SCREEN_WIDTH // 2, 370))
        
        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()

        # Kiểm tra các sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Kiểm tra nếu click chuột
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if volume_rect.collidepoint(mouse_pos):
                    selected_option = 0
                elif difficulty_rect.collidepoint(mouse_pos):
                    selected_option = 1
                elif back_rect.collidepoint(mouse_pos):
                    selected_option = 2
            
            # Điều chỉnh volume hoặc difficulty theo click chuột
            if event.type == pygame.KEYDOWN:
                if selected_option == 0:
                    if event.key == pygame.K_LEFT and volume > 0:
                        volume -= 1
                    if event.key == pygame.K_RIGHT and volume < 10:
                        volume += 1
                elif selected_option == 1:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        if difficulty == 'Easy':
                            difficulty = 'Normal'
                        elif difficulty == 'Normal':
                            difficulty = 'Hard'
                        elif difficulty == 'Hard':
                            difficulty = 'Easy'
                elif selected_option == 2 and event.key == pygame.K_RETURN:
                    return

        # Kiểm tra nếu chuột đang hover lên các tùy chọn
        if volume_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, volume_rect, 2)  # Viền quanh "Volume"
        elif difficulty_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, difficulty_rect, 2)  # Viền quanh "Difficulty"
        elif back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, back_rect, 2)  # Viền quanh "Back"

        # Cập nhật màn hình sau mỗi vòng lặp
        pygame.display.update()

# Main function
def main():
    while True:
        selected_action = menu_screen()  # Show the menu

        if selected_action == 'start_game':
           os.system('python pacman.py') # Start game trong file pacman.py
        elif selected_action == 'Options':
            show_Options()  # Show the Options screen
        elif selected_action == 'Character Info':
            screen.fill(BLACK)
            display_ghosts()  # Show ghost information
            display_points()  # Show points information
            pygame.display.update()
            pygame.time.wait(3000)  # Wait before returning to menu

if __name__ == "__main__":
    main()
