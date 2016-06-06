import asyncio

import demjson

from bot import user_steps, sender, get, downloader
from message import Message

client_id = ''#YOUR CLIENT ID


async def search(query):
    global guest_client_id

    search_url = 'https://api.soundcloud.com/search?q=%s&facet=model&limit=30&offset=0&linked_partitioning=1&client_id='+client_id

    url = search_url % query

    response = await get(url)
    r = demjson.decode(response)
    res = []
    for entity in r['collection']:
        if entity['kind'] == 'track':
            res.append([entity['title'], entity['permalink_url']])
    return res


async def getfile(url):
    response = await get(
        "https://api.soundcloud.com/resolve?url={}&client_id="+client_id.format(url))
    r = demjson.decode(response)
    return r['stream_url'] + "?client_id="+client_id


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    from_id = message['from']['id']
    if step == 0:
        await sender(
            Message(chat_id).set_text("*Please Wait*\nI'm Searching all Music with this name", parse_mode="markdown"))
        user_steps[from_id] = {"name": "Soundcloud", "step": 1, "data": {}}
        i = 0
        show_keyboard = {'keyboard': [], "selective": True}
        matches = matches.replace(" ", "+")
        for song in await search(matches):
            title, link = song[0], song[1]
            user_steps[from_id]['data'][title] = link
            show_keyboard['keyboard'].append([title])
            i += 1
            if i == 20:
                break
        if len(show_keyboard['keyboard']) in [0, 1]:
            hide_keyboard = {'hide_keyboard': True, 'selective': True}
            del user_steps[from_id]
            return [Message(chat_id).set_text("*Not Found*",
                                              reply_to_message_id=message['message_id'], reply_markup=hide_keyboard,
                                              parse_mode="markdown")]
        return [Message(chat_id).set_text("Select One Of these :", reply_to_message_id=message['message_id'],
                                          reply_markup=show_keyboard)]
    elif step == 1:
        try:
            hide_keyboard = {'hide_keyboard': True, "selective": True}
            await sender(Message(chat_id).set_text("*Please Wait*\nLet me Save this Music For You",
                                                   reply_to_message_id=message['message_id'],
                                                   reply_markup=hide_keyboard, parse_mode="markdown"))
            await downloader(await getfile(user_steps[from_id]['data'][message['text']]),
                             "tmp/{}.mp3".format(message['text']))
            del user_steps[from_id]
            return [Message(chat_id).set_audio("tmp/{}.mp3".format(message['text']), title=message['text'],
                                               performer="@Siarobot")]
        except Exception as e:
            del user_steps[from_id]
            return [Message(chat_id).set_text("*Wrong Input*\n_Try Again_", parse_mode="markdown")]


plugin = {
    "name": "Soundcloud",
    "desc": "Download a Music From Sound Cloud\n\n"
            "*For Start :*\n`/sc michael jackson billie jean`",
    "usage": ["/sc \\[`Search`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^[/!#]sc (.*)$"]
}
