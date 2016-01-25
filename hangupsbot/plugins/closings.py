import plugins
import json
from requests import get
from control import *
from bs4 import BeautifulSoup

def _initialise():
    plugins.register_user_command(['fcps', 'lcps'])

@asyncio.coroutine
def checklcps():
    r = get('http://www.nbcwashington.com/weather/school-closings/')
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    schools = []
    for school in soup.find_all('p'):
        schools.append(school.text)

    for i in range(len(schools)):
        if 'Loudoun County' in schools[i]:
            return (schools[i])
            yield from asyncio.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, checklcps())
    yield from bot.coro_send_message(event.conv, _(str(checklcps())))
    loop.run_until_complete(checklcps())

main()

def lcps(bot, event, *args):
    try:
        check = checklcps()
        status = check.replace('Loudoun County Schools', '')
        msg = _('LCPS is {}').format(status)
        yield from bot.coro_send_message(event.conv, msg)
    except BaseException as e:
        simple = _('An Error Occurred')
        msg = _('{} -- {}').format(str(e), event.text)
        yield from bot.coro_send_message(event.conv, simple)
        yield from bot.coro_send_message(CONTROL, msg)

def fcps(bot, event, *args):
    try:
        page = get('https://ion.tjhsst.edu/api/emerg?format=json')
        data = json.loads(page.text)
        status = data['status']
        if status:
            message = data['message']
            message = message.replace('<p>', '')
            message = message.replace('</p>', '')
            msg = _(message)
        else:
            msg = _('FCPS is open')
        yield from bot.coro_send_message(event.conv, msg)
    except BaseException as e:
        simple = _('An Error Occurred')
        msg = _('{} -- {}').format(str(e), event.text)
        yield from bot.coro_send_message(event.conv, simple)
        yield from bot.coro_send_message(CONTROL, msg)
