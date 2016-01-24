"""
Identify images, upload them to google plus, post in hangouts
"""

import aiohttp, asyncio, io, logging, os, re

import plugins
from control import *
from links import *

logger = logging.getLogger(__name__)


def _initialise():
    plugins.register_handler(_watch_image_link, type="message")


@asyncio.coroutine
def _watch_image_link(bot, event, command):
    try:
        # Don't handle events caused by the bot himself
        if event.user.is_self:
            return

        probable_image_link = False
        event_text_lower = event.text.lower()
        not_image_but_link = False
        if re.match("^(https?://)?([a-z0-9.]*?\.)?imgur.com/", event_text_lower, re.IGNORECASE):
            """imgur links can be supplied with/without protocol and extension"""
            probable_image_link = True

        elif event_text_lower.startswith(("http://", "https://")) and event_text_lower.endswith((".png", ".gif", ".gifv", ".jpg")):
            """other image links must have protocol and end with valid extension"""
            probable_image_link = True

        if probable_image_link and "googleusercontent" in event_text_lower:
            """reject links posted by google to prevent endless attachment loop"""
            logger.debug("rejected link {} with googleusercontent".format(event.text))
            return

        if probable_image_link:
            link_image = event.text

            if "imgur.com" in link_image:
                """special imgur link handling"""
                if not link_image.endswith((".jpg", ".gif", "gifv", "webm", "png")):
                    link_image = link_image + ".gif"
                link_image = "https://i.imgur.com/" + os.path.basename(link_image)

            link_image = link_image.replace(".webm",".gif")
            link_image = link_image.replace(".gifv",".gif")

            logger.info("getting {}".format(link_image))

            filename = os.path.basename(link_image)
            r = yield from aiohttp.request('get', link_image)
            raw = yield from r.read()
            image_data = io.BytesIO(raw)

            image_id = yield from bot._client.upload_image(image_data, filename=filename)

            yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)
        words  = str(event.text).split()
        for i in range(len(words)):
            if 'http' in words[i]:
                parsedurl = str(words[i])
                not_image_but_link = True
                break
            else:
                not_image_but_link = False
        if not_image_but_link and not probable_image_link:
            title = get_title(parsedurl)
            if not title == 'Unable to open url :(':
                link = shorten(parsedurl)
                msg = _("** {} ** -- {}").format(title, link)
            else:
                msg = _("{}").format(title)
            yield from bot.coro_send_message(event.conv, msg)
    except BaseException as e:
        simple = _('An Error Occurred')
        msg = _('{} -- {}').format(str(e), event.text)
        yield from bot.coro_send_message(CONTROL, msg)
        yield from bot.coro_send_message(event.conv, simple)
