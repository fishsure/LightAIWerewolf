import json
from typing import List, Dict, Any
from player_agent import LLMPlayerAgent

class GameLogger:
    """
    游戏日志记录类，结构化记录游戏过程。
    """
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.roles: Dict[int, str] = {}
        self.result: str = ""
        self.detailed_prompts: List[Dict[str, Any]] = []  # 新增详细prompt日志

    def log_roles(self, players: List[LLMPlayerAgent]):
        """
        记录身份分配。
        """
        self.roles = {p.player_id: p.role.value for p in players}
        print(f"[LOG] Roles assigned: {self.roles}")
        print(json.dumps({"roles": self.roles}, indent=2, ensure_ascii=False))

    def log_night(self, round_num: int, wolves: List[LLMPlayerAgent], killed_id: int, log: dict = None):
        """
        记录夜晚事件。
        """
        if log is None:
            log = {
                "round": round_num,
                "phase": "night",
                "wolves": [w.player_id for w in wolves],
                "killed": killed_id
            }
        self.logs.append(log)
        print(f"[LOG] Night {round_num}: Wolves killed player {killed_id}")
        print(json.dumps(log, indent=2, ensure_ascii=False))

    def log_speeches(self, round_num: int, speeches: List[Dict]):
        """
        记录白天发言。
        """
        log = {
            "round": round_num,
            "phase": "day_speech",
            "speeches": speeches
        }
        self.logs.append(log)
        print(f"[LOG] Day {round_num}: Speeches recorded.")
        print(json.dumps(log, indent=2, ensure_ascii=False))

    def log_votes(self, round_num: int, votes: Dict[int, int], eliminated: int):
        """
        记录投票结果。
        """
        log = {
            "round": round_num,
            "phase": "day_vote",
            "votes": votes,
            "eliminated": eliminated
        }
        self.logs.append(log)
        print(f"[LOG] Day {round_num}: Player {eliminated} eliminated by vote.")
        print(json.dumps(log, indent=2, ensure_ascii=False))

    def log_result(self, result: str):
        """
        记录游戏胜负结果。
        """
        self.result = result
        log = {
            "phase": "result",
            "result": result
        }
        self.logs.append(log)
        print(f"[LOG] Game result: {result}")
        print(json.dumps(log, indent=2, ensure_ascii=False))

    def log_prompt(self, player_id: int, round_num: int, phase: str, prompt: str, response: str):
        """
        记录每个玩家每轮的prompt和LLM回复。
        """
        entry = {
            "player_id": player_id,
            "round": round_num,
            "phase": phase,
            "prompt": prompt,
            "response": response
        }
        self.detailed_prompts.append(entry)
        print(f"[PROMPT LOG] Player {player_id} Round {round_num} Phase {phase}\nPrompt: {prompt}\nResponse: {response}\n")

    def save(self, filename: str = "game_log.json"):
        """
        保存日志到文件。
        """
        data = {
            "roles": self.roles,
            "logs": self.logs,
            "result": self.result,
            "detailed_prompts": self.detailed_prompts  # 保存详细prompt日志
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[LOG] Game log saved to {filename}") 