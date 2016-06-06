import asyncio
import telepot
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    if 'reply_to_message' in message:
        content_type, chat_type, chat_id = telepot.glance(message['reply_to_message'])
        if content_type == "document":
            return [Message(chat_id).set_document(message['reply_to_message']['document']['file_id'], caption=matches)]
        elif content_type == "video":
            return [Message(chat_id).set_video(message['reply_to_message']['video']['file_id'], caption=matches)]
        elif content_type == "photo":
            return [Message(chat_id).set_photo(message['reply_to_message']['photo'][-1]['file_id'], caption=matches)]
        return [Message(chat_id).set_text("Reply Just photos,Videos or gifs!")]
    else:
        return [Message(chat_id).set_text("Reply Something!")]


plugin = {
    "name": "Caption",
    "desc": "You Can Use This Plugin To Set Caption On Photos, Videos, Documents and gifs.\n"
            "*For Example:*\nJust _Reply_ a photo and send `/cap this is the caption`",
    "usage": ["/cap \\[`Caption_Text`] _<reply>_"],
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]cap ([\s\S]*)$"]
}
