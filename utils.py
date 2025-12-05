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
