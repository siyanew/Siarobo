import asyncio
import uuid

from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle

from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    return [Message(chat_id).set_text(matches, parse_mode="Markdown")]


@asyncio.coroutine
def inline(message, matches, chat_id, step):
    return [InlineQueryResultArticle(
        id=str(uuid.uuid4()), title='Send Custom Markdown Style', description=matches,
        input_message_content=InputTextMessageContent(message_text=matches, parse_mode="Markdown"),
        thumb_url="http://siyanew.com/bots/custom.jpg")]


plugin = {
    "name": "Echo",
    "desc": "This is the simplest plugin in the world\nYou can use this plugin to send messages in Markdown Format.\n"
            "\\* *Bold* \\*\n"
            "\\_ _Italic_ \\_\n"
            "[link](https://telegram.me/siarobot) \\[link](url)\n"
            "\\` `inline Fixed-width code` \\`\n"
            "\\`\\`\\` ```Pre-formatted fixed-width code block``` \\`\\`\\`\n\n"
            "*For Example:*\n/echo \\*How Are You\\* \\_Robot\\_ ?",
    "usage": ["/echo \\[`Markdown_Text`] _{Inline}_"],
    "inline_patterns": ["^[!/#]echo ([\s\S]*)$"],
    "inline_query": inline,
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]echo ([\s\S]*)$"]
}
