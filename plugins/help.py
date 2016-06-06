import asyncio

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from bot import public_plugins
from message import Message


def show_help(num):
    res = []
    t = []
    counter = 10 * num
    for plugin in public_plugins[counter:]:
        if not plugin['sudo'] and 'usage' in plugin:
            t.append(
                InlineKeyboardButton(text=plugin['name'], callback_data='/help ' + plugin['name'] + '--' + str(num)))
            counter += 1
            if len(t) == 2:
                res.append(t)
                t = []
            if counter % 10 == 0:
                break
    return res


def show_shelp(name):
    for plugin in public_plugins:
        if str(plugin['name']).lower() == name.lower():
            return "\n".join(plugin['usage']) + "\n\n" + plugin['desc']
    return "There is no *Plugin* with this name!"


@asyncio.coroutine
def run(message, matches, chat_id, step):
    response = Message(chat_id)
    res = show_help(0)
    if public_plugins:
        res.append([InlineKeyboardButton(text='Next ▶️', callback_data='/helpn 1')])
    markup = InlineKeyboardMarkup(inline_keyboard=res)
    response.set_text("Welcome to Siarobo\nSelect One of these Items.", parse_mode="Markdown", reply_markup=markup)
    return [response]


@asyncio.coroutine
def callback(message, matches, chat_id):
    query_id, from_id, data = telepot.glance(message, flavor='callback_query')
    if data == "/help":
        res = show_help(0)
        if len(public_plugins) > 10:
            res.append([InlineKeyboardButton(text='Next ▶️', callback_data='/helpn 1')])
        markup = InlineKeyboardMarkup(inline_keyboard=res)
        msgid = (chat_id, message['message']['message_id'])
        return Message(from_id).edit_message(msgid, "Welcome to Siarobo\nSelect One of these Items.",
                                             parse_mode="Markdown",
                                             reply_markup=markup)
    elif "/helpn" in data:
        num = int(matches)
        res = show_help(num)
        if len(public_plugins) > (num + 1) * 10 and num != 0:
            res.append([InlineKeyboardButton(text='◀️ Previous', callback_data='/helpn ' + str(num - 1)),
                        InlineKeyboardButton(text='Next ▶️', callback_data='/helpn ' + str(num + 1))])
        elif len(public_plugins) > (num + 1) * 10:
            res.append([InlineKeyboardButton(text='Next ▶️', callback_data='/helpn ' + str(num + 1))])
        elif num != 0:
            res.append([InlineKeyboardButton(text='◀️ Previous', callback_data='/helpn ' + str(num - 1))])
        markup = InlineKeyboardMarkup(inline_keyboard=res)
        msgid = (chat_id, message['message']['message_id'])
        return Message(from_id).edit_message(msgid, "Welcome to Siarobo\nSelect One of these Items.",
                                             parse_mode="Markdown",
                                             reply_markup=markup)
    elif matches:
        tokenize = matches.split("--")
        matches = tokenize[0]
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Return', callback_data='/helpn ' + tokenize[1])]])
        msgid = (chat_id, message['message']['message_id'])
        return Message(from_id).edit_message(msgid, show_shelp(matches), parse_mode="Markdown", reply_markup=markup)


plugin = {
    "name": "Help",
    "desc": "Show This Message1!",
    "usage": ["/help", "/help \\[`plugin_name`]"],
    "run": run,
    "sudo": False,
    "callback": callback,
    "callback_patterns": ["^[!/#]help (.+?)$", "^[!/#]help$", "^[!/#]helpn (\d*)$"],
    "patterns": ["^[!/#]help", "^[!/#]start"]
}
