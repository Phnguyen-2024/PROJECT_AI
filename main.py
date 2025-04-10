# pathfinding_game.py
import pygame
import sys
import heapq
from map_generator import generate_random_map
from utils import load_image
import random
import time

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROWS = SCREEN_HEIGHT // TILE_SIZE
COLS = SCREEN_WIDTH // TILE_SIZE
TILE_TYPES = ["G", "D", "T", "W"]

# Tile costs
TILE_COST = {
    'G': 1,
    'D': 3,
    'T': 100,
    'W': 1000
}

# Load image function
def load_image(filepath, tile_size):
    image = pygame.image.load(filepath)
    return pygame.transform.scale(image, (tile_size, tile_size))

# Map generator
def generate_random_map(rows, cols):
    return [[random.choice(TILE_TYPES) for _ in range(cols)] for _ in range(rows)]

# Neighbors
MOVE_DIRS = [(0,1),(1,0),(0,-1),(-1,0)]

def get_neighbors(pos):
    r, c = pos
    for dr, dc in MOVE_DIRS:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield (nr, nc)

# Heuristic function
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# Pathfinding algorithms

def ucs(start, goal, tilemap):
    pq = [(0, start)]
    cost = {start: 0}
    parent = {start: None}
    while pq:
        curr_cost, curr = heapq.heappop(pq)
        if curr == goal:
            break
        for neighbor in get_neighbors(curr):
            ncost = TILE_COST[tilemap[neighbor[0]][neighbor[1]]]
            total = curr_cost + ncost
            if neighbor not in cost or total < cost[neighbor]:
                cost[neighbor] = total
                heapq.heappush(pq, (total, neighbor))
                parent[neighbor] = curr
    return reconstruct_path(parent, start, goal)

def greedy(start, goal, tilemap):
    pq = [(heuristic(start, goal), start)]
    visited = set()
    parent = {start: None}
    while pq:
        _, curr = heapq.heappop(pq)
        if curr == goal:
            break
        visited.add(curr)
        for neighbor in get_neighbors(curr):
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic(neighbor, goal), neighbor))
                parent[neighbor] = curr
                visited.add(neighbor)
    return reconstruct_path(parent, start, goal)

def astar(start, goal, tilemap):
    pq = [(0 + heuristic(start, goal), 0, start)]
    cost = {start: 0}
    parent = {start: None}
    while pq:
        _, g, curr = heapq.heappop(pq)
        if curr == goal:
            break
        for neighbor in get_neighbors(curr):
            ncost = TILE_COST[tilemap[neighbor[0]][neighbor[1]]]
            new_cost = g + ncost
            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                heapq.heappush(pq, (new_cost + heuristic(neighbor, goal), new_cost, neighbor))
                parent[neighbor] = curr
    return reconstruct_path(parent, start, goal)

def reconstruct_path(parent, start, goal):
    path = []
    curr = goal
    while curr and curr in parent:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path if path and path[0] == start else []

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pathfinding Game: Auto + Manual")

# Load tile images
grass_img = load_image("D:\\tailieumonhoc\\trituenhantao\\grass.png", TILE_SIZE)
dirt_img = load_image("D:\\tailieumonhoc\\trituenhantao\\dirt.png", TILE_SIZE)
trees_img = load_image("D:\\tailieumonhoc\\trituenhantao\\tree.png", TILE_SIZE)
water_img = load_image("D:\\tailieumonhoc\\trituenhantao\\water_16px.png", TILE_SIZE)

font = pygame.font.SysFont(None, 24)
tilemap = generate_random_map(ROWS, COLS)
start = (0, 0)
goal = (ROWS - 1, COLS - 1)
current_path = []
algorithm = "UCS"
agent_index = 0
player_pos = start
control_mode = "auto"
step_count = 0
pathfinding_time = 0
completed = False
manual_step_limit = 60
manual_timer_limit = 30
manual_start_time = None

# Draw map
def draw_tilemap():
    for row in range(ROWS):
        for col in range(COLS):
            tile = tilemap[row][col]
            x, y = col*TILE_SIZE, row*TILE_SIZE
            screen.blit({'G': grass_img, 'D': dirt_img, 'T': trees_img, 'W': water_img}[tile], (x, y))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, TILE_SIZE, TILE_SIZE), 1)
    if control_mode == "auto":
        for (r, c) in current_path:
            pygame.draw.rect(screen, (255, 255, 0), (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
    pygame.draw.rect(screen, (0, 255, 0), (start[1]*TILE_SIZE, start[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)
    pygame.draw.rect(screen, (255, 0, 0), (goal[1]*TILE_SIZE, goal[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)
    px, py = player_pos
    pygame.draw.circle(screen, (0, 0, 255), (py*TILE_SIZE + TILE_SIZE//2, px*TILE_SIZE + TILE_SIZE//2), TILE_SIZE//3)
    screen.blit(font.render(f"{algorithm} | Mode: {control_mode.upper()} (M to toggle)", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Steps: {step_count}  Time: {pathfinding_time:.2f}s", True, (255, 255, 255)), (10, 35))
    if completed:
        screen.blit(font.render("🎉 WIN!", True, (255, 255, 0)), (SCREEN_WIDTH - 100, 10))

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill((0, 0, 0))
    draw_tilemap()
    pygame.display.flip()

    if control_mode == "manual" and manual_start_time is not None:
        if step_count >= manual_step_limit or time.time() - manual_start_time > manual_timer_limit:
            completed = True
    if control_mode == "auto" and agent_index < len(current_path):
        player_pos = current_path[agent_index]
        agent_index += 1
        step_count += 1
        pygame.time.wait(80)
    if player_pos == goal and not completed:
        completed = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = my // TILE_SIZE, mx // TILE_SIZE
            if tilemap[gx][gy] != 'W':
                goal = (gx, gy)
                completed = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                t0 = time.time()
                current_path = ucs(start, goal, tilemap)
                pathfinding_time = time.time() - t0
                algorithm = "UCS"
                agent_index = 0
                player_pos = start
                step_count = 0
                completed = False
            elif event.key == pygame.K_2:
                t0 = time.time()
                current_path = greedy(start, goal, tilemap)
                pathfinding_time = time.time() - t0
                algorithm = "Greedy"
                agent_index = 0
                player_pos = start
                step_count = 0
                completed = False
            elif event.key == pygame.K_3:
                t0 = time.time()
                current_path = astar(start, goal, tilemap)
                pathfinding_time = time.time() - t0
                algorithm = "A*"
                agent_index = 0
                player_pos = start
                step_count = 0
                completed = False
            elif event.key == pygame.K_r:
                tilemap = generate_random_map(ROWS, COLS)
                current_path = []
                player_pos = start
                step_count = 0
                agent_index = 0
                pathfinding_time = 0
                completed = False
            elif event.key == pygame.K_m:
                control_mode = "manual" if control_mode == "auto" else "auto"
                current_path = [] if control_mode == "manual" else current_path
                player_pos = start
                step_count = 0
                agent_index = 0
                completed = False
                manual_start_time = time.time() if control_mode == "manual" else None
            elif control_mode == "manual":
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dx = -1
                elif event.key == pygame.K_DOWN:
                    dx = 1
                elif event.key == pygame.K_LEFT:
                    dy = -1
                elif event.key == pygame.K_RIGHT:
                    dy = 1
                nx, ny = player_pos[0] + dx, player_pos[1] + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and tilemap[nx][ny] != 'W':
                    player_pos = (nx, ny)
                    step_count += 1

    clock.tick(60)

pygame.quit()
sys.exit()
