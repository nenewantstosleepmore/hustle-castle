import pygame
import sys
from file2 import Player, bombs, show_game_over, show_congratulations

empty = 0
dirt = 1
water = 2
lava = 3
stone = 4


class Tile:
    def __init__(self, type):
        self.type = type

    def set_type(self, new_type):
        self.type = new_type


class Fluidlogic:
    def __init__(self, width, height, size, grid):
        self.width = width
        self.height = height
        self.size = size
        self.grid = grid

    def flow(self):
        for pos in sorted(self.grid.keys(), key=lambda p: -p[1]):
            cell = self.grid[pos]

            direction = {'under': (pos[0], pos[1] + 1),
                         'left': (pos[0] - 1, pos[1]),
                         'right': (pos[0] + 1, pos[1])}

            if cell.type in [water, lava]:
                for dr in direction:
                    if direction[dr] in self.grid:
                        n_cell = self.grid[direction[dr]]
                        if n_cell.type == empty:
                            n_cell.set_type(cell.type)
                            cell.set_type(empty)
                            continue
        self.check_lavawater()

    def delete_dirt(self, mouseX, mouseY):
        pos_g = (mouseX // self.size, mouseY // self.size)
        if pos_g in self.grid:
            cell = self.grid[pos_g]
            if cell.type == dirt:
                cell.set_type(empty)

    def check_lavawater(self):
        for pos, cell in self.grid.items():
            if cell.type == water:
                direction = [(0, 1),  # above
                             (0, -1),  # under
                             (1, 0),  # right
                             (-1, 0)]  # left
                for dx, dy in direction:
                    near_pos = (pos[0] + dx, pos[1] + dy)
                    if near_pos in self.grid and self.grid[near_pos].type == lava:
                        self.turn_into_stone(pos)
                        cell.set_type(empty)

    def turn_into_stone(self, start_pos):
        lis = [start_pos]
        visited = set()
        while lis:
            pos = lis.pop()

            if pos in visited:
                continue
            visited.add(pos)
            cell = self.grid.get(pos)

            if cell and cell.type in [water, lava]:
                cell.set_type(stone)
                under = (pos[0], pos[1] + 1)
                left = (pos[0] - 1, pos[1])
                right = (pos[0] + 1, pos[1])

                for near in [under, left, right]:
                    if near not in visited and near in self.grid:
                        near_cell = self.grid[near]
                        if near_cell.type in [water, lava]:
                            lis.append(near)
        self.remove_water()

    def remove_water(self):
        for pos, cell in self.grid.items():
            if cell.type == water:
                cell.set_type(empty)

    def draw(self, screen):
        for pos, cell in self.grid.items():
            # Draw each tile (e.g., dirt, water, stone, etc.)
            tile_img = img[cell.type]  # Assuming 'img' is a dict of images for tile types
            screen.blit(tile_img, (pos[0] * self.size, pos[1] * self.size))


class Treasure:
    def __init__(self, pos, chest1, chest2, min_d):
        self.pos = pos
        self.can_open = False
        self.closed_chest = chest1
        self.opened_chest = chest2
        self.min_d = min_d

    def distance(self, player_pos):
        d = abs(player_pos[0] - self.pos[0] + 1) # distance btw chest and player (calculate from center of chest)
        if d <= self.min_d and player_pos[1] == self.pos[1]:
            return True  # as bool
        else:
            return False

    def open_chest(self):  # after check distance
        self.can_open = True

    def draw(self, screen):
        img = self.opened_chest if self.can_open else self.closed_chest
        screen.blit(img, (self.pos[0] * size, (self.pos[1] - 1) * size))  # from btm-left


class GameMenu:

    def __init__(self):
        pygame.init()

        # Screen dimensions
        self.screen_width = 750
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # Colors
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        # Fonts
        self.font_path = "Pokemon GB.ttf"
        self.font_size = 40
        self.font = pygame.font.Font(self.font_path, self.font_size)

        # Game states
        self.MENU = "start_menu"
        self.STAGE1 = "stage_1"
        self.STAGE2 = "stage_2"
        self.STAGE3 = "stage_3"
        self.GAME_OVER = "game_over"
        self.WIN = 'game_win'
        self.game_state = self.MENU
        self.stage = 1

        # Player and obstacle dimensions
        self.player_x = 200
        self.player_y = 400
        self.player_width = 20
        self.player_height = 20
        self.obstacle_x = 400
        self.obstacle_y = 400
        self.obstacle_width = 40
        self.obstacle_height = 40

        # Initialize stage button rectangles
        self.stage1_rect, self.stage2_rect, self.stage3_rect = self.draw_start_menu()
        # Initialize game setup
        self.setup = Stage(self.stage, self.screen_width // 30, self.screen_height // 30, 30)

    def draw_start_menu(self):
        self.screen.fill(self.black)
        title = self.font.render('Hustle Castle', True, self.white)
        stage1_button = self.font.render('Stage 1', True, self.white)
        stage2_button = self.font.render('Stage 2', True, self.white)
        stage3_button = self.font.render('Stage 3', True, self.white)

        self.screen.blit(title, (
        self.screen_width / 2 - title.get_width() / 2, self.screen_height / 4 - title.get_height() / 2))
        self.screen.blit(stage1_button, (
        self.screen_width / 2 - stage1_button.get_width() / 2, self.screen_height / 2 - stage1_button.get_height() / 2))
        self.screen.blit(stage2_button, (
        self.screen_width / 2 - stage2_button.get_width() / 2, self.screen_height / 2 + stage2_button.get_height()))
        self.screen.blit(stage3_button, (
        self.screen_width / 2 - stage3_button.get_width() / 2, self.screen_height / 2 + 2 * stage3_button.get_height()))

        pygame.display.update()

        return stage1_button.get_rect(topleft=(self.screen_width / 2 - stage1_button.get_width() / 2,
                                               self.screen_height / 2 - stage1_button.get_height() / 2)), \
            stage2_button.get_rect(topleft=(self.screen_width / 2 - stage2_button.get_width() / 2,
                                            self.screen_height / 2 + stage2_button.get_height())), \
            stage3_button.get_rect(topleft=(self.screen_width / 2 - stage3_button.get_width() / 2,
                                            self.screen_height / 2 + 2 * stage3_button.get_height()))

    def update_stage(self):
        global setup, grid, test, treasure, player, img

        # Reinitialize stage setup
        setup = Stage(self.stage, self.screen_width // 30, self.screen_height // 30, 30)
        grid = setup.setup_tile()  # Create the grid for the new stage

        # Reinitialize dependent objects
        test = Fluidlogic(setup.width, setup.height, setup.size, grid)
        treasure = Treasure(setup.get_treasure_pos(), closed_chest, opened_chest, min_d)
        player = Player(setup.get_player_pos(), player_img)

        # Update images for the selected stage
        img = load_image(self.stage)

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == self.MENU:
                    mouse_x, mouse_y = event.pos
                    if self.stage1_rect.collidepoint(mouse_x, mouse_y):
                        self.game_state = self.STAGE1
                        self.stage = 1
                        self.update_stage()
                        return
                    elif self.stage2_rect.collidepoint(mouse_x, mouse_y):
                        self.game_state = self.STAGE2
                        self.stage = 2
                        self.update_stage()
                        return
                    elif self.stage3_rect.collidepoint(mouse_x, mouse_y):
                        self.game_state = self.STAGE3
                        self.stage = 3
                        self.update_stage()
                        return

            if self.game_state == self.MENU:
                self.stage1_rect, self.stage2_rect, self.stage3_rect = self.draw_start_menu()

            elif self.game_state == self.GAME_OVER:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.game_state = self.MENU
                if keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
        pygame.quit()
        sys.exit()

class Stage:
    def __init__(self, stage, width, height, size):
        self.stage = stage
        self.width = width
        self.height = height
        self.size = size
        self.grid = {}
        self.empty_pos = []

    def stage_vary(self, stage):
        if stage == 1:
            water_pos = [(x, y) for x in range(13, 16) for y in range(2, 5)]
            lava_pos = [(x, y) for x in range(5, 11) for y in range(13, 16)]
            self.empty_pos = [(x, y) for x in range(0, 5) for y in range(6, 9)] + [(x, y) for x in range(18, self.width)
                                                                                   for y in range(9, 13)]
            self.player_pos = (4, 7)
            self.treasure_pos = (20, max([pos[1] for pos in self.empty_pos]))

        elif stage == 2:
            water_pos = [(x, y) for x in range(14, 16) for y in range(6, 8)]
            lava_pos = [(x, y) for x in range(7, 11) for y in range(9, 12)]
            self.empty_pos = [(x, y) for x in range(0, 5) for y in range(6, 9)] + [(x, y) for x in range(18, self.width)
                                                                                   for y in range(10, 13)]
            self.player_pos = (4, 7)
            self.treasure_pos = (20, max([pos[1] for pos in self.empty_pos]))

        elif stage == 3:
            water_pos = [(x, y) for x in range(12, 14) for y in range(7, 11)]
            lava_pos = [(x, y) for x in range(7, 10) for y in range(11, 14)]
            self.empty_pos = [(x, y) for x in range(0, 5) for y in range(8, 9)] + [(x, y) for x in range(18, self.width)
                                                                                   for y in range(9, 12)]
            self.player_pos = (4, 7)
            self.treasure_pos = (20, max([pos[1] for pos in self.empty_pos]))
        return water_pos, lava_pos

    def get_player_pos(self):
        return self.player_pos

    def get_treasure_pos(self):
        return self.treasure_pos

    def get_empty_pos(self):
        return self.empty_pos

    def setup_tile(self):
        self.grid = {}  # Reset grid

        # Set up the grid with dirt by default
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                self.grid[pos] = Tile(dirt)

        # Customize grid with stage-specific tiles
        water_pos, lava_pos = self.stage_vary(self.stage)
        for pos in water_pos:
            self.grid[pos].set_type(water)
        for pos in lava_pos:
            self.grid[pos].set_type(lava)
        for pos in self.empty_pos:
            self.grid[pos].set_type(empty)

        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.grid[(x, y)].set_type(stone)

        return self.grid  # Return the newly created grid

pygame.init()
screen = pygame.display.set_mode((750, 600))
pygame.display.set_caption("Hustle Castle")

size = 30
min_d = 3
grid_w = screen.get_width() // size
grid_h = screen.get_height() // size
running = True
game_over = False

game_menu = GameMenu()

#image
closed_chest = pygame.transform.smoothscale(pygame.image.load("pic/chest1.png").convert_alpha(), (size * 2, size * 2))
opened_chest = pygame.transform.smoothscale(pygame.image.load("pic/chest2.png").convert_alpha(), (size * 2, size * 2))
player_img = pygame.transform.smoothscale(pygame.image.load("pic/player.png").convert_alpha(), (size, size))
player2_img = pygame.transform.smoothscale(pygame.image.load("pic/player2.png").convert_alpha(), (size, size))
path = {empty: ["pic/empty1.png", "pic/empty2.png", "pic/empty3.png"],
        dirt: ["pic/dirt1.png", "pic/dirt2.png", "pic/dirt3.png"],
        water: "pic/water.png",
        lava: "pic/lava.png",
        stone: "pic/stone.png"}

def load_image(stage):
    return {
        empty: pygame.image.load(path[empty][stage - 1]).convert_alpha(),
        water: pygame.image.load(path[water]).convert_alpha(),
        lava: pygame.image.load(path[lava]).convert_alpha(),
        stone: pygame.image.load(path[stone]).convert_alpha(),
        dirt: pygame.image.load(path[dirt][stage - 1]).convert_alpha()
    }

img = load_image(game_menu.stage)

#init class
setup = Stage(game_menu.stage, grid_w, grid_h, size)
grid = setup.setup_tile()
test = Fluidlogic(grid_w, grid_h, size, setup.grid)
treasure = Treasure(setup.get_treasure_pos(), closed_chest, opened_chest, min_d)
player = Player(setup.get_player_pos(), player_img)
player.update(test)
player.lava_die(test)

while running:

    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    # Run the menu if in the MENU state
    if game_menu.game_state == game_menu.MENU:
        game_menu.run()
        continue  # Return to the main loop and recheck game state

    if game_over:
        game_menu.game_state = game_menu.GAME_OVER
        restart_button = show_game_over(screen, "You Lose")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):  # Check if the restart button is clicked
                    game_over = False
                    game_menu.game_state = game_menu.MENU  # Go back to the menu or reset the state
                    player = Player(setup.get_player_pos(), player_img)
                    test = Fluidlogic(grid_w, grid_h, size, setup.grid)
                    bombs.clear()  # Clear any game elements
                    break

    # Update game state when transitioning to a new stage
    if game_menu.game_state in [game_menu.STAGE1, game_menu.STAGE2, game_menu.STAGE3]:
        if setup.stage != game_menu.stage:
            game_menu.update_stage()

    dt = pygame.time.Clock().tick(60) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # opening chest
            if treasure.distance(player.pos):
                treasure.open_chest()
                if game_menu.stage < 3:
                    game_menu.stage += 1
                    game_menu.game_state = f"stage_{game_menu.stage}"
                    game_menu.update_stage()
                else:
                    # Player completed Stage 3, show the congratulations panel
                    game_menu.game_state = game_menu.WIN
                    show_congratulations(screen)
                    game_over = True
                    continue
        elif event.type == pygame.KEYDOWN and not game_over:
            # switching player mode
            if event.key == pygame.K_SPACE:
                player.switch_mode()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # throwing bomb object
            if event.button == 1 and player.mode == "BOMB MODE" and player.bomb_appear and not player.bomb_launched:
                bomb = player.throw(*pygame.mouse.get_pos())
                if bomb:
                    bombs.append(bomb)

    # Player movement and interactions
    if not game_over and player.mode == 'DIG MODE':
        keys = pygame.key.get_pressed()
        player.move(keys)
    player.update(test)

    #Player touching lava, Digging dirt and bomb update
    if not game_over and game_menu.game_state in ['stage_1','stage_2','stage_3'] :
        if player.lava_die(test):
            game_over = True
            game_menu.game_state = game_menu.GAME_OVER
        pressed = pygame.mouse.get_pressed()
        if pressed[0] and player.mode == "DIG MODE":
            test.delete_dirt(*pygame.mouse.get_pos())
        for bomb in bombs:
            if bomb.launched:
                bomb.update(dt, test, player)
            if bomb.exploded:
                bombs.remove(bomb)

        # Update and draw all components
        test.flow()
        test.draw(screen)
        treasure.draw(screen)
        player.draw(screen)
        for bomb in bombs:
            bomb.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
