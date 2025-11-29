from wxauto import WeChat
from wxauto.msgs import FriendMessage
from wxauto import get_wx_clients
from wxauto import get_wx_logins
from wxauto import LoginWnd


def print_now_windows():
    msgs = wx.GetAllMessage()
    for msg in msgs:
        print('==' * 30)
        print(f"{msg.sender}: {msg.content}")

def send(message, name="戒不了色吧"):
    wx.SendMsg(message, who=name)
    print(f"Send Success to {name}:\n\t{message}")

def print_sessions():
    # {'name': '戒不了色吧', 'time': '19:34', 'content': 'test', 'isnew': False, 'new_count': 0, 'ismute': False}
    sessions = wx.GetSession()
    for session in sessions:
        print(session.info)

def auto_reply(msg, chat):
    # send("自动回复", "oh")
    chat.SendMsg("自动回复")

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
    wx = WeChat(debug=True)
    # addListen("fzx")
    addListen("戒不了色吧")
    wx.KeepRunning()


