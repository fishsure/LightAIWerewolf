# werewolf_llm/main.py

# 游戏入口

from roles import Role
from game_engine import GameEngine

if __name__ == "__main__":
    import sys
    # 设置玩家数量和身份分布
    # 例如：2狼，1预言家，1女巫，1猎人，5平民
    num_players = 10
    role_distribution = {
        Role.WOLF: 2,
        Role.SEER: 1,
        Role.WITCH: 1,
        Role.HUNTER: 1,
        Role.VILLAGER: 5
    }
    # 语言参数，默认英文，可通过命令行传递'zh'或'en'
    language = 'en'
    if len(sys.argv) > 1 and sys.argv[1] in ['en', 'zh']:
        language = sys.argv[1]
    # 启动游戏引擎
    engine = GameEngine(num_players, role_distribution, language=language)
    engine.run()
    # 保存日志
    engine.logger.save("game_log.json")
    print("Game finished. Log saved to game_log.json.") 