import asyncio
import uuid
from urllib.parse import urlencode

from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle

from bot import markdown_escape
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    get_params = urlencode({'q': matches})
    return [Message(chat_id).set_text("*Click On The Bottom Link :*\n\n👇👇👇👇👇👇👇👇\n"
                                      "[{}](http://lmgtfy.com/?{})".format(markdown_escape(matches),
                                                                           markdown_escape(get_params)),
                                      disable_web_page_preview=True, parse_mode="Markdown")]


@asyncio.coroutine
def inline(message, matches, chat_id, step):
    get_params = urlencode({'q': matches})
    return [InlineQueryResultArticle(
        id=str(uuid.uuid4()), title="Let Me Google That For You", description=matches,
        input_message_content=InputTextMessageContent(
            message_text="[{}](http://lmgtfy.com/?{})".format(markdown_escape(matches), markdown_escape(get_params)),
            parse_mode="Markdown", disable_web_page_preview=True),
        thumb_url="http://www.ultimobyte.org/wp-content/uploads/2010/08/lmgtfy.png")]


plugin = {
    "name": "LetMeGoogleThatForYou",
    "desc": "You can Make lmgtfy links.\n"
            "*For Example :*\n\n"
            "/lmgtfy how to make a bot?",
    "usage": ["/lmgtfy \\[`Search_Query`]"],
    "inline_patterns": ["^[!/#]lmgtfy (.*)$"],
    "inline_query": inline,
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]lmgtfy (.*)$"]
}
