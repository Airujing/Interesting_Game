import pygame
import random
from collections import deque

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 生成保证连通的迷宫
def generate_connected_maze(rows, cols):
    # 初始化迷宫：1 表示墙，0 表示路径
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    visited = set()

    def carve_passages(cx, cy):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)  # 随机化方向，增加生成迷宫的随机性
        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                visited.add((nx, ny))
                maze[cx + dx][cy + dy] = 0  # 打通墙
                maze[nx][ny] = 0           # 打通路径
                carve_passages(nx, ny)

    # 以 (0, 0) 为起点
    visited.add((0, 0))
    maze[0][0] = 0
    carve_passages(0, 0)
    maze[rows - 1][cols - 1] = 0  # 确保终点可通行
    return maze

# 绘制迷宫
def draw_maze(win, maze):
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            color = WHITE if maze[row][col] == 0 else BLACK
            pygame.draw.rect(win, color, (col * cell_size, row * cell_size, cell_size, cell_size))

# 动态路径展示
def animate_path(win, path, color, maze):
    for node in path:
        pygame.time.wait(100)
        pygame.draw.rect(win, color, (node[1] * cell_size, node[0] * cell_size, cell_size, cell_size))
        pygame.display.update()

# BFS 搜索算法
def bfs(maze, start, end):
    queue = deque([start])
    visited = set()
    visited.add(start)
    parent = {start: None}
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        current = queue.popleft()
        
        if current == end:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]
        
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if (0 <= neighbor[0] < len(maze) and
                0 <= neighbor[1] < len(maze[0]) and
                maze[neighbor[0]][neighbor[1]] == 0 and
                neighbor not in visited):
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    
    return None

# 主程序
def main():
    global cell_size
    cell_size = 20
    rows, cols = 21, 21  # 使用奇数大小以确保路径可打通
    
    pygame.init()
    win = pygame.display.set_mode((cols * cell_size, rows * cell_size))
    pygame.display.set_caption("Human vs AI Pathfinding")
    clock = pygame.time.Clock()
    fps = 30

    # 生成迷宫并绘制
    maze = generate_connected_maze(rows, cols)
    draw_maze(win, maze)
    pygame.display.update()  # 更新屏幕，显示迷宫

    start = (0, 0)
    end = (rows - 1, cols - 1)

    machine_path = bfs(maze, start, end)
    player_position = start
    player_path = [player_position]
    running = True
    human_control = True  # 控制状态

    while running:
        win.fill(BLACK)
        draw_maze(win, maze)

        # 绘制玩家路径
        for node in player_path:
            pygame.draw.rect(win, GREEN, (node[1] * cell_size, node[0] * cell_size, cell_size, cell_size))

        # 显示提示信息
        font = pygame.font.SysFont(None, 24)
        if human_control:
            text = font.render("Human Control: Arrow Keys to Move", True, RED)
        else:
            text = font.render("AI Pathfinding: Machine Taking Over", True, BLUE)
        win.blit(text, (10, 10))

        pygame.display.update()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and human_control:
                if event.key == pygame.K_UP:
                    new_position = (player_position[0] - 1, player_position[1])
                elif event.key == pygame.K_DOWN:
                    new_position = (player_position[0] + 1, player_position[1])
                elif event.key == pygame.K_LEFT:
                    new_position = (player_position[0], player_position[1] - 1)
                elif event.key == pygame.K_RIGHT:
                    new_position = (player_position[0], player_position[1] + 1)
                else:
                    continue

                if (0 <= new_position[0] < rows and
                    0 <= new_position[1] < cols and
                    maze[new_position[0]][new_position[1]] == 0):
                    player_position = new_position
                    player_path.append(player_position)

                # 检查是否到达终点
                if player_position == end:
                    human_control = False

        # 机器控制部分
        if not human_control and machine_path:
            animate_path(win, machine_path, BLUE, maze)
            machine_path = None  # 防止重复动画

        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()
