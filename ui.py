import pygame
from config import get_window_size, GRAY, DARK_GRAY, BLACK, FONT_PATH, BLUE, RED, GREEN


def draw_text(text, size, color, x, y):
    try:
        font = pygame.font.Font(FONT_PATH, size)
    except:
        font = pygame.font.SysFont("simhei", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    from config import SCREEN
    SCREEN.blit(text_surface, text_rect)


def draw_button(text, x, y, width, height, normal_color, hover_color, action=None, is_clicked=False, text_color=BLACK):
    SCREEN = pygame.display.get_surface()
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    is_hover = button_rect.collidepoint(mouse_pos)

    # 绘制按钮背景 + 圆角美化
    if is_hover:
        pygame.draw.rect(SCREEN, hover_color, button_rect, border_radius=6)
    else:
        pygame.draw.rect(SCREEN, normal_color, button_rect, border_radius=6)

    # 按钮文字字号适配小按钮，永不溢出
    try:
        font = pygame.font.Font(FONT_PATH, 20)
    except:
        font = pygame.font.SysFont("simhei", 20)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x, y))
    SCREEN.blit(text_surface, text_rect)

    if is_clicked and is_hover and action:
        return action
    return None


def draw_difficulty_buttons(is_clicked=False):
    WIDTH, HEIGHT = get_window_size()
    # 简单难度：浅粉色底 + 深玫瑰红反馈 + 红色字体 不变
    easy_action = draw_button("简单", WIDTH // 2, HEIGHT // 2 - 60, 180, 60,
                              (255, 220, 225), (205, 92, 92), "easy", is_clicked, text_color=(255, 0, 0))
    # 普通难度：浅豆绿底 + 深草绿反馈 + 绿色字体 不变
    normal_action = draw_button("普通", WIDTH // 2, HEIGHT // 2 + 10, 180, 60,
                                (220, 245, 220), (60, 179, 113), "normal", is_clicked, text_color=(0, 255, 0))
    # 地狱难度：浅天兰底 + 深海蓝反馈 + 蓝色字体 不变
    hell_action = draw_button("地狱", WIDTH // 2, HEIGHT // 2 + 80, 180, 60,
                              (220, 240, 255), (0, 100, 200), "hell", is_clicked, text_color=(0, 0, 255))
    return easy_action, normal_action, hell_action


def draw_item_buttons(is_clicked=False):
    from score_item_system import ITEM_PRICE, get_item_name, get_total_score
    WIDTH, HEIGHT = get_window_size()
    # ========== 核心修改1：购买道具按钮 调小尺寸 (缩小一圈，完美比例) ==========
    button_width = 220  # 比之前更小，刚刚好装下文字
    button_height = 50  # 高度微调变小
    start_y = HEIGHT // 2 + 120
    gap_y = 60

    # ========== 核心修改2：道具按钮  默认=蓝色  点击/悬浮=红色  文字白色 ==========
    item1_text = f"{get_item_name('item1')}（{ITEM_PRICE['item1']}积分）"
    item1_action = draw_button(
        item1_text, WIDTH // 2 - 130, start_y,
        button_width, button_height,
        (0, 100, 255),  # 默认按钮底色：深蓝色（好看不刺眼）
        (220, 0, 0),  # 悬浮/点击反馈：红色
        action="buy_item1", is_clicked=is_clicked,
        text_color=(255, 255, 255)  # 按钮文字：纯白色
    )

    item2_text = f"{get_item_name('item2')}（{ITEM_PRICE['item2']}积分）"
    item2_action = draw_button(
        item2_text, WIDTH // 2 + 130, start_y,
        button_width, button_height,
        (0, 100, 255),  # 默认按钮底色：深蓝色
        (220, 0, 0),  # 悬浮/点击反馈：红色
        action="buy_item2", is_clicked=is_clicked,
        text_color=(255, 255, 255)  # 按钮文字：纯白色
    )

    # ========== 核心要求：使用道具的按钮 完全不变 原样保留 ==========
    use_item_text = "使用（所有）已购买道具"
    use_item_action = draw_button(
        use_item_text, WIDTH // 2, start_y + gap_y,
                       button_width * 2, button_height,
        (0, 128, 255), (0, 191, 255),
        action="use_item", is_clicked=is_clicked,
        text_color=(255, 255, 255)
    )

    return item1_action, item2_action, use_item_action


# 结算界面积分绘制 - 不变
def draw_end_menu_score():
    from score_item_system import get_total_score
    WIDTH, HEIGHT = get_window_size()
    draw_text("当前总积分", 40, (255, 165, 0), WIDTH//2, HEIGHT//2 - 100) # 橙金色
    score = get_total_score()
    draw_text(str(score), 80, (255,215,0), WIDTH//2, HEIGHT//2 - 30) # 黄金色