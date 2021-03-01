import pygame
import sys
import random

C, R = 12, 20  # 11列， 20行

BAT_LENGTH = 4
CELL_SIZE = 40  # 格子尺寸
PADDING = 2  # 间距

FPS=20 # 游戏帧率
MOVE_SPACE = 10  # 敌人移动速度（单位，帧）

WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

COLORS = {
    "bg": (200, 200, 200),
    "player": (65, 105, 225),  # RoyalBlue
    "ball": (200, 50, 50),
    "brick": (50, 50, 50),
    "line": (225, 225, 225),
    "score": (0,128,0),  # SpringGreen
    "over": (255,0,0)
}


DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


pygame.init() # pygame初始化，必须有，且必须在开头
# 创建主窗体
clock=pygame.time.Clock() # 用于控制循环刷新频率的对象
win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

# 大中小三种字体，48,36,24
FONTS = [
    pygame.font.Font(pygame.font.get_default_font(), font_size) for font_size in [48, 36, 24]
]


class Brick(pygame.sprite.Sprite):
    def __init__(self, c, r, color="bg"):
        super().__init__()

        self.cr = [c, r]
        brick_x = c * CELL_SIZE + PADDING
        brick_y = r * CELL_SIZE + PADDING

        self.image  = pygame.Surface((CELL_SIZE - 2 * PADDING, CELL_SIZE - 2 * PADDING))
        self.image.fill(COLORS[color])

        self.rect = self.image.get_rect()

        self.rect.move_ip(brick_x, brick_y)


class BrickManager(pygame.sprite.Group):
    def __init__(self, rnum):
        super().__init__()
        for ri in range(rnum):
            for ci in range(C):
                brick = Brick(ci, ri, "brick")
                self.add(brick)


class Ball(Brick):
    def __init__(self, c, r, color="ball"):
        super().__init__(c, r, color)

        self.direction = [1, -1]

    def move(self):
        new_c = self.cr[0] + self.direction[0]
        self.cr[0] = new_c
        bat_x = new_c * CELL_SIZE + PADDING

        self.rect.left = bat_x

        new_r = self.cr[1]  + self.direction[1]
        self.cr[1] = new_r
        bat_y = new_r * CELL_SIZE + PADDING

        self.rect.top = bat_y

    def check_collide_with_wall(self):
        new_c = self.cr[0] + self.direction[0]
        if not (0 <= new_c < C):
            print("change direction 0")
            self.direction[0] = -self.direction[0]

        new_r = self.cr[1]  + self.direction[1]
        if new_r < 0:
            print("change direction 1")
            self.direction[1] = -self.direction[1]
        elif new_r >= R:
            return False

        return True


class Bat(pygame.sprite.Sprite):
    def __init__(self, c, batlen):
        super().__init__()

        self.cnum = batlen
        self.c = c
        bat_x = c * CELL_SIZE
        bat_y = ( R - 1 ) * CELL_SIZE

        self.image = pygame.Surface((CELL_SIZE * self.cnum, CELL_SIZE))
        self.image.fill(COLORS["player"])

        self.rect = self.image.get_rect()

        self.rect.move_ip(bat_x, bat_y)

    def move(self, mc):
        new_c = self.c + mc
        if 0 <= new_c <= C - self.cnum:

            self.c = new_c
            bat_x = self.c * CELL_SIZE

            self.rect.left = bat_x



bm = BrickManager(4)
bat = Bat((C - BAT_LENGTH) // 2 , BAT_LENGTH)
ball = Ball(C // 2 - 1,  R - 2)

running = True
move_c = 0

while True:
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if running:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    move_c = -1
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    move_c = 1

        elif event.type == pygame.KEYUP:
            if running:
                if (event.key == pygame.K_LEFT or event.key == ord('a')) and move_c == -1:
                    move_c = 0
                if (event.key == pygame.K_RIGHT or event.key == ord('d')) and move_c == 1:
                    move_c = 0

    if running:
        # Fill the screen with black
        win.fill(COLORS["bg"])

    bm.draw(win)

    if ball.check_collide_with_wall():
        ball.move()

    win.blit(ball.image, ball.rect)

    bat.move(move_c)
    win.blit(bat.image, bat.rect)



    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数

    pygame.display.update()
