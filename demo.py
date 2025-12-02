from wxauto import WeChat
from wxauto.msgs import FriendMessage, SelfMessage, SystemMessage
from wxauto import get_wx_clients
from wxauto import get_wx_logins
from wxauto import LoginWnd
from chatgpt import get_reply

def print_now_windows():
    msgs = wx.GetAllMessage()
    for msg in msgs:
        print('==' * 30)
        print(f"{msg.sender}: {msg.content}")

def send(message, name="戒不了色吧", members=None):
    wx.SendMsg(message, who=name, at=members)
    print(f"Send Success to {name}:\n\t{message}")

def print_sessions():
    # {'name': '戒不了色吧', 'time': '19:34', 'content': 'test', 'isnew': False, 'new_count': 0, 'ismute': False}
    sessions = wx.GetSession()
    for session in sessions:
        print(session.info)

def handle_message(message):
    message = message.replace("@fzxbot", "")
    message = message.replace("@fzx", "")
    return message

def check_message(msg, chat):
    if msg.attr != "friend":
        return False
    if msg.type != "text" and msg.type != "quote":
        return False
    # 群聊里需要 @fzx
    # return True
    if chat.chat_type == "group" and not "@fzx" in msg.content:
        return False
    return True

def auto_reply(msg, chat):
    if check_message(msg, chat):
        # members = chat._api.get_group_members()
        # message = "群聊里所有人为："
        # for member in members:
        #     message += member+" "
        # msg.quote(message)
        # return

        content = handle_message(msg.content)
        reply = "[自动回复] " + get_reply(content)
        msg.quote(reply)            # 引用消息
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
    # addListen("fzx")
    addListen("什么档次和我一组")
    # addListen("戒不了色吧")
    wx.KeepRunning()
