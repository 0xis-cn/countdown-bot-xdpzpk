from common.plugin import Plugin
from common.config_loader import ConfigBase
from common.datatypes import PluginMeta
from common.countdown_bot import CountdownBot
from common.loop import TimeTuple
from common.command import ChatType
from common.event import MessageEvent, PrivateMessageEvent
from typing import Set, Dict, List
from .game import Game
import json
import flask
HELP_STR =\
    """
"""


class XdpzpkConfig(ConfigBase):
    pass

class XdpzpkPlugin(Plugin):
    def on_enable(self):
        self.bot: CountdownBot
        self.config: XdpzpkConfig
        self.人到局: Dict[int, Game] = {}
        self.名到局: Dict[str, Game] = {}
        self.register_command_wrapped(
            command_name = 'xdpzpk',
            command_handler = self.指令_xdpzpk,
            help_string = '进入希顶拼字扑克游戏',
            chats = { ChatType.private },
            alias = []
        )
        self.register_event_listener(PrivateMessageEvent, self.消息处理)


    def 指令_xdpzpk(self, plugin, args: List[str],
            raw_string: str, context, evt: PrivateMessageEvent):
        人 = evt.sender.user_id
        if 人 in self.人到局:
            self.人到局[人].退出(人)
            del self.人到局[人]
        if len(args) == 0:
            self.bot.client.send(context,
                    '如何忽告别，决去如惊凫。' +
                    '您已退出希顶拼字扑克！')
            return
        if len(args) > 1:
            self.bot.client.send(context, '参数过多！')
            return
        名 = args[0]
        人名 = evt.sender.nickname 
        if 名 not in self.名到局:
            self.名到局[名] = Game(self.bot, 名)
        self.人到局[人] = self.名到局[名]
        self.名到局[名].加入(人名, 人)
        self.bot.client.send(context,
                    '花径不曾缘客扫，蓬门今始为君开。' +
                    '您已加入希顶拼字扑克房间「%s」！' % 名)

    def 内指令模式(self, event: PrivateMessageEvent, game: Game, 模式):
        game.改模式(模式, event.sender.user_id)

    def 内指令开始(self, event: PrivateMessageEvent, game: Game):
        game.开始(event.sender.user_id)

    def 内指令状态(self, event: PrivateMessageEvent, game: Game):
        game.查询(event.sender.user_id)

    def 内指令出(self, event: PrivateMessageEvent, game: Game, 牌):
        game.动作(牌, event.sender.user_id)

    def 消息处理(self, evt: PrivateMessageEvent):
        人 = evt.sender.user_id
        if 人 not in self.人到局:
            self.bot.client.send(event.context, '您尚未进入希顶拼字扑克！')
            return
        指令, *余 = evt.message.split() 
        # 此处部分摘自 GitHub 的 officeyutong/Countdown-Bot
        if not hasattr(self, '内指令' + 指令):
            self.bot.client.send(evt.context, '希顶拼字扑克无此指令。')
            return
        操作 = getattr(self, '内指令' + 指令)
        if 3 + len(余) != len(操作.__code__.co_varnames):
            self.bot.client.send(evt.context, '指令参数数量错误。')
            return
        操作(evt, 人到局[人], *余)

def get_plugin_class():
    return XdpzpkPlugin

def get_config_class():
    return XdpzpkConfig

def get_plugin_meta():
    return PluginMeta(
        '物灵', 0.1, '希顶拼字扑克'
    )

