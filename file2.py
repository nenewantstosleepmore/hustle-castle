import pygame
import sys
import math

empty = 0
dirt = 1
water = 2
lava = 3
stone = 4
GRAVITY = 0.5
BOUNCE_STOP = 1
pygame.init()
screen = pygame.display.set_mode((750, 600))
pygame.display.set_caption("Hustle Castle")
size = 30
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
grid_w, grid_h = WIDTH // size, HEIGHT // size
bombs = []
running = True
game_over = False
game_win = False

#load image
player_img = pygame.image.load("pic/player.png").convert_alpha()
player2_img = pygame.image.load("pic/player2.png").convert_alpha()
bomb_img = pygame.image.load("pic/bomb.png").convert_alpha()
explosion_effect_img = pygame.image.load("pic/explosion_effect.png").convert_alpha()

#resize image
player_img = pygame.transform.smoothscale(player_img, (size, size))
player2_img = pygame.transform.smoothscale(player2_img, (size, size))
bomb_img = pygame.transform.smoothscale(bomb_img, (size*0.8, size*0.8))
explosion_effect_img  = pygame.transform.smoothscale(explosion_effect_img, (size*1.2, size*1.2))

# the congratulations panel
def show_congratulations(screen):
    font_1 = pygame.font.Font("Pokemon GB.ttf", 25)
    font_2 = pygame.font.Font("Pokemon GB.ttf", 30)

    text_main = font_1.render("Congratulations! You beat the game!", True, (0, 255, 0))
    text_aura = font_2.render("plus 1000 aura", True, (0, 255, 0))

    screen.fill((0, 0, 0))

    # Calculate positions for centering the text
    text_main_x = WIDTH // 2 - text_main.get_width() // 2
    text_main_y = HEIGHT // 2 - text_main.get_height()
    text_aura_x = WIDTH // 2 - text_aura.get_width() // 2
    text_aura_y = HEIGHT // 2 + 10  # Position below the main text with some spacing

    # Blit the text to the screen
    screen.blit(text_main, (text_main_x, text_main_y))
    screen.blit(text_aura, (text_aura_x, text_aura_y))

    pygame.display.flip()

    # Wait for a key press to continue or quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Press 'Q' to quit
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:  # Press 'R' to restart
                    waiting = False  # Exit the loop and continue with the game flow

#restart button
def show_game_over(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    restart_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 50)
    pygame.draw.rect(screen, (0, 255, 0), restart_button)
    font_small = pygame.font.Font(None, 30)
    button_text = font_small.render("Restart", True, (0, 0, 0))
    screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, HEIGHT // 2 + 65))
    pygame.display.flip()
    return restart_button

class Player:
    def __init__(self, pos, player_img):
        self.pos = list(pos)
        self.mode = "DIG MODE"
        self.bomb_appear = None # bomb object
        self.image = player_img
        self.bomb_launched = False #check if the bomb is working
        self.in_air = True  # check if the player is in the air
        self.allowed_directions = {"left": True, "right": True}
        self.GRAVITY = 0.05

    def draw(self, screen):
        # Convert grid --> pixel
        pixel_x = self.pos[0] * size
        pixel_y = self.pos[1] * size

        # Draw player
        screen.blit(self.image, (pixel_x, pixel_y))

        # Draw mode text
        font = pygame.font.Font(None, 20)
        text = font.render(self.mode, True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Draw bomb and dashed line
        if self.bomb_appear and not self.bomb_launched and self.mode == "BOMB MODE":
            self.bomb_appear.draw(screen)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.draw_dashed_line(screen, self.bomb_appear.rect.center, (mouse_x, mouse_y), (255, 255, 255))

    def draw_dashed_line(self, screen, start_pos, end_pos, color, dash_length=10):
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        dash_count = int(distance / dash_length)
        for i in range(dash_count):
            if i % 2 == 0:
                x = start_pos[0] + (dx / dash_count) * i
                y = start_pos[1] + (dy / dash_count) * i
                pygame.draw.line(screen, color, (x, y), (x + dx / dash_count, y + dy / dash_count), 2)

    def switch_mode(self):
        if self.mode == "DIG MODE":
            self.mode = "BOMB MODE"
        else:
            self.mode = "DIG MODE"
        if self.mode == "BOMB MODE" and not self.bomb_appear:
            self.bomb_appear = Bomb(self.pos[0] * size + size * 0.5, self.pos[1] * size - size * 0.2, 5, 0, 0, 0.8, 0.05, bomb_img, explosion_effect_img)
        elif self.mode == "DIG MODE":
            self.bomb_appear = None

    def throw(self, target_x, target_y):
        if self.bomb_appear and not self.bomb_launched:
            dx = target_x - self.bomb_appear.x_pos
            dy = target_y - self.bomb_appear.y_pos
            self.bomb_appear.launched = True
            self.bomb_launched = True
            self.bomb_appear.x_speed = dx * self.GRAVITY
            self.bomb_appear.y_speed = dy * self.GRAVITY
            return self.bomb_appear
        return



    def update(self, fluid_logic):
        if self.in_air:
            self.pos[1] += GRAVITY

        # Check if the player is standing on dirt or stone
        grid_x, grid_y = int(self.pos[0]), int(self.pos[1])
        below_tile = fluid_logic.grid.get((grid_x, grid_y + 1))
        self.in_air = not (below_tile and below_tile.type in [dirt, stone])

        # Update allowed directions
        self.allowed_directions = {"left": True, "right": True}
        collisions = self.check_collision(fluid_logic)
        for collision in collisions:
            self.allowed_directions[collision] = False

        # Check if the player is touching lava
        self.lava_die(fluid_logic)

    def check_collision(self, fluid_logic):
        directions = {
            "left": (self.pos[0] + 0.15, self.pos[1]),
            "right": (self.pos[0] + 0.85, self.pos[1])
        }
        collisions = []

        for direction, pos in directions.items():
            grid_x = int(pos[0])
            grid_y = int(pos[1])
            if (grid_x, grid_y) in fluid_logic.grid:
                tile = fluid_logic.grid[(grid_x, grid_y)]
                if tile.type not in [empty, water]:
                    collisions.append(direction)
        return collisions

    def move(self, keys):
        if keys[pygame.K_a] and self.allowed_directions["left"]:  # Move left
            self.pos[0] -= 0.1
            self.image = player2_img
        if keys[pygame.K_d] and self.allowed_directions["right"]:  # Move right
            self.pos[0] += 0.1
            self.image = player_img

    def lava_die(self, fluid_logic):
        global game_over

        directions = {
            "bottom": (self.pos[0] * fluid_logic.size, (self.pos[1] + 1) * fluid_logic.size),
            "top": (self.pos[0] * fluid_logic.size, (self.pos[1] - 1) * fluid_logic.size),
            "left": ((self.pos[0] - 1) * fluid_logic.size, self.pos[1] * fluid_logic.size),
            "right": ((self.pos[0] + 1) * fluid_logic.size, self.pos[1] * fluid_logic.size),
        }
        # Check for collisions with lava
        for direction, pos in directions.items():
            grid_x = int(pos[0] // fluid_logic.size)
            grid_y = int(pos[1] // fluid_logic.size)
            if (grid_x, grid_y) in fluid_logic.grid:
                tile = fluid_logic.grid[(grid_x, grid_y)]
                if tile.type == lava:
                    game_over = True
                    return True
        return False


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, r,y_sp, x_sp, retention, friction, bomb_img,explosion_effect_img):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = r
        self.retention = retention
        self.y_speed = y_sp
        self.x_speed = x_sp
        self.friction = friction
        self.launched = False
        self.exploded = False
        self.time_left = 3.0
        self.image = bomb_img
        self.explosion_image = explosion_effect_img
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.explosion_warning_time = 0.1  # Time before explosion to start showing effect
        self.showing_explosion_effect = False

    def draw(self, screen):
        #bomb object
        screen.blit(self.image, self.rect)
        #explosion effect
        if self.showing_explosion_effect:
            screen.blit(self.explosion_image,self.rect)
        #timer
        font = pygame.font.Font(None, 20)
        time_text = font.render(f"{self.time_left:.1f}", True, (255, 255, 255))
        screen.blit(time_text, (self.rect.x, self.rect.y - 20))

    def check_collision(self, fluid_logic):
        directions = {
            "bottom": (self.x_pos, self.y_pos + self.radius),
            "top": (self.x_pos, self.y_pos - self.radius),
            "left": (self.x_pos - self.radius, self.y_pos),
            "right": (self.x_pos + self.radius, self.y_pos)
        }
        collisions, collisions_LAVA, collisions_WATER = [], [], []

        for direction, pos in directions.items():
            grid_x = int(pos[0] // fluid_logic.size)
            grid_y = int(pos[1] // fluid_logic.size)
            if (grid_x, grid_y) in fluid_logic.grid:
                tile = fluid_logic.grid[(grid_x, grid_y)]
                if tile.type in [dirt, stone]:
                    collisions.append(direction)
                elif tile.type == lava:
                    collisions_LAVA.append(direction)
                elif tile.type == water:
                    collisions_WATER.append(direction)

        return collisions, collisions_LAVA, collisions_WATER

    def update(self, delta_time, fluid_logic, player):
        #showing explosion  effect
        if self.time_left <= self.explosion_warning_time:
            self.showing_explosion_effect = True

        if not self.launched:
            return
        self.time_left = max(0, self.time_left - delta_time)
        if self.time_left <= 0:
            self.explode(fluid_logic, player)
            return

        self.y_speed += GRAVITY
        self.x_pos += self.x_speed
        self.y_pos += self.y_speed
        self.rect.center = (self.x_pos, self.y_pos)

        collisions, collisions_LAVA, collisions_WATER = self.check_collision(fluid_logic)
        for collision in collisions:
            if collision == "bottom":
                self.y_pos -= (self.y_speed + GRAVITY)
                self.y_speed = -self.y_speed * self.retention
            elif collision == "top":
                self.y_pos += (self.y_speed + GRAVITY)
                self.y_speed = -self.y_speed * self.retention
            elif collision == "left":
                self.x_pos += abs(self.x_speed)
                self.x_speed = -self.x_speed * self.retention
            elif collision == "right":
                self.x_pos -= abs(self.x_speed)
                self.x_speed = -self.x_speed * self.retention

        if collisions_LAVA:
            self.explode(fluid_logic, player)
        if collisions_WATER:
            self.x_speed *= 0.5
            self.y_speed *= 0.5

    def explode(self, fluid_logic, player):
        explosion_radius = 1
        grid_x = int(self.x_pos // fluid_logic.size)
        grid_y = int(self.y_pos // fluid_logic.size)
        for dx in range(-explosion_radius, explosion_radius + 1):
            for dy in range(-explosion_radius, explosion_radius + 1):
                pos = (grid_x + dx, grid_y + dy)
                if pos in fluid_logic.grid:
                    cell = fluid_logic.grid[pos]
                    if cell.type == dirt :
                        if (pos[0] ==0 or pos[0] == grid_w-1) or (pos[1]==0 or pos[1]== grid_h-1):
                            pass
                        else:
                            fluid_logic.grid[pos].set_type(empty)

        player_dist_x = abs(player.pos[0] - grid_x)
        player_dist_y = abs(player.pos[1] - grid_y)
        if player_dist_x <= explosion_radius and player_dist_y <= explosion_radius:
            global game_over
            game_over = True

        self.launched = False
        self.exploded = True  # Mark bomb as exploded
        if self.time_left == 0:
            self.showing_explosion_effect = False# Mark bomb as exploded
