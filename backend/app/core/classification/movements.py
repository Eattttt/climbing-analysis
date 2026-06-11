from enum import Enum
from dataclasses import dataclass


class MovementType(str, Enum):
    FLAG = "flag"
    DROP_KNEE = "drop_knee"
    DYNO = "dyno"
    DEADPOINT = "deadpoint"
    CAMPUSING = "campusing"
    CUT_LOOSE = "cut_loose"
    ROCK_OVER = "rock_over"
    BARN_DOOR = "barn_door"
    MATCHING = "matching"
    STEMMING = "stemming"
    KNEE_BAR = "knee_bar"
    SIDE_BODY = "side_body"
    STATIC = "static"
    REST = "rest"


MOVEMENT_LABELS_CN: dict[str, str] = {
    MovementType.FLAG: "旗式",
    MovementType.DROP_KNEE: "折膝",
    MovementType.DYNO: "动态跳跃",
    MovementType.DEADPOINT: "死点",
    MovementType.CAMPUSING: "无脚攀登",
    MovementType.CUT_LOOSE: "脱脚",
    MovementType.ROCK_OVER: "翻越",
    MovementType.BARN_DOOR: "开门",
    MovementType.MATCHING: "换手/换脚",
    MovementType.STEMMING: "撑开",
    MovementType.KNEE_BAR: "膝盖锁",
    MovementType.SIDE_BODY: "侧身",
    MovementType.STATIC: "静态移动",
    MovementType.REST: "休息",
}


@dataclass
class MovementEvent:
    type: str
    start_frame: int
    end_frame: int
    confidence: float
    label_cn: str
