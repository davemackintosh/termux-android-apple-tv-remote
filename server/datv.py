import asyncio
import aiohttp_cors
from aiohttp import WSMsgType, web
from handlers import (
    scan,
    pair,
    device,
    connect,
    send_pin,
    remote_control,
    playing,
    close,
)
from pyatv.storage.file_storage import FileStorage

routes = web.RouteTableDef()


@routes.get("/devices")
@routes.get("/devices/")
async def devices(request):
    return await scan.handler(request)


@routes.get("/devices/{id}")
@routes.get("/devices/{id}/")
async def device_info(request):
    return await device.handler(request)


@routes.post("/devices/{id}/pair")
@routes.post("/devices/{id}/pair/")
async def pair_device(request):
    return await pair.handler(request)


@routes.post("/devices/{id}/pair/pin")
@routes.post("/devices/{id}/pair/pin/")
async def send_pin_handler(request):
    return await send_pin.handler(request)


@routes.get("/devices/{id}/connect")
@routes.get("/devices/{id}/connect/")
async def device_connect(request):
    return await connect.handler(request)


@routes.post("/devices/{id}/remote_control")
@routes.post("/devices/{id}/remote_control/")
async def remote_control_handler(request):
    return await remote_control.handler(request)


@routes.get("/devices/{id}/playing")
async def playing_handler(request):
    return await playing.handler(request)


@routes.get("/devices/{id}/close")
async def close_handler(request):
    return await close.handler(request)


@routes.get("/ws/{id}")
async def websocket_handler(request):
    device_id = request.match_info["id"]
    atv = request.app["atv"].get(device_id)

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app["clients"].setdefault(device_id, []).append(ws)

    playstatus = await atv.metadata.playing()
    await ws.send_str(str(playstatus))

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            # Handle custom commands from client here
            if msg.data == "close":
                await ws.close()
        elif msg.type == WSMsgType.ERROR:
            print(f"Connection closed with exception: {ws.exception()}")

    request.app["clients"][device_id].remove(ws)

    return ws


async def on_shutdown(app: web.Application) -> None:
    for atv in app["atv"].values():
        atv.close()


def main():
    app = web.Application()
    loop = asyncio.get_event_loop()
    storage = FileStorage("$HOME/.pyatv.conf", loop)
    app.current_pairing = None
    app["pair_requests"] = {}
    app["atv"] = {}
    app["listeners"] = []
    app["storage"] = storage
    app["clients"] = {}
    app.add_routes(routes)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            max_age=3600,
            allow_methods="*"
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    app.on_shutdown.append(on_shutdown)
    web.run_app(app)


if __name__ == "__main__":
    main()
