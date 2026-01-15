import pygame
import sys
import os

# ================== 1. 获取资源绝对路径 ==================
def get_resource_path(relative_path):
    """
    获取资源绝对路径，兼容开发环境和 PyInstaller 打包后的 exe
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ================== 2. 全局变量 & GIF/图片配置 ==================
BACKGROUND_GIF_PATH = get_resource_path("bg1.jpg")  # 可替换为 JPG/PNG/GIF
_ORIGINAL_BACKGROUND = None
_CURRENT_BACKGROUND = None
gif_frames = []
gif_delays = []
current_frame_idx = 0
frame_timer = 0
SPEED_FACTOR = 1  # GIF原速播放

# 全局提示变量
tip_text = ""
tip_color = (255, 255, 255)
tip_show_time = 0

# 顶部提示变量（成就用）
top_tip_text = ""
top_tip_color = (255, 255, 255)
top_tip_show_time = 0

# 彩球呼吸闪烁核心配置
FLASH_SPEED = 8
MIN_ALPHA = 170
MAX_ALPHA = 255

# ================== 3. 初始化 pygame ==================
pygame.init()
pygame.font.init()

# 窗口基础配置
_INIT_WIDTH = 960
_INIT_HEIGHT = 540
WIDTH = _INIT_WIDTH
HEIGHT = _INIT_HEIGHT
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("躲避球")

# ================== 4. GIF/图片背景加载 ==================
try:
    from PIL import Image

    with Image.open(BACKGROUND_GIF_PATH) as img:
        try:
            n_frames = img.n_frames  # 多帧 GIF
        except AttributeError:
            n_frames = 1  # 单帧 JPG/PNG 或单帧 GIF

        for frame_idx in range(n_frames):
            if n_frames > 1:
                img.seek(frame_idx)
            frame = img.convert("RGBA")
            pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            gif_frames.append(pygame_frame)
            original_delay = img.info.get("duration", 100)
            delayed_time = original_delay * SPEED_FACTOR
            gif_delays.append(delayed_time)

    if gif_frames:
        _ORIGINAL_BACKGROUND = gif_frames
        _CURRENT_BACKGROUND = pygame.transform.smoothscale(gif_frames[0], (WIDTH, HEIGHT))
    else:
        _ORIGINAL_BACKGROUND = pygame.Surface((_INIT_WIDTH, _INIT_HEIGHT))
        _ORIGINAL_BACKGROUND.fill((200, 200, 200))
        _CURRENT_BACKGROUND = _ORIGINAL_BACKGROUND.copy()

except Exception as e:
    print(f"GIF/图片加载失败：{e}，使用灰色兜底")
    _ORIGINAL_BACKGROUND = pygame.Surface((_INIT_WIDTH, _INIT_HEIGHT))
    _ORIGINAL_BACKGROUND.fill((200, 200, 200))
    _CURRENT_BACKGROUND = _ORIGINAL_BACKGROUND.copy()


# ================== 5. 核心函数 ==================
def update_gif_frame(dt):
    """
    更新 GIF 或背景帧
    """
    global current_frame_idx, frame_timer, _CURRENT_BACKGROUND
    if not gif_frames:
        return
    frame_timer += dt
    if frame_timer >= gif_delays[current_frame_idx]:
        current_frame_idx = (current_frame_idx + 1) % len(gif_frames)
        frame_timer = 0
        _CURRENT_BACKGROUND = pygame.transform.smoothscale(gif_frames[current_frame_idx], (WIDTH, HEIGHT))


def get_window_size():
    return WIDTH, HEIGHT


def get_background_image():
    return _CURRENT_BACKGROUND


def update_window(new_width, new_height):
    global WIDTH, HEIGHT, SCREEN, _CURRENT_BACKGROUND
    WIDTH = max(400, new_width)
    HEIGHT = max(300, new_height)
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    if gif_frames:
        _CURRENT_BACKGROUND = pygame.transform.smoothscale(gif_frames[current_frame_idx], (WIDTH, HEIGHT))
    else:
        _CURRENT_BACKGROUND = pygame.transform.scale(_ORIGINAL_BACKGROUND, (WIDTH, HEIGHT))


# ================== 6. 提示框绘制函数 ==================
def set_tip(text, color=(255, 255, 255)):
    global tip_text, tip_color, tip_show_time
    tip_text = text
    tip_color = color
    tip_show_time = pygame.time.get_ticks()


def set_top_tip(text, color=(255, 255, 255)):
    global top_tip_text, top_tip_color, top_tip_show_time
    top_tip_text = text
    top_tip_color = color
    top_tip_show_time = pygame.time.get_ticks()


def draw_tip(screen):
    global tip_text, tip_color, tip_show_time, top_tip_text, top_tip_color, top_tip_show_time

    TIP_DURATION = 2000
    TOP_TIP_DURATION = 3000
    current_time = pygame.time.get_ticks()

    # 底部提示
    if tip_text and (current_time - tip_show_time) <= TIP_DURATION:
        try:
            font = pygame.font.Font(FONT_PATH, 24)
        except:
            font = pygame.font.SysFont("simhei", 24)
        tip_surface = font.render(tip_text, True, tip_color)
        tip_rect = tip_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        bg_rect = pygame.Rect(tip_rect.x - 10, tip_rect.y - 5, tip_rect.width + 20, tip_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        screen.blit(tip_surface, tip_rect)

    # 顶部提示
    if top_tip_text and (current_time - top_tip_show_time) <= TOP_TIP_DURATION:
        try:
            font = pygame.font.Font(FONT_PATH, 24)
        except:
            font = pygame.font.SysFont("simhei", 24)
        top_tip_surface = font.render(top_tip_text, True, top_tip_color)
        top_tip_rect = top_tip_surface.get_rect(center=(WIDTH // 2, 60))
        bg_rect = pygame.Rect(top_tip_rect.x - 15, top_tip_rect.y - 8,
                              top_tip_rect.width + 30, top_tip_rect.height + 16)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        screen.blit(s, (bg_rect.x, bg_rect.y))
        pygame.draw.rect(screen, (255, 215, 0), bg_rect, 2, border_radius=8)
        screen.blit(top_tip_surface, top_tip_rect)

    # 清除已过期提示
    if tip_text and (current_time - tip_show_time) > TIP_DURATION:
        tip_text = ""
    if top_tip_text and (current_time - top_tip_show_time) > TOP_TIP_DURATION:
        top_tip_text = ""


# ================== 7. 常量配置 ==================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
FPS = 60
SAFE_RADIUS_RATIO = 0.2
MAX_SPEED = 30
COLLIDE_RATIO = 1.1
WIN_LOSE_DELAY = 1000
TIME_LIMIT = 10000  # 10秒
FONT_PATH = r"C:\WINDOWS\FONTS\SIMSUN.TTC"
SPEED_MULTIPLIER = 1.2

DIFFICULTY_CONFIG = {
    "easy": {"ball_count": 3, "ball_radius": 20, "hole_radius": 25, "init_speed": 3},
    "normal": {"ball_count": 6, "ball_radius": 10, "hole_radius": 12, "init_speed": 6},
    "hell": {"ball_count": 12, "ball_radius": 5, "hole_radius": 6, "init_speed": 12}
}

SCORE_RULE = {"easy": 1, "normal": 2, "hell": 10}
TIME_SURVIVAL_SCORE_RULE = {"easy": 1, "normal": 2, "hell": 10}
ITEM_PRICE = {"item1": 2, "item2": 1}


class GameState:
    START = 0
    SELECT_DIFFICULTY = 1
    PLAYING = 2
    WIN_DISPLAY = 3
    LOSE_DISPLAY = 4
    END_MENU = 5
    ACHIEVEMENTS = 6
