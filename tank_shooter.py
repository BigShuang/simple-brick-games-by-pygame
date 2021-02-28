import pygame
import sys
import time
import random

C, R = 11, 20
CELL_SIZE = 40

FPS=60 # 游戏帧率
MOVE_SPACE = 10

WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

COLORS = {
    "bg": (200, 200, 200),
    "player": (65, 105, 225),  # RoyalBlue
    "enemy": (50, 50, 50),
    "line": (225, 225, 225)
}


TANKS = {
    "player": [
        [0, 1, 0],
        [1, 1, 1],
        [1, 0, 1],
    ],
    "enemy": [
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 0],
    ]
}


pygame.init() # pygame初始化，必须有，且必须在开头
# 创建主窗体
clock=pygame.time.Clock() # 用于控制循环刷新频率的对象
win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))


class Block(pygame.sprite.Sprite):
    def __init__(self, c, r, color="bg"):
        super().__init__()

        self.cr = [c, r]
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE

        self.image  = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(COLORS[color])
        # points = []
        # pygame.draw.polygon(self.image, COLOR_1, points)

        self.rect = self.image.get_rect()

        self.rect.move_ip(self.x, self.y)

    def move_cr(self, c, r):
        self.cr[0] = c
        self.cr[1] = r
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE
        self.rect.move_ip(self.x, self.y)

    def is_out(self):
        if 0 <= self.cr[0] < C and 0 <= self.cr[1] < R:
            return False
        return False

    def move(self, direction=""):
        if direction == "LEFT":
            self.cr[0] -= 1
            self.x -= CELL_SIZE
            self.rect.left = self.x
        if direction == "RIGHT":
            self.cr[0] += 1
            self.x += CELL_SIZE
            self.rect.left = self.x
        if direction == "UP" :
            self.cr[1] -= 1
            self.y -= CELL_SIZE
            self.rect.top = self.y
        if direction == "DOWN":
            self.cr[1] += 1
            self.y += CELL_SIZE
            self.rect.top = self.y

    def check_move(self, direction=""):
        if direction == "LEFT":
            if self.cr[0] <= 0:
                return False
        if direction == "RIGHT":
            if self.cr[0] >= C - 1:
                return False

        if direction == "UP":
            if self.cr[1] <= 0:
                return False

        if direction == "DOWN":
            if self.cr[1] >= R - 1:
                return False

        return True


class Tank(pygame.sprite.Group):
    def __init__(self, c, r, tank_kind):
        super().__init__()

        self.kind = tank_kind

        for ri, row in enumerate(TANKS[self.kind]):
            for ci, cell in enumerate(row):
                if cell == 1:
                    block = Block(c+ci, r+ri, tank_kind)
                    self.add(block)

    def move(self, direction=""):
        if all(block.check_move(direction) for block in self.sprites()):
            self.free_move(direction)

    def free_move(self, direction=""):
        for block in self.sprites():
            block.move(direction)

    def is_out(self):
        return all(block.is_out() for block in self.sprites())


class EnemyManager():
    def __init__(self):
        self.enemies = []

        self.move_count = 0

    def gen_new_enemies(self):
        if self.move_count % (2 * len(TANKS["enemy"]) + 1) == 1:
            ec = random.randint(1, C - len(TANKS["enemy"][0]))
            enemy = Tank(ec, 0, "enemy")

            self.enemies.append(enemy)

    def move(self):
        to_delete = []
        for i, enemy in enumerate(self.enemies):
            enemy.free_move("DOWN")
            if enemy.is_out():
                to_delete.append(i)

        for di in to_delete[::-1]:  # 倒着按序号来删除
            self.enemies.pop(di)

        self.move_count += 1

        self.gen_new_enemies()

    def draw(self, master):
        for enemy in self.enemies:
            enemy.draw(master)


bottom_center_c = (C - len(TANKS["player"][0])) // 2
bottom_center_r = R - len(TANKS["player"])
player_tank = Tank(bottom_center_c, bottom_center_r, "player")

time_count = 0

emg = EnemyManager()

while True:
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player_tank.move("LEFT")
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player_tank.move("RIGHT")
            if event.key == pygame.K_UP or event.key == ord('w'):
                player_tank.move("UP")
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                player_tank.move("DOWN")

    if (time_count + 1) % MOVE_SPACE == 0:
        emg.move()

    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    time_count += 1

    # Fill the screen with black
    win.fill(COLORS["bg"])
    for ci in range(C):
        cx = CELL_SIZE * ci
        pygame.draw.line(win, COLORS["line"], (cx, 0), (cx, R * CELL_SIZE))

    # Draw the player on the screen
    player_tank.draw(win)
    emg.draw(win)

    pygame.display.update()
