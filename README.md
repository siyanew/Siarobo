# Siarobo
Siarobo is a telegram bot based on [Telepot](https://github.com/nickoala/telepot) - http://telegram.me/siarobot

## How to Run ?
First of all install Python >= 3.5 and then install `pip3`.
```
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python3.5
sudo apt-get install python3-pip
```
Run These commands for Resolving the dependencies.

```
pip3 install telepot
pip3 install aiohttp
pip3 install beautifulsoup4
pip3 install youtube-dl
pip3 install pafy
pip3 install demjson
```

Add the bot Token and your id in config.json as a sudo member.

make a screen!
```
screen -S siarobo
python3 bot.py
```
Ctrl + A + D !

## How to Stop ?
```
screen -r siarobot
```
Ctrl + C !
## Work With Plugins
```
/plugins --> Show all of the plugins
/plugins enable {name} --> Enabaling {name} plugin | Change {name} with a plugin file name!
/plugins disable {name} --> Disabaling {name} plugin | Change {name} with a plugin file name!
```
# Developers Guide to make a plugin
Add a file in plugins folder and this is the base :
```
import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    return []


@asyncio.coroutine
def inline(message, matches, chat_id, step):
    return []


plugin = {
    "name": "",
    "desc": "",
    "usage": [""],
    "inline_patterns": ["^$"],
    "inline_query": inline,
    "run": run,
    "sudo": False,
    "patterns": ["^$"]
}

```
For using Amazing Step Handler You must Create Something Like that.
Name and step are Required.
```
user_steps[from_id] = {"name": "Youtube", "step": 0, "data": []}
```
so in run function handle the steps, and delete it at the end:
```
del user_steps[from_id]
```
### Returning a Result
For returning a result use Message Class in message.py
You can return as many as response that you wants in a plugin just append them in to a list and return them.
```
results = []
results.append(Message(chat_id).set_text("Text")) # Send an text
results.append(Message(chat_id).set_audio("File Path or File_id", performer="", title="")) # Send an audio
results.append(Message(chat_id).set_video("File Path or File_id")) # Send an video
results.append(Message(chat_id).set_document("File Path or File_id")) # Send an document
results.append(Message(chat_id).set_photo("File Path or File_id")) # Send an photo
```
You can pass some other arguments in Message, so its good to look at message.py file.
# Known Issue
* My English is not good, so maybe there are some Gramatically and Dictation mistakes. Feel free to fork and correct the mistakes.😅
* Step handler must combine chat_id and from_id but it doesn't.It will be ok as soon as possible, so if user step handler opened in a group it will be finalize in the private or another groups that bot added to them!

#Thanks to
[Nickoala](https://github.com/nickoala/) For his amazing Framework

[Imandaneshi](https://github.com/imandaneshi)

[Flöö](https://github.com/arandomstranger)

@af_zoun


### Please
please feel free to ask any questions here by issues or on telegram via [@Siyanew](https://telegram.me/siyanew/)
