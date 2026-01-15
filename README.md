# 《躲避球》游戏 - Python课程设计

## 项目简介
一个基于Python/Pygame开发的2D躲避球游戏，具有双重胜利条件、成就系统等创新设计。

## 功能特性
- ✅ 双重胜利机制（时间生存/目标清除）
- ✅ 多层次碰撞检测系统
- ✅ 积分道具经济系统
- ✅ 成就系统与跨平台数据存储
- ✅ 三种难度模式

## 快速开始
1. 安装Python 3.x
2. 安装依赖：`pip install pygame pillow`
3. 运行游戏：`python main.py`

## 系统架构总览
main.py（主控制器 / 程序入口）
├── config.py（配置中心 / 参数仓库）
├── game_logic.py（游戏引擎 / 核心规则）
│   ├── sprites.py（游戏对象 / 实体定义）
│   └── score_item_system.py（经济系统 / 积分道具）
├── ui.py（界面显示 / 用户交互）
└── achievement_system.py（成就系统 / 进度记录）

## 论文摘要
本项目对应重庆理工大学课程设计论文《基于Python的《play the ball》》，详细设计见文档。

## 作者
wukey
