"""
成就系统模块
处理成就的解锁、保存、加载和显示
"""
import pygame
import json
import os
import sys


class AchievementSystem:
    """
    成就系统类
    管理所有成就的解锁状态和显示
    """

    def __init__(self):
        """初始化成就系统，加载成就定义和保存数据"""
        # 成就定义 - 只保留三个难度通关成就
        self.achievements = {
            "first_easy": {
                "id": "first_easy",
                "name": "小试牛刀",
                "description": "首次通过简单难度",
                "icon": "🥉",  # 可以用emoji或图片
                "unlocked": False,
                "hidden": False,
                "unlock_time": None
            },
            "first_normal": {
                "id": "first_normal",
                "name": "登堂入室",
                "description": "首次通过普通难度",
                "icon": "🥈",
                "unlocked": False,
                "hidden": False,
                "unlock_time": None
            },
            "first_hell": {
                "id": "first_hell",
                "name": "已臻化境",
                "description": "首次通过地狱难度",
                "icon": "🥇",
                "unlocked": False,
                "hidden": False,
                "unlock_time": None
            }
            # 已删除："hell_no_items" - 天下无敌成就
        }

        # 当前游戏状态追踪
        self.current_difficulty = None  # 当前游戏难度

        # 加载已解锁的成就
        self.load_achievements()

    def get_save_path(self):
        """
        获取成就数据保存路径（兼容exe和开发环境）

        Returns:
            str: 成就数据文件路径
        """
        try:
            # 如果是exe文件，保存到用户目录
            if getattr(sys, 'frozen', False):
                # 运行在PyInstaller打包的exe中
                if sys.platform == 'win32':
                    # Windows: 保存到用户的AppData/Roaming目录
                    appdata_path = os.getenv('APPDATA')
                    save_dir = os.path.join(appdata_path, '躲避球游戏')
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    return os.path.join(save_dir, 'achievements.json')
                else:
                    # macOS/Linux: 保存到用户home目录
                    home_path = os.path.expanduser('~')
                    save_dir = os.path.join(home_path, '.躲避球游戏')
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    return os.path.join(save_dir, 'achievements.json')
            else:
                # 开发环境：保存在当前目录
                return "achievements.json"
        except:
            # 出错时使用当前目录
            return "achievements.json"

    def load_achievements(self):
        """从文件加载已解锁的成就"""
        save_path = self.get_save_path()
        try:
            if os.path.exists(save_path):
                with open(save_path, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    for key, data in saved_data.items():
                        if key in self.achievements:
                            # 更新成就状态
                            self.achievements[key].update(data)
                print(f"从 {save_path} 加载成就数据")
        except Exception as e:
            print(f"加载成就数据失败: {e}")

    def save_achievements(self):
        """保存成就数据到文件"""
        save_path = self.get_save_path()
        try:
            save_data = {}
            for key, achievement in self.achievements.items():
                # 只保存必要的数据
                save_data[key] = {
                    "unlocked": achievement["unlocked"],
                    "unlock_time": achievement["unlock_time"]
                }

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"成就数据保存到: {save_path}")
        except Exception as e:
            print(f"保存成就数据失败: {e}")

    def start_new_game(self, difficulty, used_items=False):
        """
        开始新游戏时调用，设置当前游戏状态

        Args:
            difficulty: 游戏难度
            used_items: 是否使用了道具（不再需要追踪道具使用）
        """
        self.current_difficulty = difficulty


    def mark_item_used(self):
        """当玩家使用道具时调用（保留方法，但现在不需要特殊处理）"""
        # 不再需要追踪道具使用情况
        pass

    def check_level_completion(self, difficulty, win_reason):
        """
        关卡完成时调用，检查是否解锁新成就

        Args:
            difficulty: 完成的难度
            win_reason: 胜利原因 ("all_balls_absorbed" 或 "time_survived" 或 "lose")

        Returns:
            dict or None: 解锁的成就信息，如果没有解锁返回None
        """
        achievement_unlocked = None
        achievement_key = f"first_{difficulty}"

        # 只检查首次通关成就
        if (achievement_key in self.achievements and
                not self.achievements[achievement_key]["unlocked"] and
                win_reason != "lose"):  # 只有胜利时才解锁成就

            achievement_unlocked = self.unlock_achievement(
                achievement_key,
                f"首次通过{difficulty}难度！"
            )

        return achievement_unlocked

    def unlock_achievement(self, achievement_id, message=""):
        """
        解锁成就

        Args:
            achievement_id: 成就ID
            message: 解锁消息

        Returns:
            dict or None: 成就信息字典，如果成就已解锁或不存在返回None
        """
        if (achievement_id in self.achievements and
                not self.achievements[achievement_id]["unlocked"]):
            achievement = self.achievements[achievement_id]
            achievement["unlocked"] = True
            achievement["unlock_time"] = pygame.time.get_ticks()

            print(f"🎉 成就解锁: {achievement['name']} - {achievement['description']}")

            # 保存到文件
            self.save_achievements()

            # 返回成就信息用于显示
            return {
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"],
                "message": message
            }
        return None

    def get_unlocked_achievements(self):
        """获取已解锁的成就列表"""
        return [achievement for achievement in self.achievements.values()
                if achievement["unlocked"]]

    def get_achievement_count(self):
        """
        获取成就统计

        Returns:
            tuple: (已解锁数量, 总数量)
        """
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())
        return unlocked, total

    def get_recent_achievements(self, count=3):
        """
        获取最近解锁的成就

        Args:
            count: 要获取的成就数量

        Returns:
            list: 最近解锁的成就列表
        """
        unlocked = self.get_unlocked_achievements()
        # 按解锁时间排序（最新的在前）
        sorted_achievements = sorted(
            unlocked,
            key=lambda x: x["unlock_time"] if x["unlock_time"] else 0,
            reverse=True
        )
        return sorted_achievements[:count]

    def draw_achievement_list(self, screen, x, y, show_hidden=False):
        """
        在指定位置绘制成就列表

        Args:
            screen: Pygame屏幕Surface
            x: 列表起始x坐标
            y: 列表起始y坐标
            show_hidden: 是否显示隐藏成就（现在没有隐藏成就）
        """
        try:
            from config import FONT_PATH
            title_font = pygame.font.Font(FONT_PATH, 24)
            font = pygame.font.Font(FONT_PATH, 20)
        except:
            title_font = pygame.font.SysFont("simhei", 24)
            font = pygame.font.SysFont("simhei", 20)

        y_offset = y

        # 绘制每个成就（现在所有成就都是公开的）
        for achievement in self.achievements.values():
            # 成就条目背景
            entry_width = 400
            entry_height = 80
            entry_rect = pygame.Rect(x, y_offset, entry_width, entry_height)

            # 根据是否解锁选择颜色
            if achievement["unlocked"]:
                # 已解锁：金色边框，深色背景
                pygame.draw.rect(screen, (50, 50, 70), entry_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 215, 0), entry_rect, 2, border_radius=8)
            else:
                # 未解锁：灰色边框，更深的背景
                pygame.draw.rect(screen, (40, 40, 50), entry_rect, border_radius=8)
                pygame.draw.rect(screen, (100, 100, 100), entry_rect, 2, border_radius=8)

            # 图标（未解锁时显示为问号）
            icon_text = achievement["icon"] if achievement["unlocked"] else "❓"
            icon_color = (255, 215, 0) if achievement["unlocked"] else (100, 100, 100)
            icon_surface = font.render(icon_text, True, icon_color)
            icon_rect = icon_surface.get_rect(center=(x + 40, y_offset + entry_height // 2))
            screen.blit(icon_surface, icon_rect)

            # 成就名称
            name_color = (255, 255, 255) if achievement["unlocked"] else (150, 150, 150)
            name_surface = font.render(achievement["name"], True, name_color)
            name_rect = name_surface.get_rect(topleft=(x + 80, y_offset + 15))
            screen.blit(name_surface, name_rect)

            # 成就描述（未解锁时显示为？？？）
            desc_color = (200, 200, 200) if achievement["unlocked"] else (100, 100, 100)
            desc_text = achievement["description"] if achievement["unlocked"] else "？？？"

            # 获取小字体
            try:
                desc_font = pygame.font.Font(FONT_PATH, 16)
            except:
                desc_font = pygame.font.SysFont("simhei", 16)

            desc_surface = desc_font.render(desc_text, True, desc_color)
            desc_rect = desc_surface.get_rect(topleft=(x + 80, y_offset + 45))
            screen.blit(desc_surface, desc_rect)

            # 解锁状态指示器
            status_rect = pygame.Rect(x + entry_width - 30, y_offset + entry_height // 2 - 10, 20, 20)
            if achievement["unlocked"]:
                pygame.draw.circle(screen, (0, 255, 0), status_rect.center, 8)

                # 对勾标记
                try:
                    check_font = pygame.font.Font(FONT_PATH, 16)
                except:
                    check_font = pygame.font.SysFont("simhei", 16)

                check_surface = check_font.render("✓", True, (255, 255, 255))
                check_rect = check_surface.get_rect(center=status_rect.center)
                screen.blit(check_surface, check_rect)
            else:
                pygame.draw.circle(screen, (100, 100, 100), status_rect.center, 8)

            y_offset += entry_height + 15


# 全局成就系统实例
achievement_system = AchievementSystem()