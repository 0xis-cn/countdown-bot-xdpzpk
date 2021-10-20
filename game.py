from enum import Enum
from common.countdown_bot import CountdownBot
from typing import List, Dict, Set, Union, Callable
from threading import Lock
import random


class 状态(Enum):
    等待 = 1
    二七王叫庄 = 2
    二七王出牌 = 3

class 模式(Enum):
    二七王 = 1

模式名 = {
    '二七王': 模式.二七王
}

牌名 = [
    '任意百搭',
    '部首百搭',
    '韵母百搭',
    '声母百搭',
]

class Game:
    def __init__(self, 仆, 名):
        self.仆 = 仆
        self.名 = 名
        self.态 = 状态.等待 
        self.现模式: 模式 = None 
        self.下模式: 模式 = None 
        self.现玩家: List[int] = set()
        self.下玩家: Set[int] = set()

    def 发(消息, 人):
        self.仆.client.send_private_msg(message = 消息, user_id = 人)  


    def 改模式(self, 新模式, 人):
        if 新模式 not in 模式名:
            return
        self.下模式 = 模式名[新模式]
        self.发送('下局模式为%s。' % 新模式, 人)

    def 加入(self, 人):
        if 人 in 下玩家:
            self.发送('您已加入下局。', 人)
        elif len(self.下玩家) == 4:
            self.发送('抱歉，人数已满。', 人)
        else:
            self.下玩家.add(人)
            self.发送('你将进入下局。', 人)

    def 退出(self, 人):
        self.下玩家.discard(人)
        self.发送('你将离开下局。', 人)



