import pygame
import random
from config import *
from sprites import PlayerBall, Ball, Hole

# 全局精灵组初始化
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
balls = pygame.sprite.Group()
holes = pygame.sprite.Group()
current_difficulty = "easy"
# ========== 新增：游戏计时器 ==========
game_start_time = 0


# 重置游戏核心函数 - 新增多黑洞逻辑，彩球/黑洞数量对应难度
def reset_game(difficulty):
    global current_difficulty, game_start_time
    current_difficulty = difficulty
    all_sprites.empty()
    player_group.empty()
    balls.empty()
    holes.empty()
    # ========== 新增：重置游戏开始时间 ==========
    game_start_time = pygame.time.get_ticks()

    width, height = get_window_size()
    cfg = DIFFICULTY_CONFIG[difficulty]

    # ========== 新增：导入道具系统 ==========
    from score_item_system import get_active_items, clear_active_items

    # 获取激活的道具效果
    active_items = get_active_items()

    # 根据道具效果调整黑洞和玩家球的大小
    hole_radius = cfg["hole_radius"]
    # ========== 修改：主球固定大小为30，不受难度影响 ==========
    player_radius = 30  # 固定大小，所有难度都一样

    # 道具1：黑洞放大
    if active_items.get("item1", False):
        hole_radius *= 2  # 放大一倍

    # 根据难度定义彩球/黑洞数量（简单3/普通6/地狱12）
    count_map = {
        "easy": 3,
        "normal": 6,
        "hell": 12
    }
    obj_count = count_map[difficulty]

    # ========== 先创建黑洞和彩球，然后再确定主球位置 ==========
    # 创建多个黑洞（随机位置，避免重叠）
    for _ in range(obj_count):
        # 随机生成位置，确保黑洞不超出窗口且远离边缘
        hole_x = random.randint(hole_radius * 2, width - hole_radius * 2)
        hole_y = random.randint(hole_radius * 2, height - hole_radius * 2)
        # 检测黑洞是否重叠，若重叠则重新生成位置
        overlap = True
        while overlap:
            overlap = False
            for existing_hole in holes:
                dx = hole_x - existing_hole.x
                dy = hole_y - existing_hole.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < hole_radius * 3:  # 黑洞间距至少3倍半径
                    hole_x = random.randint(hole_radius * 2, width - hole_radius * 2)
                    hole_y = random.randint(hole_radius * 2, height - hole_radius * 2)
                    overlap = True
                    break
        # 创建黑洞并加入精灵组
        hole = Hole(hole_x, hole_y, hole_radius)
        all_sprites.add(hole)
        holes.add(hole)

    # 创建对应数量的敌方彩球（随机位置+速度，适配难度）
    ball_positions = []  # 记录所有彩球的位置和半径
    for _ in range(obj_count):
        # 彩球位置远离黑洞和边缘
        ball_x = random.randint(cfg["ball_radius"] * 2, width - cfg["ball_radius"] * 2)
        ball_y = random.randint(cfg["ball_radius"] * 2, height - cfg["ball_radius"] * 2)

        # 确保彩球初始位置不与黑洞重叠
        overlap = True
        while overlap:
            overlap = False
            for hole in holes:
                dx = ball_x - hole.x
                dy = ball_y - hole.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < (cfg["ball_radius"] + hole_radius) * 2:
                    ball_x = random.randint(cfg["ball_radius"] * 2, width - cfg["ball_radius"] * 2)
                    ball_y = random.randint(cfg["ball_radius"] * 2, height - cfg["ball_radius"] * 2)
                    overlap = True
                    break

        color = random.choice([RED, GREEN, BLUE])
        ball = Ball(ball_x, ball_y, cfg["ball_radius"], color)
        # 彩球速度适配难度配置
        ball.speed_x = random.randint(-cfg["init_speed"], cfg["init_speed"])
        ball.speed_y = random.randint(-cfg["init_speed"], cfg["init_speed"])
        # 避免彩球初始速度为0
        if ball.speed_x == 0:
            ball.speed_x = 1 if random.random() > 0.5 else -1
        if ball.speed_y == 0:
            ball.speed_y = 1 if random.random() > 0.5 else -1
        all_sprites.add(ball)
        balls.add(ball)

        # 记录彩球位置信息，用于主球位置检查
        ball_positions.append({
            "x": ball_x,
            "y": ball_y,
            "radius": cfg["ball_radius"]
        })

    # ========== 新增：寻找安全的主球生成位置 ==========
    player_x, player_y = find_safe_player_position(width, height, player_radius, ball_positions, holes)

    # 创建玩家主球（固定大小30）
    player = PlayerBall(player_x, player_y, player_radius, WHITE)
    # 道具2：主球缩小（在创建后应用）
    if active_items.get("item2", False):
        from score_item_system import apply_item_effect_to_player
        apply_item_effect_to_player(player)

    all_sprites.add(player)
    player_group.add(player)

    # ========== 新增：应用道具效果到所有黑洞 ==========
    if active_items.get("item1", False):
        for hole in holes:
            from score_item_system import apply_item_effect_to_hole
            apply_item_effect_to_hole(hole)

    # 清除激活的道具状态（一次性使用）
    clear_active_items()

    return GameState.PLAYING


# ========== 新增：寻找安全的主球生成位置函数 ==========
def find_safe_player_position(width, height, player_radius, ball_positions, holes):
    """寻找安全的主球生成位置，避免开门杀"""
    max_attempts = 200  # 最大尝试次数
    min_safe_distance = 500  # 最小安全距离（像素）

    for attempt in range(max_attempts):
        # 随机生成候选位置
        candidate_x = random.randint(player_radius * 2, width - player_radius * 2)
        candidate_y = random.randint(player_radius * 2, height - player_radius * 2)

        # 检查是否安全（远离所有彩球）
        safe_from_balls = True
        for ball_info in ball_positions:
            dx = candidate_x - ball_info["x"]
            dy = candidate_y - ball_info["y"]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            # 需要保持至少最小安全距离
            if distance < (player_radius + ball_info["radius"] + min_safe_distance):
                safe_from_balls = False
                break

        # 如果离彩球太近，尝试下一个位置
        if not safe_from_balls:
            continue

        # 检查是否安全（远离所有黑洞）
        safe_from_holes = True
        for hole in holes:
            dx = candidate_x - hole.x
            dy = candidate_y - hole.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            # 需要保持至少一定距离（黑洞半径+主球半径+额外安全距离）
            if distance < (player_radius + hole.radius + 50):
                safe_from_holes = False
                break

        # 如果离黑洞太近，尝试下一个位置
        if not safe_from_holes:
            continue

        # 位置安全，返回这个位置
        return candidate_x, candidate_y

    # 如果找不到完全安全的位置，返回屏幕中心（最后的保障）
    print(f"警告：经过{max_attempts}次尝试未找到完全安全位置，使用屏幕中心")
    return width // 2, height // 2


# ========== 原有函数保持不变 ==========
def get_player_ball():
    """
    获取当前游戏中的玩家球对象。

    返回值:
        PlayerBall or None: 玩家球精灵对象，如果没有玩家球则返回None
    """
    return player_group.sprites()[0] if player_group else None


def get_holes():
    """
    获取当前游戏中的所有黑洞对象。

    返回值:
        pygame.sprite.Group: 包含所有黑洞精灵的精灵组
    """
    return holes


def get_balls():
    """
    获取当前游戏中的所有彩球（敌方球）对象。

    返回值:
        pygame.sprite.Group: 包含所有彩球精灵的精灵组
    """
    return balls


def get_all_sprites():
    """
    获取当前游戏中的所有精灵对象。

    这个函数返回包含所有类型精灵（玩家球、彩球、黑洞）的精灵组，
    用于统一更新和渲染所有游戏对象。

    返回值:
        pygame.sprite.Group: 包含所有游戏精灵的精灵组
    """
    return all_sprites

# 获取当前难度
def get_current_difficulty():
    return current_difficulty


# 检测小球进黑洞（适配多黑洞，彩球和黑洞碰撞后都消失）
def check_ball_hole_collision():
    collided = False
    collided_holes = []  # 记录需要删除的黑洞

    # 遍历所有黑洞，检测彩球碰撞
    for hole in holes:
        collided_balls = pygame.sprite.spritecollide(hole, balls, True, pygame.sprite.collide_circle)
        if collided_balls:
            collided = True
            collided_holes.append(hole)  # 标记这个黑洞也要删除

    # 删除所有碰撞过的黑洞
    for hole in collided_holes:
        hole.kill()
        holes.remove(hole)

    return collided


# 检测玩家碰撞小球
def check_player_collision():
    player = get_player_ball()
    if not player:
        return False
    return pygame.sprite.spritecollideany(player, balls, pygame.sprite.collide_circle)


# ========== 修改：检测胜利条件（所有彩球都被黑洞吸收 OR 坚持10秒） ==========
def check_win_condition():
    # 条件1：所有彩球都被黑洞吸收
    if len(balls) == 0:
        return True, "all_balls_absorbed"

    # 条件2：坚持10秒没有失败
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - game_start_time
    if elapsed_time >= TIME_LIMIT:
        return True, "time_survived"

    return False, None


# ========== 新增：获取已游戏时间 ==========
def get_elapsed_time():
    if game_start_time == 0:
        return 0
    current_time = pygame.time.get_ticks()
    return current_time - game_start_time


# ========== 新增：获取剩余时间 ==========
def get_remaining_time():
    if game_start_time == 0:
        return TIME_LIMIT
    elapsed = get_elapsed_time()
    remaining = TIME_LIMIT - elapsed
    return max(0, remaining)


# 所有精灵更新
def update_all_sprites(dt):
    all_sprites.update()


# 清空所有精灵
def clear_all_sprites():
    all_sprites.empty()
    player_group.empty()
    balls.empty()
    holes.empty()