import pygame
import sys
import random

C, R = 11, 20  # 11列， 20行

FPS=20 # 游戏帧率
MOVE_SPACE = 3  # 敌人移动速度（单位，帧）

BAT_LENGTH = 6
BRICK_LAYER = 4


CELL_SIZE = 40  # 格子尺寸
PADDING = 2  # 间距


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
pygame.display.set_caption('Pong Breakout by Big Shuang')


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

    def check_hit(self, ball):
        ball_cr = tuple(ball.cr)
        for brick in self.sprites():
            if tuple(brick.cr) == ball_cr:
                self.remove(brick)
                return True

        return False


class Ball(Brick):
    def __init__(self, c, r, color="ball"):
        super().__init__(c, r, color)

        self.direction = [1, 1]

    def move(self):
        new_c = self.cr[0] + self.direction[0]
        self.cr[0] = new_c
        ball_x = new_c * CELL_SIZE + PADDING

        self.rect.left = ball_x

        new_r = self.cr[1]  + self.direction[1]
        self.cr[1] = new_r
        ball_y = new_r * CELL_SIZE + PADDING

        self.rect.top = ball_y

    def check_collide_with_wall(self):
        new_c = self.cr[0] + self.direction[0]
        if not (0 <= new_c < C):
            self.direction[0] = -self.direction[0]

        new_r = self.cr[1]  + self.direction[1]
        if new_r < 0:
            self.direction[1] = -self.direction[1]
        elif new_r >= R:
            return False

        return True

    def check_collide_with_bat(self, bat):
        new_c = self.cr[0] + self.direction[0]
        new_r = self.cr[1] + self.direction[1]
        if new_r == R -1 and bat.c <= new_c < bat.c + bat.cnum:
            self.direction[1] = -self.direction[1]
            new_c = self.cr[0] + bat.mc
            if 0 <= new_c < C:
                self.cr[0] = new_c
                self.check_collide_with_wall()


class Bat(pygame.sprite.Sprite):
    def __init__(self, c, batlen):
        super().__init__()

        self.cnum = batlen
        self.c = c
        self.mc = 0
        bat_x = c * CELL_SIZE
        bat_y = ( R - 1 ) * CELL_SIZE

        self.image = pygame.Surface((CELL_SIZE * self.cnum, CELL_SIZE))
        self.image.fill(COLORS["player"])

        self.rect = self.image.get_rect()

        self.rect.move_ip(bat_x, bat_y)

    def move(self):
        new_c = self.c + self.mc
        if 0 <= new_c <= C - self.cnum:

            self.c = new_c
            bat_x = self.c * CELL_SIZE

            self.rect.left = bat_x


bm = BrickManager(BRICK_LAYER)
bat = Bat((C - BAT_LENGTH) // 2 , BAT_LENGTH)
ball = Ball(C // 2 - 1,  R - 2)

running = False
time_count = 0


start_info = FONTS[2].render("Press any key to start game", True, COLORS["score"])
text_rect = start_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
win.blit(start_info, text_rect)


while True:
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()
            sys.exit()

        if running:
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == ord('a'):
                        bat.mc = -1
                    if event.key == pygame.K_RIGHT or event.key == ord('d'):
                        bat.mc = 1
            elif event.type == pygame.KEYUP:
                    if (event.key == pygame.K_LEFT or event.key == ord('a')) and bat.mc == -1:
                        bat.mc = 0
                    if (event.key == pygame.K_RIGHT or event.key == ord('d')) and bat.mc == 1:
                        bat.mc = 0
        else:
            if event.type == pygame.KEYDOWN:
                bm = BrickManager(BRICK_LAYER)
                bat = Bat((C - BAT_LENGTH) // 2, BAT_LENGTH)
                ball = Ball(C // 2 - 1, R - 2)
                running = True

    if running:
        # Fill the screen with black
        win.fill(COLORS["bg"])

        # 划上网格线，方便把握距离
        for ci in range(C):
            cx = CELL_SIZE * ci
            pygame.draw.line(win, COLORS["line"], (cx, 0), (cx, R * CELL_SIZE))
        for ri in range(R):
            ry = CELL_SIZE * ri
            pygame.draw.line(win, COLORS["line"], (0, ry), (C * CELL_SIZE, ry))

        bat.move()
        win.blit(bat.image, bat.rect)

        if (time_count + 1) % MOVE_SPACE == 0:
            if ball.check_collide_with_wall():
                ball.check_collide_with_bat(bat)
                ball.move()
                bm.check_hit(ball)
            else:
                print("Game Over")
                texts = ["Game Over", "Brick Left: %d" % len(bm.sprites()), "Press Any Key to Restart game"]
                for ti, text in enumerate(texts):
                    over_info = FONTS[ti].render(text, True, COLORS["over"])
                    text_rect = over_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 48 * ti))
                    win.blit(over_info, text_rect)
                running = False

            if len(bm.sprites()) == 0:
                texts = ["You Win!", "Brick nums: %d" % (BRICK_LAYER * C) ,"Press Any Key to Restart game"]
                for ti, text in enumerate(texts):
                    over_info = FONTS[ti].render(text, True, COLORS["score"])
                    text_rect = over_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 48 * ti))
                    win.blit(over_info, text_rect)
                running = False

        win.blit(ball.image, ball.rect)

        bm.draw(win)
        time_count += 1


    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()

