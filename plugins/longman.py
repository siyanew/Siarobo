import asyncio
import json
import uuid

from bot import user_steps, get, downloader
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
            return [Message(chat_id).set_text("<b>Wrong Input!</b>\n<i>Try Again</i>", parse_mode="html")]
    if step == 0:
        if from_id not in user_steps:
            page_content = yield from get(
                "http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword=" + matches.replace(" ", "+"))
            json_datas = json.loads(page_content)
            json_data = json_datas['results']
            if not json_data:
                return [Message(chat_id).set_text("<b>Result Not Found !</b>", parse_mode="html")]
            user_steps[from_id] = {"name": "Longman Dictionary", "step": 0}
            user_steps[from_id]['back'] = matches
            user_steps[from_id]['json'] = json_data
            user_steps[from_id]['count'] = len(json_data)
        else:
            json_data = user_steps[from_id]['json']
        result = "<b>Word: {} </b> " \
                 "<i>{}</i>\n\n" \
                 "<b>Definition: </b>\n" \
                 "{}\n\n".format(json_data[step]['headword'], json_data[step]['part_of_speech'],
                                 json_data[step]['senses'][0]['definition'][0])
        if json_data[step]['senses'][0].get('examples'):
            result += "<b>Example: </b>\n" \
                      "{}\n\n".format(json_data[step]['senses'][0]['examples'][0]['text'])
        if user_steps[from_id]['count'] == 1:
            show_keyboard = {'hide_keyboard': True}
            del user_steps[from_id]
        else:
            show_keyboard = {'keyboard': [['Next ➡️'], ["🚫 Cancel"]], 'selective': True}
        res = [Message(chat_id).set_text(result, parse_mode="html", reply_to_message_id=message['message_id'],
                                         reply_markup=show_keyboard)]
        if json_data[step].get('pronunciations'):
            for i in json_data[step]['pronunciations']:
                for j in i['audio']:
                    res.append(Message(chat_id).set_audio(
                        yield from downloader("http://api.pearson.com" + j['url'], "tmp/{}.mp3".format(uuid.uuid4())),
                        performer=j['lang'], title=json_data[step]['headword']))
        return res
    elif step > 0:
        json_data = user_steps[from_id]['json']
        result = "<b>Word: {} </b> " \
                 "<i>{}</i>\n\n" \
                 "<b>Definition: </b>\n" \
                 "{}\n\n".format(json_data[step]['headword'], json_data[step]['part_of_speech'],
                                 json_data[step]['senses'][0]['definition'][0])
        if json_data[step]['senses'][0].get('examples'):
            result += "<b>Example: </b>\n" \
                      "{}\n\n".format(json_data[step]['senses'][0]['examples'][0]['text'])
        if step == user_steps[from_id]['count'] - 1:
            show_keyboard = {'keyboard': [['⬅️ Previous'], ["🚫 Cancel"]], 'selective': True}
        else:
            show_keyboard = {'keyboard': [['⬅️ Previous', 'Next ➡️'], ["🚫 Cancel"]], 'selective': True}
        res = [Message(chat_id).set_text(result, parse_mode="html", reply_to_message_id=message['message_id'],
                                         reply_markup=show_keyboard)]
        if json_data[step].get('pronunciations'):
            for i in json_data[step]['pronunciations']:
                for j in i['audio']:
                    res.append(Message(chat_id).set_audio(
                        yield from downloader("http://api.pearson.com" + j['url'], "tmp/{}.mp3".format(uuid.uuid4())),
                        performer=j['lang'], title=json_data[step]['headword']))
        return res


plugin = {
    "name": "Longman Dictionary",
    "desc": "Find A Word in Longman Dictionary.\n\n"
            "*For Example :*\n`/lm car`",
    "usage": ["/lm \\[`Word`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^[/!#]lm (.*)",
                 "^[/!#]def (.*)"]
}
