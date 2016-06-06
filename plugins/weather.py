import asyncio
import json

from bot import get
from message import Message

icons = {'01d': '🌞',
         '01n': '🌚',
         '02d': '⛅️',
         '02n': '⛅️',
         '03d': '☁️',
         '03n': '☁️',
         '04d': '☁️',
         '04n': '☁️',
         '09d': '🌧',
         '09n': '🌧',
         '10d': '🌦',
         '10n': '🌦',
         '11d': '🌩',
         '11n': '🌩',
         '13d': '🌨',
         '13n': '🌨',
         '50d': '🌫',
         '50n': '🌫',
         }

@asyncio.coroutine
async def run(message, matches, chat_id, step):
    payload = {
            'q': matches,
            'units': "metric",
            'appid': ''#Your Open Weather Api Code
            }
    req = await get("http://api.openweathermap.org/data/2.5/weather", params=payload)
    try:
        data = json.loads(req)
        cityName = "{}, {}".format(data["name"], data["sys"]["country"])
        tempInC = round(data["main"]["temp"], 2)
        tempInF = round((1.8 * tempInC) + 32, 2)
        icon = data["weather"][0]["icon"]
        desc = data["weather"][0]["description"]
        res = "<b>{}</b>\n<pre>🌡{}C ({}F)</pre>\n<pre>{} {}</pre>".format(cityName, tempInC, tempInF, icons[icon], desc)
        return [Message(chat_id).set_text(res, parse_mode="html")]
    except:
        return [Message(chat_id).set_text("*Not Found!*", parse_mode="Markdown")]

plugin = {
    "name": "Weather",
    "desc": "Show The Weather of a city\n\n"
            "*For Example :*\n`/weather London`",
    "usage": ["/weather \\[`City`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^/weather (.+?)$"]
}
