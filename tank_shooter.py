import pygame
import sys

C, R = 10, 20
CELL_SIZE = 40

FPS=60 # 游戏帧率

WIN_WIDTH = CELL_SIZE * C  # 窗口宽度
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度

COLOR_1 = (255, 255, 255)

TANK_GRID = [
    [0, 1, 0],
    [1, 1, 1],
    [1, 1, 1],
]


pygame.init() # pygame初始化，必须有，且必须在开头
# 创建主窗体
clock=pygame.time.Clock() # 用于控制循环刷新频率的对象
win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))


class Block(pygame.sprite.Sprite):
    def __init__(self, c, r):
        super().__init__()

        self.cr = [c, r]
        self.x = c * CELL_SIZE
        self.y = r * CELL_SIZE

        self.image  = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(COLOR_1)
        # points = []
        # pygame.draw.polygon(self.image, COLOR_1, points)

        self.rect = self.image.get_rect()

        self.rect.move_ip(self.x, self.y)

    def move(self, direction=""):
        if direction == "LEFT" and self.cr[0] > 0:
            self.cr[0] -= 1
            self.x -= CELL_SIZE
            self.rect.left = self.x
        if direction == "RIGHT" and self.cr[0] < C - 1:
            self.cr[0] += 1
            self.x += CELL_SIZE
            self.rect.left = self.x
        if direction == "UP" and self.cr[1] > 0 :
            self.cr[1] -= 1
            self.y -= CELL_SIZE
            self.rect.top = self.y
        if direction == "DOWN" and self.cr[1] < R - 1:
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
    def __init__(self, *sprites):
        super().__init__(*sprites)

        for r, row in enumerate(TANK_GRID):
            for c, cell in enumerate(row):
                if cell == 1:
                    player = Block(c, r)
                    self.add(player)

    def move(self, direction=""):
        if all(player.check_move(direction) for player in self.sprites()):
            for player in self.sprites():
                player.move(direction)


player_tank = Tank()


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

    clock.tick(FPS) # 控制循环刷新频率,每秒刷新FPS对应的值的次数

    # Fill the screen with black
    win.fill((0, 0, 0))

    # Draw the player on the screen
    player_tank.draw(win)

    pygame.display.update()