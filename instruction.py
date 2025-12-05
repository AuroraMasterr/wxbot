from utils import handle_message
from chatgpt import set_system, get_reply


def Summary(msg, chat):
    msg_str = ""
    msgs = chat.GetAllMessage()
    for m in msgs:
        msg_str += f"{m.sender}: {m.content}\n"
    set_system("summary")
    reply = get_reply(msg_str)
    msg.quote(reply)


def Honor_of_kings(msg, chat):
    reply = "王者荣耀，启动！"
    msg.quote(reply)


instruction_dict = {
    "summary": Summary,
    "农": Honor_of_kings,
}


def instruct_hook(msg, chat):
    content = handle_message(msg.content)
    if not content or content[0] != "/":
        return False
    content = content.split(" ")[0].lstrip("/")
    if content in instruction_dict:
        instruction_dict[content](msg, chat)
        return True
    return False
