from wxauto import WeChat
from wxauto.msgs import FriendMessage, SelfMessage, SystemMessage
from wxauto import get_wx_clients
from wxauto import get_wx_logins
from wxauto import LoginWnd
from chatgpt import get_reply, set_system
from instruction import instruct_hook
from utils import handle_message, check_message


def print_now_windows():
    print("start print")
    msgs = wx.GetAllMessage()
    print("message", msgs)
    for msg in msgs:
        print("==" * 30)
        print(f"{msg.sender}: {msg.content}")


def send(message, name="戒不了色吧", members=None):
    wx.SendMsg(message, who=name, at=members)
    print(f"Send Success to {name}:\n\t{message}")


def print_sessions():
    # {'name': '戒不了色吧', 'time': '19:34', 'content': 'test', 'isnew': False, 'new_count': 0, 'ismute': False}
    sessions = wx.GetSession()
    for session in sessions:
        print(session.info)


def auto_reply(msg, chat):
    if instruct_hook(msg, chat):
        return
    if check_message(msg, chat):
        # members = chat._api.get_group_members()
        # message = "群聊里所有人为："
        # for member in members:
        #     message += member+" "
        # msg.quote(message)
        # return
        set_system("cat_girl")
        content = handle_message(msg.content)
        reply = "[自动回复] " + get_reply(content)
        msg.quote(reply)  # 引用消息
        # chat.SendMsg(reply)


def addListen(name):
    wx.AddListenChat(nickname=name, callback=auto_reply)
    print("已监听会话: {}".format(name))


def login():
    # 不知道为啥只能打开登陆页面，但是登不上去
    path = "D:/BotWeChat3.9.12/WeChat/WeChat.exe"
    loginwnd = LoginWnd(path)
    loginwnd.login()


if __name__ == "__main__":
    wx = WeChat(debug=True)
    # addListen("田亦海")
    # addListen("什么档次和我一组")
    # addListen("戒不了色吧")
    addListen("fzx")
    wx.KeepRunning()
