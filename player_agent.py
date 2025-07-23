from roles import Role
from typing import Optional, List, Dict
from llm_api import call_llm_api

class Player:
    """
    玩家基础类，包含ID、角色、存活状态等属性。
    """
    def __init__(self, player_id: int, role: Role):
        self.player_id = player_id
        self.role = role
        self.is_alive = True
        self.is_protected = False  # 是否被守卫保护
        self.extra_info: Dict = {}  # 角色特有信息

    def __repr__(self):
        return f"Player({self.player_id}, {self.role}, Alive={self.is_alive})"

class LLMPlayerAgent(Player):
    """
    LLM玩家代理类，负责与LLM API交互，生成发言、投票等。
    """
    def __init__(self, player_id: int, role: Role, name: Optional[str] = None):
        super().__init__(player_id, role)
        self.name = name or f"Player{player_id}"

    def make_speech(self, game_history: List[Dict], prompt_template: str) -> str:
        """
        生成发言，调用LLM API。
        game_history: 游戏历史记录
        prompt_template: 英文prompt模板（已格式化）
        """
        # prompt_template 已经格式化好，直接用
        prompt = prompt_template
        response = call_llm_api(prompt)
        return response

    def vote(self, candidates: List[int], game_history: List[Dict], prompt_template: str) -> int:
        """
        生成投票决策，调用LLM API。
        candidates: 可投票的玩家ID列表
        prompt_template: 英文prompt模板（已格式化）
        """
        prompt = prompt_template
        response = call_llm_api(prompt)
        # 假设返回的是被投票玩家ID
        try:
            vote_id = int(response)
        except Exception:
            vote_id = candidates[0]  # fallback
        return vote_id 