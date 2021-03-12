import pygame
import sys
import random


C, R = 16, 24  # 16列， 24行
CELL_SIZE = 30  # 格子尺寸
SPACE_LEN = 6
PADDING = 5

bg_color = (0, 0, 0)
wall_color = (100, 100, 100)
bird_color = (65, 105, 225)
score_color = (0,128,0)  # SpringGreen
over_color = (255, 0, 0)

FPS=6  # 游戏帧率
MOVE_SPACE = 3
WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

pygame.init() # pygame初始化，必须有，且必须在开头
# 创建主窗体
clock = pygame.time.Clock() # 用于控制循环刷新频率的对象
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('Flappy Bird by Big Shuang')

# 大中小三种字体，48,36,24
FONTS = [
    pygame.font.Font(pygame.font.get_default_font(), font_size) for font_size in [48, 36, 24]
]


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

    def move_cr(self, c=0, r=0):
        self.cr[0] += c
        self.cr[1] += r
        self.x = self.cr[0] * CELL_SIZE
        self.y = self.cr[1] * CELL_SIZE
        self.rect.left = self.x
        self.rect.top = self.y

class Wall(pygame.sprite.Group):
    def __init__(self, space, space_r):
        super().__init__()
        right_c = C - 1

        for ri in range(R):
            if not (0 <= ri - space_r < space):
                block = Block(right_c, ri, wall_color)
                self.add(block)

    def move_left(self):
        for block in self.sprites():
            block.move_cr(c=-1)

    def get_c(self):
        top_block = self.sprites()[0]
        return top_block.cr[0]

    def check_collide(self, other_block):
        for block in self.sprites():
            if tuple(block.cr) == tuple(other_block.cr):
                return True

        return False


class WallManager():
    def __init__(self, padding):
        self.walls = []
        self.last_r = R // 2
        self.padding = padding
        self.last_c = 0

    def generate_wall(self):
        print("generate a new wall")

        next_r = self.last_r + random.randint(-self.padding, self.padding)

        if next_r <= 0:
            next_r = 1
        elif next_r + SPACE_LEN >= R:
            next_r -= SPACE_LEN

        wall = Wall(SPACE_LEN, next_r)
        self.last_r = next_r

        self.walls.append(wall)
        self.last_c = C - 1
        print("wall counts:", len(self.walls))

    def move(self, bird_c):
        score = 0
        # 超出边界后，自动清理掉
        to_delete = []
        for i, wall in enumerate(self.walls):
            wall.move_left()
            if wall.get_c() == bird_c + 1:
                score = 1
            if wall.get_c() < 0:
                to_delete.append(i)

        for di in to_delete[::-1]:  # 倒着按序号来删除
            self.walls.pop(di)

        self.last_c -= 1
        if C - self.last_c - 1 > self.padding:
            self.generate_wall()
        return score

    def draw(self, win):
        for wall in self.walls:
            wall.draw(win)


class Bird(Block):
    def __init__(self, c, r, color):
        super().__init__(c, r, color)

    def check_collide(self, wallmanager):
        if self.cr[1] < 0 or self.cr[1] >= R:
            return True

        for wall in wallmanager.walls:
            if wall.check_collide(self):
                return True

        return False

wm = WallManager(PADDING)
bird_c = C // 2
bird_r = R // 2
bird = Bird(bird_c, bird_r, bird_color)

frame_count = 0

start_info = FONTS[2].render("Press S to start game", True, score_color)
text_rect = start_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
win.blit(start_info, text_rect)

running =False
score = 0
while True:
    frame_count += 1
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()  # 关闭窗口
            sys.exit()  # 停止程序

        if event.type == pygame.KEYDOWN:
            if running:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    bird.move_cr(r=-2)
            else:
                if event.key == ord('s'):
                    running = True

    if running:
        win.fill(bg_color)

        if frame_count % MOVE_SPACE == 0:
            score += wm.move(bird.cr[0])

        wm.draw(win)

        bird.move_cr(r=1)
        win.blit(bird.image, bird.rect)

        text_info = FONTS[2].render("Scores: %d" % score, True, score_color)
        win.blit(text_info, dest=(0, 0))

        if bird.check_collide(wm):
            running = False

            texts = ["Game Over", "Scores: %d" % (score), "Press S to Restart game"]
            for ti, text in enumerate(texts):
                over_info = FONTS[ti].render(text, True, over_color)
                text_rect = over_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 48 * ti))
                win.blit(over_info, text_rect)


    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()