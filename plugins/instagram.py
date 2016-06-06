import asyncio
import uuid

from bs4 import BeautifulSoup

from bot import downloader, get
from message import Message


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    response = await get(message['text'])
    soup = BeautifulSoup(response, "html.parser")
    image = soup.find("meta", {"property": "og:image"})
    video = soup.find("meta", {"property": "og:video"})
    if video:
        width = soup.find("meta", {"property": "og:video:width"})
        height = soup.find("meta", {"property": "og:video:height"})
        return [Message(chat_id).set_video(await downloader(video['content'], "tmp/{}.mp4".format(uuid.uuid4())),
                                           width=width, height=height)]
    elif image:
        return [Message(chat_id).set_photo(await downloader(image['content'], "tmp/{}.jpg".format(uuid.uuid4())))]
    else:
        return [Message(chat_id).set_text("<b>Wrong Link !</b>:\n", parse_mode="html")]


plugin = {
    "name": "Instagram",
    "desc": "_Just Send_ *Instagram* _Share Link and get the Photo or Video immediately._",
    "usage": ["Instagram Downloader"],
    "run": run,
    "sudo": False,
    "patterns": ["^(https?://(instagr\.am/p/.*|instagram\.com/p/.*|www\.instagram\.com/p/.*))$"]
}
