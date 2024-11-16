import pygame
import random
from collections import deque
import time
import sys

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 定义字体颜色
TEXT_COLOR = (255, 255, 0)

# 生成随机迷宫
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if random.random() < 0.7:
                maze[i][j] = 0
            else:
                maze[i][j] = 1
    maze[0][0] = 0
    maze[rows - 1][cols - 1] = 0
    return maze

# 绘制迷宫
def draw_maze(win, maze):
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            color = WHITE if maze[row][col] == 0 else BLACK
            pygame.draw.rect(win, color, (col * cell_size, row * cell_size + top_margin, cell_size, cell_size))

# BFS搜索算法
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

# 动画路径显示
def animate_path(win, path, color):
    for node in path:
        pygame.time.wait(100)  # 每步延迟
        pygame.draw.rect(win, color, (node[1] * cell_size, node[0] * cell_size + top_margin, cell_size, cell_size))
        pygame.display.update()

# 保存当前屏幕为图片
def save_screen(win, filename):
    pygame.image.save(win, filename)

# 绘制文本信息
def draw_text(win, text, position, font, color=TEXT_COLOR):
    render_text = font.render(text, True, color)
    win.blit(render_text, position)

# 主程序
def main():
    global cell_size, top_margin
    cell_size = 20
    rows, cols = 20, 20
    top_margin = 40  # 顶部用于显示文本的间距

    pygame.init()
    win_width, win_height = cols * cell_size, rows * cell_size + top_margin
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("Human vs AI Pathfinding")
    font = pygame.font.SysFont("Arial", 20)

    human_scores = []
    ai_scores = []

    for round_num in range(1, 4):
        # 初始化迷宫
        maze = generate_maze(rows, cols)
        start = (0, 0)
        end = (rows - 1, cols - 1)

        machine_path = bfs(maze, start, end)
        if not machine_path:
            print(f"Round {round_num}: Maze is unsolvable. Regenerating...")
            continue

        player_position = start
        player_path = [player_position]
        human_control = True
        clock = pygame.time.Clock()
        fps = 30

        # 记录时间和步数
        human_start_time = time.time()
        human_steps = 0
        ai_start_time = None
        ai_steps = 0

        running = True
        while running:
            win.fill(BLACK)
            draw_maze(win, maze)

            # 绘制玩家路径
            for node in player_path:
                pygame.draw.rect(win, GREEN, (node[1] * cell_size, node[0] * cell_size + top_margin, cell_size, cell_size))

            # 绘制AI路径（机器控制阶段）
            if not human_control:
                for node in machine_path:
                    pygame.draw.rect(win, BLUE, (node[1] * cell_size, node[0] * cell_size + top_margin, cell_size, cell_size))

            # 绘制顶部文本信息
            if human_control:
                elapsed_time = time.time() - human_start_time
                draw_text(win, f"Round: {round_num} | Player Time: {elapsed_time:.2f}s | Steps: {human_steps}", (10, 10), font)
            else:
                elapsed_time = time.time() - ai_start_time if ai_start_time else 0
                draw_text(win, f"Round: {round_num} | AI Time: {elapsed_time:.2f}s | Steps: {ai_steps}", (10, 10), font)

            # 更新显示
            pygame.display.update()

            # 检测事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if human_control:
                        new_position = None
                        if event.key == pygame.K_UP:
                            new_position = (player_position[0] - 1, player_position[1])
                        elif event.key == pygame.K_DOWN:
                            new_position = (player_position[0] + 1, player_position[1])
                        elif event.key == pygame.K_LEFT:
                            new_position = (player_position[0], player_position[1] - 1)
                        elif event.key == pygame.K_RIGHT:
                            new_position = (player_position[0], player_position[1] + 1)

                        # 碰撞检测与移动逻辑
                        if (new_position and 0 <= new_position[0] < rows and
                            0 <= new_position[1] < cols and
                            maze[new_position[0]][new_position[1]] == 0):
                            player_position = new_position
                            player_path.append(player_position)
                            human_steps += 1

                        # 检查是否到达终点
                        if player_position == end:
                            human_control = False
                            human_end_time = time.time()
                            human_time = human_end_time - human_start_time

            # 切换到机器控制时，显示AI路径动画
            if not human_control:
                if ai_start_time is None:
                    ai_start_time = time.time()

                animate_path(win, machine_path, BLUE)
                ai_end_time = time.time()
                ai_time = ai_end_time - ai_start_time
                ai_steps = len(machine_path)
                running = False

            # 控制帧率
            clock.tick(fps)

        # 保存当前屏幕为图片
        save_screen(win, f"round_{round_num}_result.png")

        # 记录分数
        human_scores.append((human_time, human_steps))
        ai_scores.append((ai_time, ai_steps))
        print(f"Round {round_num} completed.")

    # 计算胜利者
    human_total = sum((10 - h[0] * 5) + (10 - h[1]) for h in human_scores) / len(human_scores)
    ai_total = sum((10 - a[0] * 5) + (10 - a[1]) for a in ai_scores) / len(ai_scores)

    if human_total > ai_total:
        print("Human wins!")
    else:
        print("AI wins!")

    pygame.quit()

if __name__ == "__main__":
    main()
