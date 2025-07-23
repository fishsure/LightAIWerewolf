from enum import Enum
from typing import Dict, Optional

class Role(Enum):
    WOLF = "狼人"
    VILLAGER = "平民"
    SEER = "预言家"
    WITCH = "女巫"
    HUNTER = "猎人"

ROLE_INFO: Dict[Role, Dict[str, Optional[str]]] = {
    Role.WOLF: {
        "camp": "狼人阵营",
        "desc": "每晚可与其他狼人协商杀死一名玩家。",
        "night_action": "选择一名玩家进行击杀。"
    },
    Role.VILLAGER: {
        "camp": "好人阵营",
        "desc": "没有特殊技能，白天参与讨论和投票。",
        "night_action": None
    },
    Role.SEER: {
        "camp": "好人阵营",
        "desc": "每晚可查验一名玩家的真实身份。",
        "night_action": "查验一名玩家身份。"
    },
    Role.WITCH: {
        "camp": "好人阵营",
        "desc": "有一瓶解药和一瓶毒药，夜晚可救人或毒人。",
        "night_action": "选择是否用药救人或毒人。"
    },
    Role.HUNTER: {
        "camp": "好人阵营",
        "desc": "被淘汰时可带走一名玩家。",
        "night_action": None
    },
}

def get_role_info(role: Role) -> Dict[str, Optional[str]]:
    return ROLE_INFO.get(role, {}) 