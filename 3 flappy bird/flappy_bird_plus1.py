# Move smoothly
import pygame
import sys
import random


C, R = 15, 24  # 16列， 24行
CELL_SIZE = 30  # 格子尺寸
SPACE_LEN = 6
PADDING = 5

bg_color = (0, 0, 0)
wall_color = (100, 100, 100)
bird_color = (65, 105, 225)
score_color = (0,128,0)  # SpringGreen
over_color = (255, 0, 0)

FPS=60  # 游戏帧率
MOVE_SPACE = 2
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


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()

        self.x = x
        self.y = y

        self.image  = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(self.x, self.y)

    def fly(self):  # move up
        self.y -= MOVE_SPACE * 2
        self.rect.top = self.y

    def fall(self):  # move down
        self.y += MOVE_SPACE * 2
        self.rect.top = self.y

    def check_collide(self, wall_manager):
        if self.y < 0 or self.y > WIN_HEIGHT - CELL_SIZE:
            return True

        for wall in wall_manager.walls:
            if wall.check_collide(self):
                return True

        return False


class Block(pygame.sprite.Sprite):
    def __init__(self, height, is_top):
        super().__init__()
        self.x = WIN_WIDTH
        if is_top:
            self.y = 0
        else:
            self.y = WIN_HEIGHT - height

        self.image = pygame.Surface((CELL_SIZE, height))
        self.image.fill(wall_color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(self.x, self.y)

    def move_left(self):
        self.x -= MOVE_SPACE
        self.rect.left = self.x


class Wall(pygame.sprite.Group):
    def __init__(self, space_num, top_rnum):
        super().__init__()

        top_height = top_rnum * CELL_SIZE
        bottom_height = WIN_HEIGHT - (top_rnum+space_num) * CELL_SIZE

        top_block = Block(top_height, True)
        bottom_block = Block(bottom_height, False)

        self.add(top_block)
        self.add(bottom_block)

        self.passed = False  # bird fly over it

    def move_left(self):
        for block in self.sprites():
            block.move_left()

    def get_rx(self):
        top_block = self.sprites()[0]
        return top_block.x + CELL_SIZE

    def check_collide(self, bird):
        for block in self.sprites():
            if pygame.sprite.collide_rect(block, bird):
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
        self.last_c = WIN_WIDTH
        print("wall counts:", len(self.walls))

    def move(self, bird_x):
        score = 0
        # 超出边界后，自动清理掉
        to_delete = []
        for i, wall in enumerate(self.walls):
            wall.move_left()
            if not wall.passed and wall.get_rx() < bird_x:
                wall.passed = True
                score = 1
            if wall.get_rx() < 0:
                to_delete.append(i)

        for di in to_delete[::-1]:  # 倒着按序号来删除
            self.walls.pop(di)

        if self.walls:
            self.last_c = self.walls[-1].get_rx()
        if C * CELL_SIZE - self.last_c > self.padding * CELL_SIZE:
            self.generate_wall()
        return score

    def draw(self, win):
        for wall in self.walls:
            wall.draw(win)


wm = WallManager(PADDING)
bird_c = WIN_WIDTH // 2
bird_r = WIN_HEIGHT // 2
bird = Bird(bird_c, bird_r, bird_color)

frame_count = 0

start_info = FONTS[2].render("Press S to start game", True, score_color)
text_rect = start_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
win.blit(start_info, text_rect)

running =False
is_fly = False
score = 0
while True:
    frame_count += 1
    # 获取所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 判断当前事件是否为点击右上角退出键
            pygame.quit()  # 关闭窗口
            sys.exit()  # 停止程序


        if running:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    is_fly = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    is_fly = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == ord('s'):
                    bird = Bird(bird_c, bird_r, bird_color)
                    is_fly = False
                    wm = WallManager(PADDING)
                    frame_count = 0
                    score = 0
                    running = True


    if running:
        win.fill(bg_color)

        if frame_count % MOVE_SPACE == 0:
            score += wm.move(bird.x)

        wm.draw(win)

        if is_fly:
            bird.fly()
        else:
            bird.fall()
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