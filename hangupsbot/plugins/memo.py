import plugins
import asyncio
import datetime


def _initialize():
    plugins.register_handler(_check_if_memo, type="message")
    plugins.register_user_command(["memo"])


def get_id(bot, name):
    all_users = {}
    path = bot.memory.get_by_path(["user_data"])
    for person in path:
        all_users[person] = bot.get_hangups_user(person)
    for user in all_users:
        userdata = all_users[user]
        if name in userdata.full_name.lower():
            return user


def create_memory(bot, name):
    user_id = get_id(bot, name)
    check = bot.user_memory_get(user_id, "memos")
    if not check:
        bot.user_memory_set(user_id, "memos", [])
        return True
    else:
        return False


def add_memo(bot, event, name, text):
    create_memory(bot, name)
    id_ = get_id(bot, name)
    if not id_:
        return "No user by that name"
    else:
        mem = bot.user_memory_get(id_, "memos")
        mem.append('Memo from {}: "{}" at {}'.format(
            event.user.first_name, text, str(datetime.datetime.now())))
        bot.user_memory_set(id_, "memos", mem)
        return "Memo added"


def memo(bot, event, *args):
    id_ = add_memo(bot, event, args[0], ' '.join(args[1:]))
    if id_:
        yield from bot.coro_send_message(event.conv, _(id_))
    else:
        yield from bot.coro_send_message(event.conv, _("No user by that name"))


@asyncio.coroutine
def _check_if_memo(bot, event, command):
    id_ = event.user.id_.chat_id
    memos = bot.user_memory_get(id_, "memos")
    if memos:
        msg = _('<b>{}:</b>\n{}').format(event.user.first_name, '\n'.join(memos))
        bot.user_memory_set(id_, "memos", [])
        yield from bot.coro_send_message(event.conv, msg)
