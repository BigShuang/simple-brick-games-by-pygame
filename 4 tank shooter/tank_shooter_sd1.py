import pygame
import sys
import random


C, R = 32, 24  # 11列， 20行
CELL_SIZE = 30  # 格子尺寸


FPS=60  # 游戏帧率
WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度
BULLET_SPEED = 6


DIRECTIONS = {
    "UP": (0, -1),  # (dc, dr)
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {
    "UP": "DOWN",  # (dc, dr)
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


ANGLES = {
    "UP": 0,
    "DOWN": 180,
    "LEFT": 270,
    "RIGHT": 90,
}


TANK_GRID = [  # 车的形状，即格子位置
    [0, 1, 0],
    [1, 1, 1],
    [1, 0, 1],
]


TANK_SIZE = 3


COLORS = {
    "bg": (200, 200, 200),
    "enemy": (100, 100, 100),
    "player": (150,150,150),
    "player-bullet": (165,42,42),
    "enemy-bullet": (50, 50, 50)
}


pygame.init() # pygame初始化，必须有，且必须在开头
# 创建主窗体
clock = pygame.time.Clock() # 用于控制循环刷新频率的对象
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('Tank Racing by Big Shuang')


class Block(pygame.sprite.Sprite):
    def __init__(self, c, r, color):
        super().__init__()

        self.cr = [c, r]
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE

        self.image  = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(COLORS[color])

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


class Bullet(Block):
    def __init__(self, d, c, r, color):
        super().__init__(c, r, color)
        self.d = d  # direction: UP, DOWN, LEFT, RIGHT

    def forward(self):
        self.move(self.d)

    def check_out(self):
        if self.cr[0] < 0 or self.cr[0] >= C:
            return True

        if self.cr[1] < 0 or self.cr[1] >= R:
            return True

        return False


class Tank(pygame.sprite.Group):
    def __init__(self, c, r, tank_color):
        super().__init__()

        self.color = tank_color
        self.d = "UP"
        self.cr = [c, r]
        self.blocks = [
            [None for j in range(TANK_SIZE)] for i in range(TANK_SIZE)
        ]

        for ri, row in enumerate(TANK_GRID):
            for ci, cell in enumerate(row):
                if cell == 1:
                    block = Block(c+ci, r+ri, self.color)
                    self.blocks[ri][ci] = block
                    self.add(block)

    def rotate(self, direction=""):
        if direction == "" or direction == self.d:
            return

        rotate_angle = (ANGLES[direction] - ANGLES[self.d]) % 360
        right_turns = rotate_angle // 90
        _blocks = self.blocks
        for i in range(right_turns):
            _blocks = [[k, j, i] for i, j, k in zip(*_blocks)]

        c, r = self.cr
        for ri, row in enumerate(_blocks):
            for ci, cell in enumerate(row):
                if cell is not None:
                    cell.move_cr(c + ci, r + ri)

        self.blocks = _blocks
        self.d = direction

    def move(self, direction=""):
        if self.d != direction:
            self.rotate(direction)
            return False
        elif self.check_forward():
            dcr = DIRECTIONS[direction]
            self.cr[0] += dcr[0]
            self.cr[1] += dcr[1]

            for block in self.sprites():
                block.move(direction)
            return True

        return False

    def check_forward(self):
        return all(block.check_move(self.d) for block in self.sprites())

    def back(self):
        dcr = DIRECTIONS[self.d]
        self.cr[0] -= dcr[0]
        self.cr[1] -= dcr[1]

        for block in self.sprites():
            block.move(OPPOSITE[self.d])

    def forward(self):
        self.move(self.d)

    def shoot(self):
        center = (1, 1)
        dcr = DIRECTIONS[self.d]
        shoot_c = self.cr[0] + center[0] + dcr[0]
        shoot_r = self.cr[1] + center[1] + dcr[1]
        bullet = Bullet(self.d, shoot_c, shoot_r, self.color+"-bullet")
        return bullet


class BulletManager(pygame.sprite.Group):
    def move(self):
        to_remove = []
        for bullet in self.sprites():
            bullet.forward()

            if bullet.check_out():
                to_remove.append(bullet)

        self.remove(*to_remove)

Four_Corners = {
    # position, generated tank's direction
    (0, 0): "DOWN",
    (0, R-3): "RIGHT",
    (C-3, 0): "LEFT",
    (C-3, R-3): "UP"
}

class EnemyManager:
    def __init__(self):
        self.enemies = []

    def generate_enemy(self, player):
        keys = list(Four_Corners.keys())
        random.shuffle(keys)

        for key in keys:
            kc, kr = key
            new_enemy = Tank(kc, kr, "enemy")
            if pygame.sprite.groupcollide(new_enemy, player, False, False):
                continue
            to_continue = False
            for enemy in self.enemies:
                if pygame.sprite.groupcollide(new_enemy, enemy, False, False):
                    to_continue = True
                    break
            if to_continue:
                continue

            # print("ENEMY DIRECTION: ", Four_Corners[key])
            new_enemy.rotate(Four_Corners[key])
            self.enemies.append(new_enemy)
            break

    def shoot(self):
        bullets = []
        for enemy in self.enemies:
            bullet = enemy.shoot()
            bullets.append(bullet)

        return bullets

    def move(self, player):
        for enemy in self.enemies:
            rotate = random.randint(0, 3) == 0
            if rotate:
                angel = random.choice(list(ANGLES.keys()))
                enemy.move(angel)

            moved = enemy.move(enemy.d)
            if not moved:
                continue

            if pygame.sprite.groupcollide(enemy, player, False, False):
                enemy.back()
                continue

            for other in self.enemies:
                if other != enemy and pygame.sprite.groupcollide(enemy, other, False, False):
                    enemy.back()
                    break

    def draw(self, win):
        for enemy in self.enemies:
            enemy.draw(win)


bottom_center_c = (C - len(TANK_GRID[0])) // 2
bottom_center_r = R - len(TANK_GRID)
tank = Tank(bottom_center_c, bottom_center_r, "player")
emg = EnemyManager()


BULLETS = {
    "player": BulletManager(),
    "enemy": BulletManager()
}


count = 0
while True:
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()  # 关闭窗口
            sys.exit()  # 停止程序

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                tank.move("LEFT")
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                tank.move("RIGHT")
            if event.key == pygame.K_UP or event.key == ord('w'):
                tank.move("UP")
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                tank.move("DOWN")

    win.fill(COLORS["bg"])

    if count % FPS == 0:  # 每秒生成一次子弹
        bullet = tank.shoot()
        BULLETS["player"].add(bullet)
        BULLETS["enemy"].add(*emg.shoot())


        if count % ( FPS * BULLET_SPEED ) == 0:
            emg.generate_enemy(tank)

    if count % (FPS // BULLET_SPEED) == 0:
        BULLETS["player"].move()
        BULLETS["enemy"].move()
        emg.move(tank)

    tank.draw(win)

    BULLETS["player"].draw(win)
    BULLETS["enemy"].draw(win)
    emg.draw(win)

    clock.tick(FPS)  # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    count += 1
    pygame.display.update()