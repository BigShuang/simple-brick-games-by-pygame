import pygame
import sys
import random


C, R = 11, 20  # 11列， 20行
CELL_SIZE = 40  # 格子尺寸

FPS=60  # 游戏帧率
MOVE_SPACE = 5
WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

DIRECTIONS = {
    "UP": (0, -1),  # (dc, dr)
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

CARS = {  # 车的形状，即格子位置
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
clock = pygame.time.Clock() # 用于控制循环刷新频率的对象
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

class Block(pygame.sprite.Sprite):
    def __init__(self, c, r, color):
        super().__init__()

        self.cr = [c, r]
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE

        self.image  = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(self.x, self.y)

    def move_cr(self, c, r):
        self.cr[0] = c
        self.cr[1] = r
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE
        self.rect.left = self.x
        self.rect.top = self.y

    def move(self, direction):
        dc, dr = DIRECTIONS[direction]
        next_c, next_r = self.cr[0] + dc, self.cr[1] + dr
        self.move_cr(next_c, next_r)

    def check_move(self, direction=""):
        move_c, move_r = DIRECTIONS[direction]
        next_c, next_r = self.cr[0] + move_c, self.cr[1] + move_r

        if 0 <= next_c < C and 0 <= next_r < R:
            return True

        return False

    def is_out(self):
        if 0 <= self.cr[0] < C and 0 <= self.cr[1] < R:
            return False
        return False


class Car(pygame.sprite.Group):
    def __init__(self, c, r, car_kind, car_color):
        super().__init__()

        self.kind = car_kind

        for ri, row in enumerate(CARS[self.kind]):
            for ci, cell in enumerate(row):
                if cell == 1:
                    block = Block(c+ci, r+ri, car_color)
                    self.add(block)

    def move(self, direction=""):
        if all(block.check_move(direction) for block in self.sprites()):
            self.free_move(direction)

    def free_move(self, direction=""):
        for block in self.sprites():
            block.move(direction)

    def is_out(self):
        return all(block.is_out() for block in self.sprites())


bg_color = (200, 200, 200)
enemy_color = (50, 50, 50)
player_color = (65, 105, 225)  # RoyalBlue


class EnemyManager():
    def __init__(self):
        self.enemies = []

        self.move_count = 0

    def gen_new_enemies(self):  # 生成敌人赛车
        # 设置敌人赛车的生成间隔， 隔两倍的敌人赛车行数+1
        if self.move_count % (2 * len(CARS["enemy"]) + 1) == 1:

            ec = random.randint(1, C - len(CARS["enemy"][0]))
            enemy = Car(ec, 0, "enemy", enemy_color)

            self.enemies.append(enemy)

    def move(self):  # 自动向下移动敌人赛车
        # 超出边界后，自动清理掉
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
        # 绘制敌人赛车
        for enemy in self.enemies:
            enemy.draw(master)


car = Car(5, 5, "player", player_color)
emg = EnemyManager()

frame_count = 0
while True:
    frame_count += 1

    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()  # 关闭窗口
            sys.exit()  # 停止程序

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                car.move("LEFT")
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                car.move("RIGHT")
            if event.key == pygame.K_UP or event.key == ord('w'):
                car.move("UP")
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                car.move("DOWN")

    win.fill(bg_color)

    if frame_count % MOVE_SPACE == 0:
        emg.move()

    emg.draw(win)

    car.draw(win)

    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()
