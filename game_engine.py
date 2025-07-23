import random
import re
from typing import List, Dict, Optional
from roles import Role, get_role_info
from player_agent import LLMPlayerAgent
from logger import GameLogger
import json

def extract_player_id(text, candidates):
    """
    从LLM返回文本中提取player_id，优先返回candidates中的数字。
    """
    numbers = re.findall(r'\d+', text)
    for num in numbers:
        if int(num) in candidates:
            return int(num)
    # fallback: 返回第一个候选
    return candidates[0]

class GameEngine:
    """
    游戏引擎，负责狼人杀流程控制。
    """
    def __init__(self, num_players: int, role_distribution: Dict[Role, int], language: str = 'en'):
        self.num_players = num_players
        self.role_distribution = role_distribution
        self.players: List[LLMPlayerAgent] = []
        self.logger = GameLogger()
        self.round = 0
        self.history: List[Dict] = []  # 记录每一轮的事件
        self.language = language

    def assign_roles(self):
        """
        随机分配身份。
        """
        roles = []
        for role, count in self.role_distribution.items():
            roles.extend([role] * count)
        random.shuffle(roles)
        self.players = [LLMPlayerAgent(i, roles[i]) for i in range(self.num_players)]
        self.logger.log_roles(self.players)

    def get_alive_players(self) -> List[LLMPlayerAgent]:
        """
        获取存活玩家列表。
        """
        return [p for p in self.players if p.is_alive]

    def get_role_prompt(self, role: Role) -> str:
        """
        返回每个角色的prompt说明，支持中英文。
        """
        if self.language == 'zh':
            if role == Role.WOLF:
                return (
                    "身份：狼人\n"
                    "你的目标是隐藏身份并消灭所有好人和特殊角色。绝不能暴露自己是狼人。发言时要混淆视听，保护同伴，逻辑谨慎。不要用‘作为狼人...’等暴露身份的话。\n"
                    "重要：除非有特殊策略，否则绝不直接暴露身份。不要泄露只有狼人知道的信息。发言要自然、符合身份目标。始终考虑角色视角和信息限制。"
                )
            elif role == Role.VILLAGER:
                return (
                    "身份：平民\n"
                    "你的目标是通过发言和投票找出狼人。你不知道其他人的身份。发言时要分享推理和怀疑，鼓励大家讨论。除非有特殊策略，不要假冒特殊身份。\n"
                    "重要：除非有特殊策略，否则绝不直接暴露身份。不要泄露只有特殊角色知道的信息。发言要自然、符合身份目标。始终考虑角色视角和信息限制。"
                )
            elif role == Role.SEER:
                return (
                    "身份：预言家\n"
                    "你的目标是通过查验帮助好人找出狼人。每晚可查验一人身份。白天可根据查验结果引导讨论，但要谨慎暴露身份。若要自爆需有证据。\n"
                    "重要：除非有特殊策略，否则绝不直接暴露身份。不要泄露只有预言家知道的信息。发言要自然、符合身份目标。始终考虑角色视角和信息限制。"
                )
            elif role == Role.WITCH:
                return (
                    "身份：女巫\n"
                    "你的目标是帮助好人阵营。你有一瓶解药和一瓶毒药，夜晚可救人或毒人。用药要谨慎。发言时不要轻易暴露身份。\n"
                    "重要：除非有特殊策略，否则绝不直接暴露身份。不要泄露只有女巫知道的信息。发言要自然、符合身份目标。始终考虑角色视角和信息限制。"
                )
            elif role == Role.HUNTER:
                return (
                    "身份：猎人\n"
                    "你的目标是帮助好人获胜。被淘汰时可带走一人。平时发言如普通村民，不要轻易暴露身份。\n"
                    "重要：除非有特殊策略，否则绝不直接暴露身份。不要泄露只有猎人知道的信息。发言要自然、符合身份目标。始终考虑角色视角和信息限制。"
                )
            else:
                return "你是游戏中的一名玩家，请根据身份和规则行动。"
        else:
            if role == Role.WOLF:
                return (
                    "Role: Werewolf\n"
                    "Your goal is to eliminate all villagers and special roles without being discovered. "
                    "You must hide your identity at all costs. Never admit or hint that you are a werewolf. "
                    "During discussions, try to blend in with the villagers, cast suspicion on others, and protect your fellow werewolves. "
                    "Your speech should be logical, cautious, and misleading if necessary. "
                    "Do not use phrases like 'As a werewolf...' or anything that reveals your true role.\n"
                    "Important: Never directly state your true role unless it is part of your strategy or the game situation requires it. "
                    "Avoid giving away information that only your role would know. "
                    "Your speech should be natural, logical, and consistent with your role’s objectives. "
                    "Always consider the perspective and knowledge limitations of your character."
                )
            elif role == Role.VILLAGER:
                return (
                    "Role: Villager\n"
                    "Your goal is to find out who the werewolves are and help eliminate them through discussion and voting. "
                    "You do not know anyone else’s role. "
                    "During your speech, share your observations, suspicions, and logical reasoning. "
                    "Encourage others to speak and analyze their words and actions. "
                    "Never claim to be a special role unless you have a strategic reason.\n"
                    "Important: Never directly state your true role unless it is part of your strategy or the game situation requires it. "
                    "Avoid giving away information that only your role would know. "
                    "Your speech should be natural, logical, and consistent with your role’s objectives. "
                    "Always consider the perspective and knowledge limitations of your character."
                )
            elif role == Role.SEER:
                return (
                    "Role: Seer (Prophet)\n"
                    "Your goal is to help the villagers by identifying the werewolves. "
                    "Each night, you can check one player’s true identity. "
                    "During the day, you may choose to subtly guide the discussion based on your knowledge, but be careful not to expose yourself too early. "
                    "If you decide to reveal your role, do so with caution and provide evidence to support your claims.\n"
                    "Important: Never directly state your true role unless it is part of your strategy or the game situation requires it. "
                    "Avoid giving away information that only your role would know. "
                    "Your speech should be natural, logical, and consistent with your role’s objectives. "
                    "Always consider the perspective and knowledge limitations of your character."
                )
            elif role == Role.WITCH:
                return (
                    "Role: Witch\n"
                    "Your goal is to help the villagers survive. "
                    "You have two potions: one to save a player who was attacked at night, and one to eliminate a player. "
                    "Use your abilities wisely. "
                    "During discussions, do not reveal your role unless absolutely necessary. "
                    "Share your suspicions and observations as a normal villager would, unless you have a strategic reason to reveal your identity.\n"
                    "Important: Never directly state your true role unless it is part of your strategy or the game situation requires it. "
                    "Avoid giving away information that only your role would know. "
                    "Your speech should be natural, logical, and consistent with your role’s objectives. "
                    "Always consider the perspective and knowledge limitations of your character."
                )
            elif role == Role.HUNTER:
                return (
                    "Role: Hunter\n"
                    "Your goal is to help the villagers win. "
                    "If you are eliminated, you can choose to take another player down with you. "
                    "During discussions, act as a normal villager. "
                    "Do not reveal your role unless you have a strategic reason, such as being in danger of elimination. "
                    "Share your reasoning and suspicions to help the group.\n"
                    "Important: Never directly state your true role unless it is part of your strategy or the game situation requires it. "
                    "Avoid giving away information that only your role would know. "
                    "Your speech should be natural, logical, and consistent with your role’s objectives. "
                    "Always consider the perspective and knowledge limitations of your character."
                )
            else:
                return "You are a player in the game. Please act according to your role and the game rules."

    def night_phase(self):
        """
        夜晚阶段，狼人杀人，预言家查验等。
        """
        wolves = [p for p in self.get_alive_players() if p.role == Role.WOLF]
        villagers = [p for p in self.get_alive_players() if p.role != Role.WOLF]
        if not wolves or not villagers:
            return None, None
        # 1. 狼人杀人
        wolf_prompt = (
            self.get_role_prompt(Role.WOLF) +
            "\nTonight, choose a player to kill. "
            "Alive players: {villagers}. Return the player id only."
        )
        candidates = [v.player_id for v in villagers]
        wolf_prompt_str = wolf_prompt.format(villagers=candidates)
        response = wolves[0].make_speech(
            game_history=self.history,
            prompt_template=wolf_prompt_str
        )
        self.logger.log_prompt(wolves[0].player_id, self.round, 'night_wolf', wolf_prompt_str, response)
        wolf_target = extract_player_id(response, candidates)
        # 2. 预言家查验身份
        seers = [p for p in self.get_alive_players() if p.role == Role.SEER]
        seer_result = None
        if seers:
            seer = seers[0]
            seer_candidates = [p.player_id for p in self.get_alive_players() if p.player_id != seer.player_id]
            seer_prompt = (
                self.get_role_prompt(Role.SEER) +
                "\nTonight, you can check the true identity of one player. "
                "Alive players: {candidates}. Return the player id only."
            )
            seer_prompt_str = seer_prompt.format(candidates=seer_candidates)
            seer_response = seer.make_speech(self.history, seer_prompt_str)
            self.logger.log_prompt(seer.player_id, self.round, 'night_seer', seer_prompt_str, seer_response)
            seer_check_id = extract_player_id(seer_response, seer_candidates)
            checked_player = next((p for p in self.players if p.player_id == seer_check_id), None)
            if checked_player:
                # 只返回好人/坏人
                camp = get_role_info(checked_player.role).get('camp', '')
                if camp == '狼人阵营':
                    seer_result = {"checked_id": seer_check_id, "result": "Bad"}
                else:
                    seer_result = {"checked_id": seer_check_id, "result": "Good"}
                # 记录查验结果到seer.extra_info['all_checks']
                if "all_checks" not in seer.extra_info:
                    seer.extra_info["all_checks"] = []
                seer.extra_info["all_checks"].append(seer_result)
                seer.extra_info["last_check"] = seer_result
        # 3. 女巫用药
        witches = [p for p in self.get_alive_players() if p.role == Role.WITCH]
        witch_save = False
        witch_poison_id = None
        if witches:
            witch = witches[0]
            # 初始化女巫药水使用情况
            if "save_used" not in witch.extra_info:
                witch.extra_info["save_used"] = False
            if "poison_used" not in witch.extra_info:
                witch.extra_info["poison_used"] = False
            # 解药
            if not witch.extra_info["save_used"]:
                save_prompt = (
                    self.get_role_prompt(Role.WITCH) +
                    f"\nTonight, player {wolf_target} was attacked by the werewolves. "
                    "Do you want to use your healing potion to save them? Answer 'yes' or 'no'."
                )
                save_response = witch.make_speech(self.history, save_prompt)
                self.logger.log_prompt(witch.player_id, self.round, 'night_witch_save', save_prompt, save_response)
                if "yes" in save_response.lower():
                    witch_save = True
                    witch.extra_info["save_used"] = True
            # 毒药
            if not witch.extra_info["poison_used"]:
                poison_candidates = [p.player_id for p in self.get_alive_players() if p.player_id != witch.player_id and p.player_id != wolf_target]
                if poison_candidates:
                    poison_prompt = (
                        self.get_role_prompt(Role.WITCH) +
                        f"\nYou may use your poison potion tonight. "
                        f"Alive players (excluding yourself and the attacked): {poison_candidates}. "
                        "If you want to use poison, return the player id to poison. If not, return 'no'."
                    )
                    poison_response = witch.make_speech(self.history, poison_prompt)
                    self.logger.log_prompt(witch.player_id, self.round, 'night_witch_poison', poison_prompt, poison_response)
                    if poison_response.strip().isdigit():
                        poison_id = int(poison_response.strip())
                        if poison_id in poison_candidates:
                            witch_poison_id = poison_id
                            witch.extra_info["poison_used"] = True
        # 结算死亡
        killed = None
        poisoned = None
        if not witch_save:
            killed = wolf_target
        if witch_poison_id is not None:
            poisoned = witch_poison_id
            # 立即死亡
            for player in self.players:
                if player.player_id == poisoned:
                    player.is_alive = False
        if killed is not None:
            for player in self.players:
                if player.player_id == killed:
                    player.is_alive = False
        # 日志
        log = {
            "round": self.round,
            "phase": "night",
            "wolves": [w.player_id for w in wolves],
            "killed": killed,
            "seer_check": seer_result,  # 预言家查验结果（player_id, Good/Bad）
            "witch_action": {
                "save_used": witches[0].extra_info["save_used"] if witches else None,
                "save_target": wolf_target if witches and "save_used" in witches[0].extra_info and witches[0].extra_info["save_used"] else None,
                "poison_used": witches[0].extra_info["poison_used"] if witches else None,
                "poison_target": witch_poison_id if witches and "poison_used" in witches[0].extra_info and witches[0].extra_info["poison_used"] else None
            }
        }
        self.logger.log_night(self.round, wolves, killed, log)
        self.history.append(log)
        return killed, poisoned

    def get_player_history(self, player: LLMPlayerAgent) -> list:
        """
        构造该玩家视角下可见的历史信息（视角隔离）。
        - 只包含白天公开信息（发言、投票、淘汰结果）
        - 预言家额外看到自己的查验结果
        - 女巫额外看到自己的用药情况
        """
        visible = []
        for log in self.history:
            if log.get('phase') in ['day_speech', 'day_vote', 'result']:
                visible.append(log)
        # 预言家查验信息
        if player.role == Role.SEER and 'all_checks' in player.extra_info:
            visible.append({'seer_checks': player.extra_info['all_checks']})
        # 女巫用药信息
        if player.role == Role.WITCH:
            witch_info = {}
            if 'save_used' in player.extra_info:
                witch_info['save_used'] = player.extra_info['save_used']
            if 'poison_used' in player.extra_info:
                witch_info['poison_used'] = player.extra_info['poison_used']
            if witch_info:
                visible.append({'witch_info': witch_info})
        return visible

    def day_phase(self):
        """
        白天阶段，玩家发言和投票。
        """
        speeches = []
        alive_players = self.get_alive_players()
        for player in alive_players:
            # 预言家所有查验结果提示
            seer_info = ""
            if player.role == Role.SEER and "all_checks" in player.extra_info:
                checks = player.extra_info["all_checks"]
                if checks:
                    check_lines = [f"Player {c['checked_id']}: {c['result']}" for c in checks]
                    seer_info = "\n[You have checked the following players: " + ", ".join(check_lines) + ". Only you know this information.]"
            speech_prompt = (
                self.get_role_prompt(player.role) +
                seer_info +
                "\nYou are player {player_id} (role hidden). Please make a short speech about your thoughts. "
                "Game history: {history}"
            )
            player_history = self.get_player_history(player)
            speech_prompt_str = speech_prompt.replace(
                "{player_id}", str(player.player_id)
            ).replace(
                "{history}", json.dumps(player_history, ensure_ascii=False)
            )
            speech = player.make_speech(player_history, speech_prompt_str)
            self.logger.log_prompt(player.player_id, self.round, 'day_speech', speech_prompt_str, speech)
            speeches.append({"player_id": player.player_id, "speech": speech})
        log_speeches = {
            "round": self.round,
            "phase": "day_speech",
            "speeches": speeches
        }
        self.logger.log_speeches(self.round, speeches)
        self.history.append(log_speeches)
        # 投票
        for player in alive_players:
            vote_prompt = (
                self.get_role_prompt(player.role) +
                "\nYou are player {player_id} (role hidden). Vote to eliminate one player from candidates={candidates}. "
                "Game history: {history}. Return the player id only."
            )
            player_history = self.get_player_history(player)
            vote_prompt_str = vote_prompt.replace(
                "{player_id}", str(player.player_id)
            ).replace(
                "{candidates}", str([p.player_id for p in alive_players])
            ).replace(
                "{history}", json.dumps(player_history, ensure_ascii=False)
            )
            response = player.vote([p.player_id for p in alive_players], player_history, vote_prompt_str)
            self.logger.log_prompt(player.player_id, self.round, 'day_vote', vote_prompt_str, response)
            vote = extract_player_id(str(response), [p.player_id for p in alive_players])
            if 'votes' not in locals():
                votes = {}
            votes[player.player_id] = vote
        vote_count = {}
        for v in votes.values():
            vote_count[v] = vote_count.get(v, 0) + 1
        eliminated = max(vote_count, key=vote_count.get)
        for player in self.players:
            if player.player_id == eliminated:
                player.is_alive = False
        log_votes = {
            "round": self.round,
            "phase": "day_vote",
            "votes": votes,
            "eliminated": eliminated
        }
        self.logger.log_votes(self.round, votes, eliminated)
        self.history.append(log_votes)
        return eliminated

    def check_win(self) -> Optional[str]:
        """
        判断胜负。
        """
        alive = self.get_alive_players()
        wolves = [p for p in alive if p.role == Role.WOLF]
        others = [p for p in alive if p.role != Role.WOLF]
        if not wolves:
            return "Villagers win!"
        if len(wolves) >= len(others):
            return "Wolves win!"
        return None

    def run(self):
        """
        运行游戏主循环。
        """
        self.assign_roles()
        while True:
            self.round += 1
            # Night phase
            killed, _ = self.night_phase()
            if killed is not None:
                for player in self.players:
                    if player.player_id == killed:
                        player.is_alive = False
            # Day phase
            eliminated = self.day_phase()
            # 检查胜负
            result = self.check_win()
            if result:
                self.logger.log_result(result)
                break 