import asyncio
import json

from bot import user_steps, get
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    from_id = message['from']['id']
    if from_id in user_steps:
        if "Next" in message['text'] and step != user_steps[from_id]['count'] - 1:
            user_steps[from_id]['step'] += 1
            step += 1
        elif "Previous" in message['text'] and step != 0:
            user_steps[from_id]['step'] -= 1
            step -= 1
        else:
            del user_steps[from_id]
            return [Message(chat_id).set_text("<b>Wrong Input !</b>\n\n<i>Try Again</i>", parse_mode="html")]
    if step == 0:
        if from_id not in user_steps:
            page_content = yield from get("http://api.urbandictionary.com/v0/define?term=" + matches)
            json_data = json.loads(page_content)
            if not json_data['list']:
                return [Message(chat_id).set_text("<b>Result Not Found !</b>", parse_mode="html")]
            user_steps[from_id] = {"name": "UrbanDictionary", "step": 0}
            user_steps[from_id]['back'] = matches
            user_steps[from_id]['json'] = json_data
            user_steps[from_id]['count'] = len(json_data['list'])
        else:
            json_data = user_steps[from_id]['json']
        result = "<b>Word : </b>\n" \
                 "<i>{}</i>\n\n" \
                 "<b>Definition</b>\n" \
                 "<i>{}</i>\n\n" \
                 "<b>Example</b>\n" \
                 "<i>{}</i>\n\n" \
                 "👍 {} 👎 {}".format(json_data['list'][step]['word'], json_data['list'][step]['definition'],
                                      json_data['list'][step]['example'], json_data['list'][step]['thumbs_up'],
                                      json_data['list'][step]['thumbs_down'])
        if user_steps[from_id]['count'] == 1:
            show_keyboard = {'hide_keyboard': True}
            del user_steps[from_id]
        else:
            show_keyboard = {'keyboard': [['Next ➡️'], ["🚫 Cancel"]], 'selective': True}
        return [Message(chat_id).set_text(result, parse_mode="html", reply_to_message_id=message['message_id'],
                                          reply_markup=show_keyboard)]
    elif step > 0:
        json_data = user_steps[from_id]['json']
        result = "<b>Word : </b>\n" \
                 "<i>{}</i>\n\n" \
                 "<b>Definition</b>\n" \
                 "<i>{}</i>\n\n" \
                 "<b>Example</b>\n" \
                 "<i>{}</i>\n\n" \
                 "👍 {} 👎 {}".format(json_data['list'][step]['word'], json_data['list'][step]['definition'],
                                      json_data['list'][step]['example'], json_data['list'][step]['thumbs_up'],
                                      json_data['list'][step]['thumbs_down'])

        if step == user_steps[from_id]['count'] - 1:
            show_keyboard = {'keyboard': [['⬅️ Previous'], ["🚫 Cancel"]], 'selective': True}
        else:
            show_keyboard = {'keyboard': [['⬅️ Previous', 'Next ➡️'], ["🚫 Cancel"]], 'selective': True}
        return [Message(chat_id).set_text(result, parse_mode="html", reply_to_message_id=message['message_id'],
                                          reply_markup=show_keyboard)]


plugin = {
    "name": "UrbanDictionary",
    "desc": "Find A Word in Urban Dictionary.\n\n"
            "*For Example :*\n`/ud car`",
    "usage": ["/ud \\[`Word`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^[/!#]ud (.*)"]
}
