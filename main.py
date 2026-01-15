import pygame
import random

# 导入配置和核心模块
from config import (
    SCREEN, FPS, TIME_LIMIT,
    get_window_size,
    get_background_image,
    update_window,
    update_gif_frame,
    WHITE, BLACK, GRAY, DARK_GRAY, BLUE, RED, GREEN, SCORE_RULE,
    WIN_LOSE_DELAY,
    GameState
)

# 导入UI模块
from ui import (
    draw_text,
    draw_button,
    draw_difficulty_buttons,
    draw_item_buttons,
    draw_end_menu_score  # 结算界面积分绘制
)

# 导入游戏逻辑模块
from game_logic import (
    reset_game, all_sprites, balls, holes,
    check_ball_hole_collision, check_player_collision, check_win_condition,
    get_player_ball, get_current_difficulty, get_elapsed_time, get_remaining_time
)

# 导入积分道具系统
from score_item_system import (
    add_score,
    buy_item,
    use_item,
    draw_score_item_info,
    get_owned_items,
    get_active_items,  # 新增：获取激活的道具状态
    draw_tip,  # 提示绘制函数
    set_tip  # 设置提示
)

# 导入成就系统
from achievement_system import achievement_system

# 胜负提示文案配置
WIN_TEXT = {
    "easy": "你赢了！",
    "normal": "你真棒！",
    "hell": "wc,你真NB！"
}
LOSE_TEXT = {
    "easy": "菜！",
    "normal": "可惜！",
    "hell": "虽败犹荣！"
}

# ========== 新增：扩展游戏状态 ==========
GameState.ACHIEVEMENTS = 6  # 成就界面


# ========== 新增：绘制游戏时间 ==========
def draw_game_time(screen):
    from config import FONT_PATH
    try:
        font = pygame.font.Font(FONT_PATH, 24)
    except:
        font = pygame.font.SysFont("simhei", 24)

    # 获取已游戏时间（秒）
    elapsed_ms = get_elapsed_time()
    elapsed_seconds = elapsed_ms // 1000
    elapsed_milliseconds = (elapsed_ms % 1000) // 10  # 显示2位毫秒

    # 获取剩余时间
    remaining_ms = get_remaining_time()
    remaining_seconds = remaining_ms // 1000
    remaining_milliseconds = (remaining_ms % 1000) // 10

    # 显示已游戏时间
    time_text = f"时间: {elapsed_seconds}.{elapsed_milliseconds:02d}秒"
    time_surface = font.render(time_text, True, (255, 255, 255))
    time_rect = time_surface.get_rect(topleft=(10, 10))
    screen.blit(time_surface, time_rect)

    # 显示剩余时间（在右侧）
    WIDTH, HEIGHT = get_window_size()
    remaining_text = f"剩余: {remaining_seconds}.{remaining_milliseconds:02d}秒"

    # 根据剩余时间改变颜色
    if remaining_ms > 7000:  # 剩余7秒以上，绿色
        color = (0, 255, 0)
    elif remaining_ms > 3000:  # 剩余3-7秒，黄色
        color = (255, 255, 0)
    else:  # 剩余3秒以内，红色
        color = (255, 0, 0)

    remaining_surface = font.render(remaining_text, True, color)
    remaining_rect = remaining_surface.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(remaining_surface, remaining_rect)

    # 绘制进度条
    progress = min(1.0, elapsed_ms / TIME_LIMIT)
    bar_width = 200
    bar_height = 8
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 40

    # 背景条
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    # 进度条
    pygame.draw.rect(screen, (0, 200, 0) if progress < 0.7 else (255, 200, 0) if progress < 0.9 else (255, 50, 50),
                     (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=4)


def main():
    """游戏主循环（整合所有功能）"""
    # 初始化游戏状态
    clock = pygame.time.Clock()
    current_state = GameState.START
    win_lose_start_time = 0
    is_mouse_up = False  # 鼠标左键松开标记（防止点击过快）
    # ========== 新增：胜利原因 ==========
    win_reason = ""  # "all_balls_absorbed" 或 "time_survived"

    # ========== 新增：成就系统相关变量 ==========
    unlocked_achievement = None
    achievement_show_time = 0
    ACHIEVEMENT_SHOW_DURATION = 3000  # 成就显示3秒

    while True:
        # 帧率控制（获取每帧耗时，用于GIF播放）
        dt = clock.tick(FPS)
        # 实时获取当前窗口尺寸
        WIDTH, HEIGHT = get_window_size()

        # ========== 更新GIF背景帧 ==========
        update_gif_frame(dt)

        # ========== 事件监听 ==========
        mouse_pos = pygame.mouse.get_pos()
        # 重置鼠标松开标记
        is_mouse_up = False

        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            # 窗口缩放事件
            elif event.type == pygame.VIDEORESIZE:
                update_window(event.w, event.h)
                pygame.display.flip()
            # 鼠标左键松开事件（精准检测点击）
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_mouse_up = True

        # ========== 绘制背景 ==========
        background = get_background_image()
        SCREEN.blit(background, (0, 0))

        # ========== 主球跟随逻辑（游戏中） ==========
        if current_state == GameState.PLAYING:
            player_ball = get_player_ball()
            if player_ball is not None:
                player_ball.rect.center = mouse_pos

        # ========== 游戏状态管理 ==========
        # 初始界面
        if current_state == GameState.START:
            draw_text("躲避球", 80, BLUE, WIDTH // 2, HEIGHT // 2 - 100)
            # 开始游戏按钮（粉色+缩小尺寸+玫瑰红反馈）
            start_action = draw_button("开始游戏", WIDTH // 2, HEIGHT // 2 + 80, 160, 55, (255, 182, 193),
                                       (205, 92, 92), "start", is_mouse_up)
            # 点击按钮才跳转难度界面 ✔修复核心逻辑
            if start_action == "start":
                current_state = GameState.SELECT_DIFFICULTY

        # 难度选择界面
        elif current_state == GameState.SELECT_DIFFICULTY:
            draw_text("选择游戏难度", 80, BLUE, WIDTH // 2, HEIGHT // 2 - 180)
            # 难度按钮（传入鼠标松开标记）
            easy_action, normal_action, hell_action = draw_difficulty_buttons(is_mouse_up)
            if easy_action == "easy":
                current_state = reset_game("easy")
                # ========== 新增：通知成就系统开始新游戏 ==========
                used_items = any(get_active_items().values())
                achievement_system.start_new_game("easy", used_items)
            elif normal_action == "normal":
                current_state = reset_game("normal")
                # ========== 新增：通知成就系统开始新游戏 ==========
                used_items = any(get_active_items().values())
                achievement_system.start_new_game("normal", used_items)
            elif hell_action == "hell":
                current_state = reset_game("hell")
                # ========== 新增：通知成就系统开始新游戏 ==========
                used_items = any(get_active_items().values())
                achievement_system.start_new_game("hell", used_items)

        # 游戏中界面
        elif current_state == GameState.PLAYING:
            # 更新精灵状态
            all_sprites.update()
            # 检测彩球入洞（彩球和黑洞都会消失）
            check_ball_hole_collision()

            # ========== 绘制游戏时间 ==========
            draw_game_time(SCREEN)

            # 胜负判定
            if check_player_collision():
                current_state = GameState.LOSE_DISPLAY
                win_lose_start_time = pygame.time.get_ticks()
                win_reason = "lose"
            else:
                win_result, reason = check_win_condition()
                if win_result:
                    current_state = GameState.WIN_DISPLAY
                    win_lose_start_time = pygame.time.get_ticks()
                    win_reason = reason

            # 绘制所有精灵
            all_sprites.draw(SCREEN)

        # 胜利提示界面
        elif current_state == GameState.WIN_DISPLAY:
            current_diff = get_current_difficulty()
            win_text = WIN_TEXT[current_diff]
            draw_text(win_text, 74, GREEN, WIDTH // 2, HEIGHT // 2)

            # ========== 修改：根据胜利原因显示不同提示 ==========
            if win_reason == "time_survived":
                score_to_add = SCORE_RULE[current_diff]
                draw_text(f"坚持10秒胜利！获得{score_to_add}积分", 40, (255, 215, 0), WIDTH // 2, HEIGHT // 2 + 60)
            else:  # all_balls_absorbed
                score_to_add = SCORE_RULE[current_diff]
                draw_text(f"获得 {score_to_add} 积分", 30, (255, 215, 0), WIDTH // 2, HEIGHT // 2 + 60)

            if pygame.time.get_ticks() - win_lose_start_time >= WIN_LOSE_DELAY:
                # ========== 修改：两种胜利方式都给予积分 ==========
                add_score(current_diff)  # 两种胜利方式都用相同的积分

                # ========== 新增：检查并解锁成就 ==========
                new_achievement = achievement_system.check_level_completion(current_diff, win_reason)
                if new_achievement:

                    unlocked_achievement = new_achievement
                    achievement_show_time = pygame.time.get_ticks()

                    # ========== 关键修改：使用顶部提示 ==========
                    from config import set_top_tip
                    tip_text = f"🎉 成就解锁：{new_achievement['name']}"

                    set_top_tip(tip_text, (255, 215, 0))  # 金色提示

                current_state = GameState.END_MENU

        # 失败提示界面
        elif current_state == GameState.LOSE_DISPLAY:
            current_diff = get_current_difficulty()
            lose_text = LOSE_TEXT[current_diff]
            draw_text(lose_text, 74, RED, WIDTH // 2, HEIGHT // 2)
            # 失败积分提示-白色字体清晰可见 ✔优化
            draw_text("积分不变，再接再厉！", 30, BLACK, WIDTH // 2, HEIGHT // 2 + 60)
            if pygame.time.get_ticks() - win_lose_start_time >= WIN_LOSE_DELAY:
                current_state = GameState.END_MENU

        # 结算界面（游戏结束）
        elif current_state == GameState.END_MENU:
            # 绘制结算标题
            draw_text("游戏结束", 74, BLACK, WIDTH // 2, HEIGHT // 2 - 180)
            # 绘制当前总积分
            draw_end_menu_score()

            # 绘制道具信息
            draw_score_item_info(SCREEN)

            # 重新开始+退出游戏按钮 ✔修复变量名+文字+位置+样式
            restart_action = draw_button("重新开始", WIDTH // 2 - 100, HEIGHT // 2 + 40, 160, 55, (255, 182, 193),
                                         (205, 92, 92), "restart", is_mouse_up)
            quit_action = draw_button("退出游戏", WIDTH // 2+100, HEIGHT // 2 + 40, 160, 55, (255, 182, 193), (205, 92, 92),
                                      "quit", is_mouse_up)

            # ========== 新增：成就按钮（右下角） ==========
            achievement_action = draw_button("查看成就", WIDTH - 100, HEIGHT - 80, 160, 55, (255, 182, 193),
                                             (205, 92, 92), "achievements", is_mouse_up)

            # 道具购买按钮
            item1_action, item2_action, use_item_action = draw_item_buttons(is_mouse_up)

            # 处理道具购买逻辑
            if item1_action == "buy_item1":
                success, msg = buy_item("item1")
                if success:
                    # 购买道具即视为使用道具（因为道具会在下一局生效）
                    achievement_system.mark_item_used()

            if item2_action == "buy_item2":
                success, msg = buy_item("item2")
                if success:
                    # 购买道具即视为使用道具（因为道具会在下一局生效）
                    achievement_system.mark_item_used()

            # 处理道具使用逻辑
            if use_item_action == "use_item":
                from score_item_system import use_all_items
                used = use_all_items()
                if used:
                    # 使用道具
                    achievement_system.mark_item_used()

            # 按钮事件响应
            if restart_action == "restart":
                current_state = GameState.START
            elif quit_action == "quit":
                pygame.quit()
                return
            elif achievement_action == "achievements":
                current_state = GameState.ACHIEVEMENTS

        # ========== 新增：成就界面 ==========
        elif current_state == GameState.ACHIEVEMENTS:
            # 绘制成就界面标题
            draw_text("成就系统", 80, BLUE, WIDTH // 2, 80)

            # 绘制成就统计
            unlocked_count, total_count = achievement_system.get_achievement_count()
            draw_text(f"已解锁：{unlocked_count}/{total_count}", 36, (255, 215, 0), WIDTH // 2, 140)

            # 绘制所有成就
            start_y = 180
            achievement_system.draw_achievement_list(SCREEN, WIDTH // 2 - 200, start_y, show_hidden=True)

            # 返回按钮（右下角）
            back_action = draw_button("返回", WIDTH - 100, HEIGHT - 80, 160, 55, (255, 182, 193), (205, 92, 92), "back",
                                      is_mouse_up)

            if back_action == "back":
                current_state = GameState.END_MENU

        # 绘制全局提示（包括成就提示）
        draw_tip(SCREEN)

        # 更新屏幕显示
        pygame.display.flip()


if __name__ == "__main__":
    # 启动游戏主循环
    main()