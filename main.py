import pygame
import heapq
import random

# --- CONFIGURACIÓN AUMENTADA ---
TILE_SIZE = 80  # Aumentado de 64 a 80
WIDTH, HEIGHT = 1280, 960  # Aumentado de 1024x768 a 1280x960 (16x12 tiles)
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

pygame.init()

# --- SPRITES DE MAPA ---
floor_img = pygame.transform.scale(pygame.image.load("sprites/Floor.jpg"), (TILE_SIZE, TILE_SIZE))
wall_img = pygame.transform.scale(pygame.image.load("sprites/wall.jpg"), (TILE_SIZE, TILE_SIZE))

# --- SPRITES DEL JUGADOR ---
player_direction = "down"
player_frame = 0
PLAYER_ANIM_DELAY = 6
player_anim_counter = 0

# Cargar y escalar sprites del jugador (más grandes)
player_sprites = {
    "down": [pygame.transform.scale(pygame.image.load(f"sprites/player/down_{i}.png"), (TILE_SIZE, TILE_SIZE)) for i in range(4)],
    "up": [pygame.transform.scale(pygame.image.load(f"sprites/player/up_{i}.png"), (TILE_SIZE, TILE_SIZE)) for i in range(4)],
    "left": [pygame.transform.scale(pygame.image.load(f"sprites/player/left_{i}.png"), (TILE_SIZE, TILE_SIZE)) for i in range(4)],
    "right": [pygame.transform.scale(pygame.image.load(f"sprites/player/right_{i}.png"), (TILE_SIZE, TILE_SIZE)) for i in range(4)]
}

# --- SPRITES DE ZOMBIES (aumentados aún más) ---
ZOMBIE_SCALE = int(TILE_SIZE * 1.2)  # Zombies un 20% más grandes que el jugador
zombie_sprites = {
    "down": [pygame.transform.scale(pygame.image.load(f"sprites/zombies/Zombie1_down{i}.png"), (ZOMBIE_SCALE, ZOMBIE_SCALE)) for i in range(1, 5)],
    "up": [pygame.transform.scale(pygame.image.load(f"sprites/zombies/Zombie1_up{i}.png"), (ZOMBIE_SCALE, ZOMBIE_SCALE)) for i in range(1, 5)],
    "left": [pygame.transform.scale(pygame.image.load(f"sprites/zombies/Zombie1_left{i}.png"), (ZOMBIE_SCALE, ZOMBIE_SCALE)) for i in range(1, 5)],
    "right": [pygame.transform.scale(pygame.image.load(f"sprites/zombies/Zombie1_right{i}.png"), (ZOMBIE_SCALE, ZOMBIE_SCALE)) for i in range(1, 5)]
}

# --- PANTALLA ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Escape A* - Versión Grande")
clock = pygame.time.Clock()

player_cooldown = 0
PLAYER_DELAY = 2

# --- COLORES ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- FUNCIONES AUXILIARES ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node, grid):
    x, y = node
    neighbors = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors

def a_star(start, goal, grid):
    frontier = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in get_neighbors(current, grid):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    path = []
    curr = goal
    while curr != start and curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            if grid[y][x] == 0:
                screen.blit(floor_img, pos)
            else:
                screen.blit(wall_img, pos)

def generate_open_map():
    MAX_ATTEMPTS = 100
    for _ in range(MAX_ATTEMPTS):
        g = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        for _ in range((ROWS * COLS) // 4):
            x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
            if (x, y) not in [(1, 1), (COLS - 2, ROWS - 2), (1, ROWS - 2), (COLS - 2, 1)]:
                g[y][x] = 1

        def path_exists(a, b):
            return bool(a_star(a, b, g))

        if (path_exists((1, 1), (COLS - 2, ROWS - 2)) and
            path_exists((1, ROWS - 2), (1, 1)) and
            path_exists((COLS - 2, 1), (1, 1))):
            return g

    raise RuntimeError("No se pudo generar un mapa válido tras múltiples intentos.")

# --- PANTALLA DE INICIO ---
def show_start_screen():
    start_img = pygame.image.load("sprites/homeScreen/start.png")
    start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))

    waiting = True
    while waiting:
        screen.blit(start_img, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# --- INICIALIZACIÓN DE ENTIDADES ---
grid = generate_open_map()
player_pos = [1, 1]
exit_pos = [COLS - 2, ROWS - 2]
zombie_positions = [[1, ROWS - 2], [COLS - 2, 1]]
zombie_directions = ["down"] * len(zombie_positions)
zombie_frames = [0] * len(zombie_positions)
zombie_anim_counters = [0] * len(zombie_positions)

zombie_cooldown = 0
ZOMBIE_DELAY = 15
ZOMBIE_ANIM_DELAY = 10

# --- MOSTRAR PANTALLA DE INICIO ---
show_start_screen()

# --- LOOP PRINCIPAL ---
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento del jugador
    player_cooldown += 1
    if player_cooldown >= PLAYER_DELAY:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        direction = None
        if keys[pygame.K_LEFT]: dx, direction = -1, "left"
        elif keys[pygame.K_RIGHT]: dx, direction = 1, "right"
        elif keys[pygame.K_UP]: dy, direction = -1, "up"
        elif keys[pygame.K_DOWN]: dy, direction = 1, "down"

        new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
        if direction and 0 <= new_x < COLS and 0 <= new_y < ROWS and grid[new_y][new_x] == 0:
            player_pos = [new_x, new_y]
            player_direction = direction
            player_cooldown = 0

    # Movimiento de zombies
    zombie_cooldown += 1
    if zombie_cooldown >= ZOMBIE_DELAY:
        for i, z_pos in enumerate(zombie_positions):
            path = a_star(tuple(z_pos), tuple(player_pos), grid)
            if path:
                dx = path[0][0] - z_pos[0]
                dy = path[0][1] - z_pos[1]
                if dx == 1: direction = "right"
                elif dx == -1: direction = "left"
                elif dy == 1: direction = "down"
                elif dy == -1: direction = "up"
                else: direction = zombie_directions[i]

                zombie_positions[i] = list(path[0])
                zombie_directions[i] = direction
        zombie_cooldown = 0

    # Dibujo
    screen.fill(BLACK)
    draw_grid()

    # Jugador
    player_anim_counter += 1
    if player_anim_counter >= PLAYER_ANIM_DELAY:
        player_frame = (player_frame + 1) % len(player_sprites[player_direction])
        player_anim_counter = 0

    current_sprite = player_sprites[player_direction][player_frame]
    screen.blit(current_sprite, (player_pos[0]*TILE_SIZE, player_pos[1]*TILE_SIZE))

    # Zombies (más grandes que el jugador)
    for i, z in enumerate(zombie_positions):
        zombie_anim_counters[i] += 1
        if zombie_anim_counters[i] >= ZOMBIE_ANIM_DELAY:
            zombie_frames[i] = (zombie_frames[i] + 1) % 4
            zombie_anim_counters[i] = 0

        z_sprite = zombie_sprites[zombie_directions[i]][zombie_frames[i]]
        # Ajuste de posición para centrar los zombies más grandes
        zombie_offset = (TILE_SIZE - ZOMBIE_SCALE) // 2
        screen.blit(z_sprite, (z[0]*TILE_SIZE + zombie_offset, z[1]*TILE_SIZE + zombie_offset))

    # Salida
    pygame.draw.rect(screen, YELLOW, (exit_pos[0]*TILE_SIZE, exit_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()

    # Condición de victoria
    if player_pos == exit_pos:
        print("¡Escapaste con éxito!")
        running = False

    # Condición de derrota
    for z in zombie_positions:
        if abs(z[0] - player_pos[0]) < 0.8 and abs(z[1] - player_pos[1]) < 0.8:
            print("¡Fuiste atrapado!")
            running = False

pygame.quit()