import pygame
import random
from collections import deque

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Tạo màn hình game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Trốn Tìm - Escape AI")

# Tạo mê cung ngẫu nhiên (với một số chướng ngại vật)
maze = [[0] * COLS for _ in range(ROWS)]
for _ in range(50):  # Thêm chướng ngại vật ngẫu nhiên
    x, y = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
    maze[x][y] = 1  # 1 là vật cản

# Vị trí người chơi (màu xanh)
player_pos = [ROWS - 1, COLS - 1]
maze[player_pos[0]][player_pos[1]] = 0  # Đảm bảo không đặt chướng ngại vật tại vị trí này

# Vị trí AI (màu đỏ)
ai_pos = [0, 0]
maze[ai_pos[0]][ai_pos[1]] = 0  # Đảm bảo không đặt chướng ngại vật tại vị trí này

# Tìm đường đi bằng BFS
def bfs(start, target):
    queue = deque([start])
    visited = set()
    parent = {}

    while queue:
        x, y = queue.popleft()
        if (x, y) == target:
            path = []
            while (x, y) != start:
                path.append((x, y))
                x, y = parent[(x, y)]
            return path[::-1]  # Trả về đường đi ngắn nhất

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Lên, Xuống, Trái, Phải
            nx, ny = x + dx, y + dy
            if 0 <= nx < ROWS and 0 <= ny < COLS and maze[nx][ny] == 0 and (nx, ny) not in visited:
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
    return []

# Chạy trò chơi
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Vẽ mê cung
    for i in range(ROWS):
        for j in range(COLS):
            color = BLACK if maze[i][j] == 1 else WHITE
            pygame.draw.rect(screen, color, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Vẽ người chơi
    pygame.draw.rect(screen, BLUE, (player_pos[1] * GRID_SIZE, player_pos[0] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Vẽ AI
    pygame.draw.rect(screen, RED, (ai_pos[1] * GRID_SIZE, ai_pos[0] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Xử lý sự kiện bàn phím
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_pos[0] > 0 and maze[player_pos[0] - 1][player_pos[1]] == 0:
        player_pos[0] -= 1
    if keys[pygame.K_s] and player_pos[0] < ROWS - 1 and maze[player_pos[0] + 1][player_pos[1]] == 0:
        player_pos[0] += 1
    if keys[pygame.K_a] and player_pos[1] > 0 and maze[player_pos[0]][player_pos[1] - 1] == 0:
        player_pos[1] -= 1
    if keys[pygame.K_d] and player_pos[1] < COLS - 1 and maze[player_pos[0]][player_pos[1] + 1] == 0:
        player_pos[1] += 1

    # AI tìm đường đến người chơi bằng BFS
    path = bfs(tuple(ai_pos), tuple(player_pos))
    if path:
        ai_pos = list(path[0])  # Di chuyển theo bước đầu tiên trong đường đi tìm được

    # Kiểm tra nếu AI bắt được người chơi
    if ai_pos == player_pos:
        print("AI BẮT ĐƯỢC NGƯỜI CHƠI! GAME OVER!")
        running = False

    pygame.display.flip()
    clock.tick(10)  # Giới hạn tốc độ chạy

pygame.quit()