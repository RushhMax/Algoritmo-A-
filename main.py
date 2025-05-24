import pygame
import random
import heapq

GRID_SIZE = 15
CELL_SIZE = 40
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

# Coloresd
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (100, 100, 100)

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Carrera de Robots")

clock = pygame.time.Clock()

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbor = (current[0]+dx, current[1]+dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and grid[neighbor[0]][neighbor[1]] == 0:
                tentative_g = current_g + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
    return []

def generate_grid(prob=0.3):
    grid = [[0 if random.random() > prob else 1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    grid[0][0] = 0
    grid[GRID_SIZE-1][GRID_SIZE-1] = 0
    return grid

def draw_grid(grid, player_pos, ai_pos, goal):
    screen.fill(WHITE)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (i, j) == player_pos:
                pygame.draw.rect(screen, BLUE, rect)
            elif (i, j) == ai_pos:
                pygame.draw.rect(screen, RED, rect)
            elif (i, j) == goal:
                pygame.draw.rect(screen, GREEN, rect)
            elif grid[i][j] == 1:
                pygame.draw.rect(screen, GREY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)  # Borde

def move_player(pos, direction, grid):
    x, y = pos
    dx, dy = direction
    new_pos = (x + dx, y + dy)
    if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and grid[new_pos[0]][new_pos[1]] == 0:
        return new_pos
    return pos

# Inicializar juego
grid = generate_grid()
start = (0, 0)
goal = (GRID_SIZE-1, GRID_SIZE-1)
player_pos = start
ai_path = a_star(grid, start, goal)
ai_index = 0
ai_step_counter = 0
ai_step_delay = 40  # Cuántos frames esperar entre pasos del robot
player_step_counter = 0
player_step_delay = 10

# Loop principal
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    direction = None
    if keys[pygame.K_w]: direction = (-1, 0)
    elif keys[pygame.K_s]: direction = (1, 0)
    elif keys[pygame.K_a]: direction = (0, -1)
    elif keys[pygame.K_d]: direction = (0, 1)

    player_step_counter += 1
    if direction and player_step_counter >= player_step_delay:
        player_pos = move_player(player_pos, direction, grid)
        player_step_counter = 0

    # Movimiento A* cada cierto tiempo
    ai_step_counter += 1
    if ai_step_counter >= ai_step_delay:
        ai_step_counter = 0
        if ai_index < len(ai_path) - 1:
            ai_index += 1

    ai_pos = ai_path[ai_index] if ai_index < len(ai_path) else goal
    draw_grid(grid, player_pos, ai_pos, goal)
    pygame.display.flip()

    # Verifica ganadores
    if player_pos == goal:
        print("¡Ganaste!")
        running = False
    elif ai_pos == goal:
        print("El robot A* ganó.")
        running = False

pygame.quit()
