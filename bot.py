import os
from os.path import dirname, realpath, join
import random
from queue import Queue

import aiohttp
import demjson
import re
import asyncio

import io
import telepot
import telepot.async
from message import Message


WD = dirname(realpath(__file__))
plugins = []
public_plugins = []
config = {}
user_steps = {}
sender_queue = Queue()

def get_config():
    global config
    file = open(join(WD, "config.json"), "r")
    config = demjson.decode(file.read())
    file.close()


def save_config():
    file = open(join(WD, "config.json"), "w")
    file.write(demjson.encode(config))
    file.close()


def load_plugins():
    global plugins
    global public_plugins
    get_config()
    plugins = []
    public_plugins = []
    for pluginName in config['plugins']:
        plugin_dir = join(WD, "plugins", pluginName + ".py")
        values = {}
        with open(plugin_dir) as f:
            code = compile(f.read(), plugin_dir, 'exec')
            exec(code, values)
            f.close()
        plugin = values['plugin']
        if not plugin['sudo'] and 'usage' in plugin:
            public_plugins.append(plugin)
        plugins.append(plugin)
        print("Loading plugin: {}".format(plugin['name']))

    def sort_key(p):
        return p["name"]

    plugins.sort(key=sort_key)
    public_plugins.sort(key=sort_key)


def check_sudo(chat_id):
    if chat_id in config['sudo_members']:
        return True
    return False


def add_plugin(plugin_name):
    config['plugins'].append(plugin_name)
    save_config()
    load_plugins()


def markdown_escape(text):
    text = text.replace("_", "\\_")
    text = text.replace("[", "\\{")
    text = text.replace("*", "\\*")
    text = text.replace("`", "\\`")
    return text


@asyncio.coroutine
def handle_messages(message):
    content_type, chat_type, chat_id = telepot.glance(message)
    from_id = message['from']['id']
    if 'text' in message:
        if "cancel" in message['text'].lower():
            if from_id in user_steps:
                del user_steps[from_id]
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                yield from sender(Message(chat_id).set_text("You Canceled the operation.", reply_to_message_id=message['message_id'], reply_markup=hide_keyboard))
                return
    if from_id in user_steps:
        for plugin in plugins:
            if plugin['name'] == user_steps[from_id]['name'] :
                    if plugin['sudo']:
                        if check_sudo(from_id):
                            return_values = yield from plugin['run'](message, [""], chat_id, user_steps[from_id]['step'])
                            for return_value in return_values:
                                if return_value:
                                    yield from sender(return_value)
                        else:
                            yield from sender(Message(chat_id).set_text("Just Sudo Users Can Use This."))
                    else:
                        return_values = yield from plugin['run'](message, [""], chat_id, user_steps[from_id]['step'])
                        if return_values:
                            for return_value in return_values:
                                yield from sender(return_value)
                    break
        return
    if 'text' in message:
        for plugin in plugins:
            for pattern in plugin['patterns']:
                if re.search(pattern, message['text'], re.IGNORECASE|re.MULTILINE):
                    matches = re.findall(pattern, message['text'], re.IGNORECASE)
                    if plugin['sudo']:
                        if check_sudo(message['from']['id']):
                            return_values = yield from plugin['run'](message, matches[0], chat_id, 0)
                            for return_value in return_values:
                                if return_value:
                                    yield from sender(return_value)
                        else:
                            yield from sender(Message(chat_id).set_text("Just Sudo Users Can Use This."))
                    else:
                        return_values = yield from plugin['run'](message, matches[0], chat_id, 0)
                        if return_values:
                            for return_value in return_values:
                                yield from sender(return_value)
                    break

@asyncio.coroutine
def on_callback_query(message):
    query_id, from_id, data = telepot.glance(message, flavor='callback_query')
    for plugin in plugins:
            if 'callback' in plugin:
                for pattern in plugin['callback_patterns']:
                    if re.search(pattern, data, re.IGNORECASE|re.MULTILINE):
                        matches = re.findall(pattern, data, re.IGNORECASE)
                        return_value = yield from plugin['callback'](message, matches[0], message['message']['chat']['id'])
                        if return_value:
                            yield from sender(return_value)
                        break


@asyncio.coroutine
def on_inline_query(message):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    global plugins

    @asyncio.coroutine
    def get_inline():
        for plugin in plugins:
            if 'inline_query' in plugin:
                for pattern in plugin['inline_patterns']:
                    if re.search(pattern, query, re.IGNORECASE|re.MULTILINE):
                        matches = re.findall(pattern, query, re.IGNORECASE)
                        return_values = yield from plugin['inline_query'](message, matches[0], from_id, 0)
                        if return_values:
                            return {'results': return_values, 'cache_time': 0}
                        break
        return []
    try:
        answerer.answer(message, get_inline)

    except:
        pass


@asyncio.coroutine
def on_chosen_inline_result(message):
    result_id, from_id, query_string = telepot.glance(message, flavor='chosen_inline_result')
    for plugin in plugins:
            if 'chosen_inline' in plugin:
                for pattern in plugin['chosen_inline_pattern']:
                    if re.search(pattern, query_string, re.IGNORECASE | re.MULTILINE):
                        matches = re.findall(pattern, query_string, re.IGNORECASE)
                        return_values = yield from plugin['chosen_inline'](message, matches[0], from_id, result_id)
                        if return_values:
                            return return_values
                        break


@asyncio.coroutine
def forward_id(chat_id_forward, chat_id, msg_id):
    yield from bot.forwardMessage(chat_id_forward, chat_id, msg_id)


@asyncio.coroutine
def sender(message):
    try:
        if message.content_type == "text":
            r = yield from bot.sendMessage(message.chat_id,message.text, parse_mode=message.parse_mode, disable_web_page_preview=message.disable_web_page_preview, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
        elif message.content_type == "video":
            yield from bot.sendChatAction(message.chat_id, 'upload_video')
            if os.path.isfile(message.video):
                r = yield from bot.sendVideo(message.chat_id, open(message.video, 'rb'), duration=message.duration, width=message.width, height=message.height, caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
                os.remove(message.video)
            else:
                r = yield from bot.sendVideo(message.chat_id, message.video, duration=message.duration, width=message.width, height=message.height, caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
        elif message.content_type == "document":
            yield from bot.sendChatAction(message.chat_id, 'upload_document')
            if os.path.isfile(message.file):
                r = yield from bot.sendDocument(message.chat_id, open(message.file, 'rb'), caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
                os.remove(message.file)
            else:
                r = yield from bot.sendDocument(message.chat_id, message.file, caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
        elif message.content_type == "photo":
            yield from bot.sendChatAction(message.chat_id, 'upload_photo')
            if os.path.isfile(message.photo):
                r = yield from bot.sendPhoto(message.chat_id, open(message.photo, 'rb'), caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
                os.remove(message.photo)
            else:
                r = yield from bot.sendPhoto(message.chat_id, message.photo, caption=message.caption, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
        elif message.content_type == "audio":
            yield from bot.sendChatAction(message.chat_id, 'upload_audio')
            if os.path.isfile(message.audio):
                r = yield from bot.sendAudio(message.chat_id, open(message.audio, 'rb'), duration=message.duration, performer=message.performer, title=message.title, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
                os.remove(message.audio)
            else:
                r = yield from bot.sendAudio(message.chat_id, message.audio, duration=message.duration, performer=message.performer, title=message.title, disable_notification=message.disable_notification, reply_to_message_id=message.reply_to_message_id, reply_markup=message.reply_markup)
        elif message.content_type == "callback_query":
            r = yield from bot.answerCallbackQuery(message.callback_query_id, text=message.text, show_alert=message.show_alert)
        elif message.content_type == "edit_message":
            r = yield from bot.editMessageText(message.msg_identifier, message.text, parse_mode=message.parse_mode, disable_web_page_preview=message.disable_web_page_preview, reply_markup=message.reply_markup)
        return r
    except:
        pass


@asyncio.coroutine
def download(file_id, path):
    yield from bot.download_file(file_id, path)
    return path


async def downloader(url, path, params=None):
        try:
            d = path if isinstance(path, io.IOBase) else open(path, 'wb')
            with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as r:
                    while 1:
                        chunk = await r.content.read()
                        if not chunk:
                            break
                        d.write(chunk)
                        d.flush()
                        return path
        finally:
            if not isinstance(path, io.IOBase) and 'd' in locals():
                d.close()


async def get_stream(url, params=None):
    connector = aiohttp.TCPConnector(verify_ssl=False)
    with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, params=params) as resp:
            return await resp


async def get(url, params=None, headers=None):
    connector = aiohttp.TCPConnector(verify_ssl=False)
    with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, params=params, headers=headers) as resp:
            return await resp.text()


async def check_queue():
    while 1:
        while not sender_queue.empty():
            await sender(sender_queue.get())
        await asyncio.sleep(0.1)


load_plugins()
bot = telepot.async.Bot(config['token'])
answerer = telepot.async.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': handle_messages,
                                   'callback_query': on_callback_query,
                                   'inline_query': on_inline_query,
                                   'chosen_inline_result': on_chosen_inline_result,
                                   'edited_chat': handle_messages}))
loop.create_task(check_queue())
print('Bot Started ...')

loop.run_forever()
