import pygame
import random
from config import *

# 基础精灵类
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color):
        super().__init__()
        self.radius = radius
        self.color = color
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y

    def update(self):
        self.rect.center = (self.x, self.y)


# ✅ 敌方彩球 - 呼吸式柔和闪烁【核心保留，效果完美】
class Ball(GameObject):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.alpha = MAX_ALPHA  # 初始最亮
        self.flash_direction = -1  # 闪烁方向：-1变暗 / 1变亮
        self.speed_x = 0
        self.speed_y = 0
        # ========== 新增：反弹加速因子 ==========
        self.bounce_speed_boost = 1.2  # 每次反弹加速20%

    def update(self):
        # 彩球呼吸闪烁核心逻辑 - 柔和渐变 不晃眼
        self.alpha += self.flash_direction * FLASH_SPEED
        if self.alpha <= MIN_ALPHA:
            self.alpha = MIN_ALPHA
            self.flash_direction = 1
        if self.alpha >= MAX_ALPHA:
            self.alpha = MAX_ALPHA
            self.flash_direction = -1
        self.image.set_alpha(self.alpha)

        # 小球移动+边界反弹逻辑
        self.x += self.speed_x * SPEED_MULTIPLIER
        self.y += self.speed_y * SPEED_MULTIPLIER
        width, height = get_window_size()

        # ========== 修改：边界碰撞反弹时加速 ==========
        bounced = False
        if self.x - self.radius <= 0 or self.x + self.radius >= width:
            self.speed_x *= -1
            bounced = True
        if self.y - self.radius <= 0 or self.y + self.radius >= height:
            self.speed_y *= -1
            bounced = True

        # 如果发生反弹，加速彩球
        if bounced:
            self.speed_x *= self.bounce_speed_boost
            self.speed_y *= self.bounce_speed_boost

            # 限制最大速度，避免过快
            max_speed = MAX_SPEED
            if abs(self.speed_x) > max_speed:
                self.speed_x = max_speed if self.speed_x > 0 else -max_speed
            if abs(self.speed_y) > max_speed:
                self.speed_y = max_speed if self.speed_y > 0 else -max_speed

        super().update()


# ✅ 玩家主球 - 半透明、不闪烁、完全不变
class PlayerBall(GameObject):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.image.set_alpha(220)  # 半透明优化 视野更好

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = mouse_x
        self.y = mouse_y
        super().update()


# ✅ 黑洞 - 纯黑、不闪烁、完全不变
class Hole(GameObject):
    def __init__(self, x, y, radius, color=BLACK):
        super().__init__(x, y, radius, color)
        pygame.draw.circle(self.image, (20, 20, 20), (radius, radius), radius)
