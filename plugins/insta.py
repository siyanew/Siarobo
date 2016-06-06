import asyncio
import uuid

from bs4 import BeautifulSoup

from bot import check_sudo, get, downloader
from message import Message


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    try:
        response = await get("https://www.instagram.com/" + matches)
        soup = BeautifulSoup(response, "html.parser")
        image = soup.find("meta", {"property": "og:image"})
        proimage = image['content'].replace("s320x320/", "")
        proimage = proimage.replace("s150x150/", "")
        proimage = proimage.replace("s64x64/", "")
        if image:
            return [Message(chat_id).set_photo(await downloader(proimage, "tmp/{}.jpg".format(uuid.uuid4())))]
        else:
            return [Message(chat_id).set_text("<b>Wrong Link !</b>", parse_mode="html")]
    except:
        return [Message(chat_id).set_text("<b>Invalid username !</b>", parse_mode="html")]


plugin = {
    "name": "Instagram",
    "desc": "_Just Send_ *Instagram Username* _after /insta command_\n"
            "like `/insta siarobot` or `/insta @siarobot`",
    "usage": ["/insta \\[`Username`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^[/!#]insta @?(.*)"]
}
