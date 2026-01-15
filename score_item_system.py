import pygame
from config import get_window_size, SCORE_RULE, ITEM_PRICE  # 新增导入config中的常量

# ========== 提示管理全局变量 ==========
tip_text = ""  # 提示文本
tip_color = (255, 255, 255)  # 提示颜色
tip_show_time = 0  # 提示显示时长（毫秒）
TIP_DURATION = 2000  # 提示默认显示2秒

# ========== 原有全局变量（保持不变） ==========
total_score = 0
owned_items = {"item1": 0, "item2": 0}
active_items = {"item1": False, "item2": False}

# ========== 提示操作函数 ==========
def set_tip(text, color=(255, 255, 255)):
    """设置提示文本和颜色 - 使用config中的set_tip"""
    from config import set_tip as config_set_tip
    config_set_tip(text, color)


def draw_tip(screen):
    """绘制提示文本 - 使用config中的draw_tip"""
    from config import draw_tip as config_draw_tip
    config_draw_tip(screen)


# ========== 购买/使用道具函数（保持不变） ==========
def buy_item(item_name):
    global total_score
    if item_name not in ITEM_PRICE:
        set_tip("道具不存在！", (255,0,0))
        return False, "道具不存在"
    if total_score < ITEM_PRICE[item_name]:
        # ========== 修改：积分不足 → 醒目红色大字提示 ==========
        set_tip("积分不足！无法购买", (255, 0, 0))
        return False, "积分不足"
    total_score -= ITEM_PRICE[item_name]
    owned_items[item_name] += 1
    tip_msg = f"成功购买{get_item_name(item_name)}！剩余积分：{total_score}"
    set_tip(tip_msg, (0,255,0))
    return True, tip_msg

def use_item(item_name):
    """使用道具：添加提示"""
    if owned_items.get(item_name, 0) <= 0:
        set_tip(f"{get_item_name(item_name)}数量不足！", (255, 0, 0))
        return False, "道具数量不足"
    owned_items[item_name] -= 1
    active_items[item_name] = True
    tip_msg = f"下一关将生效{get_item_name(item_name)}！"
    set_tip(tip_msg, (255, 215, 0))  # 金色提示
    return True, tip_msg

# score_item_system.py 末尾新增
def use_all_items():
    """使用所有已购买道具，并返回提示文本"""
    has_item = False
    for item_name in owned_items:
        if owned_items[item_name] > 0:
            owned_items[item_name] -= 1
            active_items[item_name] = True
            has_item = True
    if has_item:
        set_tip("道具生效！下一关自动触发效果", (255,215,0)) #金色提示
        return True
    else:
        set_tip("暂无可用道具！先购买道具再使用", (255,0,0)) #红色提示
        return False

# ========== 原有函数（保持不变） ==========
def add_score(difficulty):
    global total_score
    if difficulty in SCORE_RULE:
        total_score += SCORE_RULE[difficulty]
        set_tip(f"通关{difficulty}难度，获得{SCORE_RULE[difficulty]}积分！总积分：{total_score}", (0, 255, 0))
        print(f"通关{difficulty}难度，获得{SCORE_RULE[difficulty]}积分，总积分：{total_score}")


def get_total_score():
    return total_score


def clear_active_items():
    global active_items
    active_items = {"item1": False, "item2": False}


def get_owned_items():
    return owned_items.copy()


def get_active_items():
    return active_items.copy()


def get_item_name(item_name):
    item_name_map = {
        "item1": "黑洞放大",  # 精简文字，不会溢出
        "item2": "主球缩小"   # 精简文字，完美适配小按钮
    }
    return item_name_map.get(item_name, "未知道具")


def apply_item_effect_to_hole(hole):
    """应用道具1效果：黑洞半径放大一倍"""
    if active_items["item1"]:
        new_radius = hole.radius * 2  # 放大一倍
        hole.radius = new_radius
        hole.image = pygame.Surface((new_radius * 2, new_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(hole.image, (0, 0, 0), (new_radius, new_radius), new_radius)
        hole.rect = hole.image.get_rect(center=hole.rect.center)


def apply_item_effect_to_player(player_ball):
    """应用道具2效果：主球半径缩小一半"""
    if active_items["item2"]:
        new_radius = player_ball.radius // 2  # 缩小一半
        new_radius = max(new_radius, 5)  # 最小半径为5
        player_ball.radius = new_radius
        player_ball.image = pygame.Surface((new_radius * 2, new_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(player_ball.image, player_ball.color, (new_radius, new_radius), new_radius)
        player_ball.rect = player_ball.image.get_rect(center=player_ball.rect.center)


# ========== 修改道具信息绘制函数（结算界面右侧显示） ==========
def draw_score_item_info(screen):
    """结算界面绘制道具信息（右侧显示）"""
    WIDTH, HEIGHT = get_window_size()
    try:
        from config import FONT_PATH
        font = pygame.font.Font(FONT_PATH, 20)
    except:
        font = pygame.font.SysFont("simhei", 20)

    # 绘制位置：屏幕右侧
    start_x = WIDTH - 220
    start_y = 10

    # 绘制道具标题
    title_text = "道具信息"
    title_surface = font.render(title_text, True, (255, 215, 0))  # 金色
    title_rect = title_surface.get_rect(topleft=(start_x, start_y))
    screen.blit(title_surface, title_rect)

    # 绘制拥有的道具
    item_y = start_y + 30
    for item_code, count in owned_items.items():
        item_text = f"{get_item_name(item_code)}：{count}个"
        item_surface = font.render(item_text, True, (255, 255, 255))
        item_rect = item_surface.get_rect(topleft=(start_x, item_y))
        screen.blit(item_surface, item_rect)
        item_y += 25

    # 绘制生效中的道具
    active_y = item_y + 10
    active_text = "下一关生效："
    active_surface = font.render(active_text, True, (0, 255, 0))  # 绿色
    active_rect = active_surface.get_rect(topleft=(start_x, active_y))
    screen.blit(active_surface, active_rect)

    active_y += 25
    for item_code, is_active in active_items.items():
        if is_active:
            active_item_text = f"✓ {get_item_name(item_code)}"
            active_item_surface = font.render(active_item_text, True, (0, 255, 0))
            active_item_rect = active_item_surface.get_rect(topleft=(start_x + 10, active_y))
            screen.blit(active_item_surface, active_item_rect)
            active_y += 20