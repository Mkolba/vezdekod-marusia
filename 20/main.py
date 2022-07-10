import config

from skill import Handler
from aiohttp import web, ClientSession
from utils import Logger
import asyncio


logger = Logger("SERVER")


async def create_app(loop):
    app = web.Application()
    app.session = ClientSession()
    app.event_loop = loop

    app.router.add_route(method='POST', path='/webhook-20', handler=Handler)
    app.router.add_route(method='OPTIONS', path='/webhook-20', handler=Handler)

    # Server set-up
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=config.port, host=config.host)
    return app, site


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app, site = loop.run_until_complete(create_app(loop))
    loop.create_task(site.start())

    try:
        logger.ok('Сервер запущен')
        loop.run_forever()
    except KeyboardInterrupt:
        logger.critical('Сервер принудительно остановлен')