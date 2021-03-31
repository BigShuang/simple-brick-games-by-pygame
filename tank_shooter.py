import pygame
import sys

C, R = 11, 20  # 11列， 20行
CELL_SIZE = 40  # 格子尺寸

FPS=60  # 游戏帧率
WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

DIRECTIONS = {
    "UP": (0, -1),  # (dc, dr)
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

ANGLES = {
    "UP": 0,
    "DOWN": 180,
    "LEFT": 270,
    "RIGHT": 90,
}

TANKS = {  # 车的形状，即格子位置
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
TANK_SIZE = 3

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


class Bullet(Block):
    def __init__(self, d, c, r, color):
        super().__init__(c, r, color)
        self.d = d  # direction: UP, DOWN, LEFT, RIGHT

    def forward(self):
        self.move(self.d)


class Tank(pygame.sprite.Group):
    def __init__(self, c, r, tank_kind, tank_color):
        super().__init__()

        self.kind = tank_kind
        self.d = "UP"
        self.cr = [c, r]
        self.blocks = [
            [None for j in range(TANK_SIZE)] for i in range(TANK_SIZE)
        ]

        for ri, row in enumerate(TANKS[self.kind]):
            for ci, cell in enumerate(row):
                if cell == 1:
                    block = Block(c+ci, r+ri, tank_color)
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
        elif all(block.check_move(direction) for block in self.sprites()):
            dcr = DIRECTIONS[direction]
            self.cr[0] += dcr[0]
            self.cr[1] += dcr[1]

            for block in self.sprites():
                block.move(direction)

    def shoot(self):
        pass


bg_color = (200, 200, 200)
enemy_color = (50, 50, 50)
player_color = (65, 105, 225)  # RoyalBlue

bottom_center_c = (C - len(TANKS["player"][0])) // 2
bottom_center_r = R - len(TANKS["player"])
tank = Tank(bottom_center_c, bottom_center_r, "player", player_color)

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

    win.fill(bg_color)

    tank.draw(win)

    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()