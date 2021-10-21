from enum import Enum
from common.countdown_bot import CountdownBot
from typing import List, Dict, Set, Union, Callable
from threading import Lock
import random

class 状态(Enum):
    等待 = 1
    二七王发牌 = 996
    二七王叫庄 = 2
    二七王选花色 = 3
    二七王出牌 = 4

class 模式(Enum):
    二七王 = 1

模式名 = {
    '二七王': 模式.二七王
}

class Card:
    def __init__(self, 花, 点):
        self.花 = 花
        self.点 = 点
        点数 = [
            'i-01',
            'H-02',
            '8-03',
            'V-04',
            'u-05',
            'e-06',
            'a-07',
            'd/E-08',
            'T/o-09',
            'Y/z-10',
            '3/L-11',
            '2/6-12',
            'l/A-13',
            'r/y-14',
            't/N-15',
            'g/w-16',
            'f/j-17',
            'b/D-18',
            'F/x-19',
            's/h-20',
            'm/n-21',
            'k/q-22',
            'c/p-23',
            '4/7-24',
            '5/v-25',
            '1/B-26',
            '任意百搭',
            '部首百搭',
            '韵母百搭',
            '声母百搭'
        ]
        花色 = [ '', '红', '黑', '蓝', '绿' ]
        self.名 = '%s%s' % (花色[self.花], 点数[self.点])
    def __cmp__(self, 他):
        比花 = cmp(self.花, 他.花)
        return 比花 if 比花 != 0 else cmp(self.点, 他.点)

@dataclass
class Player:
    def __init__(self, 名: str, 号: int):
        self.名 = 名
        self.号 = 号
        self.牌: List[Card] = None
        self.庄家: bool = None

class Game:
    def __init__(self, 仆, 名):
        self.仆 = 仆
        self.名 = 名
        self.态 = 状态.等待 
        self.下模式: 模式 = None 
        self.现状: 状态 = 状态.等待
        self.现玩家: List[Player] = None 
        self.回合主 = 0
        self.下玩家: Set[Player] = set()
        self.牌堆: List[Card] = None
        self.叫分 = 0
        self.不叫人数 = 0
        self.号到玩家: Dict[int, int] = None 

    def 发(self, 消息, 人):
        self.仆.client.send_private_msg(message = 消息, user_id = 人)  

    def 发玩家(self, 消息, 人):
        self.发(消息, 现玩家[人].号)

    def 四人广播(self, 消息, 人):
        名 = 现玩家[人].名
        关系 = [
                [ '本家', '下家', '对家', '上家' ],
                [ '上家', '本家', '下家', '对家' ],
                [ '对家', '上家', '本家', '下家' ],
                [ '下家', '对家', '上家', '本家' ]
        ]
        for i in range(4):
            if i == 人:
                continue
            self.发玩家(
                    消息.format(player = ('%s（%s）' % (名, 关系[i][人])), i)

    def 改模式(self, 新模式, 人):
        if 新模式 not in 模式名:
            return
        self.下模式 = 模式名[新模式]
        self.发('下局模式为「%s」。' % 新模式, 人)

    def 加入(self, 人名, 人):
        if 人 in 下玩家:
            self.发('您已加入下局。', 人)
        elif len(self.下玩家) == 4:
            self.发('抱歉，人数已满。', 人)
        else:
            self.下玩家.add(Player(名 = 人名, 号 = 人))
            self.发('你将进入下局。', 人)

    def 退出(self, 人):
        self.下玩家.discard(人)
        self.发('你将离开下局。', 人)

    def 开始(self, 人):
        if self.现状 != 状态.等待:
            self.发('游戏已在进行！', 人)
            return
        if self.下模式 == 模式.二七王:
            self.现状 = 状态.二七王发牌
            self.回合主 = 0
            self.叫分 = 185
            self.不叫人数 = 0
            self.现玩家 = list(self.下玩家)
            self.牌堆 = [ Card(0, 26), Card(0, 27), Card(0, 28), Card(0, 29) ]
            for i in range(1, 5):
                for j in range(26):
                    self.牌堆.append(Card(i, j))
            import random
            random.seed()
            random.shuffle(self.牌堆)
            self.号到玩家 = dict(zip(
                    map(lambda x: x.号, self.现玩家), range(4)))
            for i in self.现玩家:
                i.庄家 = True
                i.牌 = sorted(self.牌堆[:25])
                self.牌堆 = list(self.牌堆[25:])
                self.发('您的牌为：\n' +
                    '\n'.join(map(lambda x: '%s %s' % x,
                            zip(星宿, map(Card.名, i.牌)))), i.号)
            self.现状 = 状态.二七王叫庄
            self.发玩家('请输入数字叫庄，不叫输 0：', 0)
            self.四人广播('{player}正在叫庄。', 0)

    def 查询(self, 人):
        if self.现状 == 状态.等待:
            说玩家 = '\n'.join(map(lambda x: x.名, 下玩家))
            self.发('您在「%s」房间，玩家为：\n%s' % (self.名, 说玩家), 人)

    def 动作(self, 牌, 人):
        if 人 not in self.号到玩家:
            self.发('您不在游戏中！', 人)
            return
        玩家号 = 号到玩家[人]
        if 玩家号 != self.回合主:
            self.发('不在您的回合！', 人)
            return
        if self.现状 == 状态.二七王叫庄:
            if not 牌.isdigit():
                self.发('「%s」不是整数。' % 牌, 人)
                return
            现分 = int(牌)
            if 现分 == 0:
                self.四人广播('{player}不叫。' % 牌, 玩家号)
                self.不叫人数 += 1
            elif 现分 >= self.叫分 or 现分 % 5 != 0:
                self.发('叫分须小于 %d 且为 5 氐倍数。' % self.叫分, 人)
                return
            else:
                self.四人广播('{player}叫分为 %s。' % 牌, 玩家号)
            if 现分 != 0:
                self.叫分 = 现分
            if 现分 == 5:
                self.不叫人数 = 3
                for i in 现玩家:
                    i.庄家 = False
                self.现玩家[玩家号].庄家 = True
            else:
                现玩家[人].庄家 = False
                while not 现玩家[self.回合主].庄家:
                    self.回合主 += 1
                    if self.回合主 == 4:
                        self.回合主 = 0
                if 现分 != 0:
                    self.现玩家[人].庄家 = True
            if self.不叫人数 == 3:
                self.发玩家('您成为庄家。', self.回合主)
                self.四人广播('{player}成为庄家。', self.回合主)
                self.现状 = 状态.二七王选花色
                
            

