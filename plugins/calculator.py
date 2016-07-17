import asyncio
import uuid

from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle

from bot import get
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    exp = matches
    payload = {
        'expr': exp
    }
    req = yield from get("http://api.mathjs.org/v1/", params=payload)
    if req:
        return [Message(chat_id).set_text(matches + " = " + req)]
    return [Message(chat_id).set_text("Oops,\nSomething went wrong!")]


@asyncio.coroutine
def inline(message, matches, chat_id, step):
    exp = matches
    payload = {
        'expr': exp
    }
    req = yield from get("http://api.mathjs.org/v1/", params=payload)
    if req:
        return [InlineQueryResultArticle(
            id=str(uuid.uuid4()), title='Calculator', description=matches + " = " + req,
            input_message_content=InputTextMessageContent(message_text=matches + " = " + req),
            thumb_url="http://siyanew.com/bots/calculate.jpg")]
    return [InlineQueryResultArticle(
        id=str(uuid.uuid4()), title='Error occurred!', description="Something Went Wrong!",
        input_message_content=InputTextMessageContent(message_text="*Something Went Wrong!*", parse_mode="Markdown"),
        thumb_url="http://siyanew.com/bots/error.jpg")]


plugin = {
    "name": "Calculator",
    "desc": "With this plugin you can calculate expressions.",
    "usage": ["/cal \\[`Expression`] _{Inline}_"],
    "inline_patterns": ["^[!/#]cal (.*)$"],
    "inline_query": inline,
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]cal (.*)$"]
}
