import asyncio
import json
from aiohttp import WSMsgType, web
from server.handlers import scan, pair
from server.headers import cors_headers
import pyatv

routes = web.RouteTableDef()


class DeviceListener(pyatv.interface.DeviceListener, pyatv.interface.PushListener):
    """Listener for device and push updates events."""

    def __init__(self, app, identifier):
        """Initialize a new DeviceListener."""
        self.app = app
        self.identifier = identifier

    def connection_lost(self, exception: Exception) -> None:
        """Call when connection was lost."""
        self._remove()

    def connection_closed(self) -> None:
        """Call when connection was closed."""
        self._remove()

    def _remove(self):
        self.app["atv"].pop(self.identifier)
        self.app["listeners"].remove(self)

    def playstatus_update(self, updater, playstatus: pyatv.interface.Playing) -> None:
        """Call when play status was updated."""
        clients = self.app["clients"].get(self.identifier, [])
        for client in clients:
            asyncio.ensure_future(client.send_str(str(playstatus)))

    def playstatus_error(self, updater, exception: Exception) -> None:
        """Call when an error occurred."""


def web_command(method):
    """Decorate a web request handler."""

    async def _handler(request):
        device_id = request.match_info["id"]
        atv = request.app["atv"].get(device_id)
        if not atv:
            return web.Response(
                text=json_error(f"Not connected to {device_id}"),
                status=500,
                content_type="application/json",
                headers=cors_headers,
            )
        return await method(request, atv)

    return _handler


def json_error(error: str) -> str:
    return json.dumps({"error": error})


def json_text(error: str) -> str:
    return json.dumps({"res": error})


def add_credentials(config, query):
    """Add credentials to pyatv device configuration."""
    for service in config.services:
        proto_name = service.protocol.name.lower()
        if proto_name in query:
            config.set_credentials(service.protocol, query[proto_name])


@routes.get("/devices")
async def devices(request):
    """Handle request to scan for devices."""
    return await scan.handler(request)


@routes.get("/devices/{id}/pair/{protocol}")
async def pair_device(request):
    """Handle request to pair with a device."""
    return await pair.handler(request)


@routes.get("/devices/{id}/pair/{protocol}/{pin}")
@web_command
async def send_pin(request, atv):
    """Handle request to pair with a device."""
    if request.app.current_pairing is None:
        return web.Response(
            text=json_error("No pairing in progress"),
            content_type="application/json",
            status=400,
            headers=cors_headers,
        )

    try:
        request.app.current_pairing.pin(request.match_info["pin"])
        await request.app.current_pairing.finish()
        await request.app.current_pairing.close()

        if request.app.current_pairing.has_paired:
            return web.Response(
                text=json_text("paired"),
                content_type="application/json",
                headers=cors_headers,
            )
        else:
            return web.Response(
                text=json_error("failed"),
                status=400,
                content_type="application/json",
                headers=cors_headers,
            )
    except Exception as ex:
        print(ex)
        return web.Response(
            text=json_error(f"Failed to pair with pin: {ex}"),
            content_type="application/json",
            status=500,
            headers=cors_headers,
        )


@routes.get("/devices/{id}/connect")
async def connect(request):
    """Handle request to connect to a device."""
    loop = asyncio.get_event_loop()
    device_id = request.match_info["id"]
    if device_id in request.app["atv"]:
        return web.Response(
            text=json_error(f"Already connected to {device_id}"),
            content_type="application/json",
            status=200,
            headers=cors_headers,
        )

    results = await pyatv.scan(identifier=device_id, loop=loop)
    if not results:
        return web.Response(
            text=json_error("Device not found"),
            status=500,
            content_type="application/json",
            headers=cors_headers,
        )

    add_credentials(results[0], request.query)

    try:
        atv = await pyatv.connect(results[0], loop=loop)
    except Exception as ex:
        return web.Response(
            text=json_error(f"Failed to connect to device: {ex}"),
            status=500,
            content_type="application/json",
            headers=cors_headers,
        )

    listener = DeviceListener(request.app, device_id)
    atv.listener = listener
    atv.push_updater.listener = listener
    atv.push_updater.start()
    request.app["listeners"].append(listener)

    request.app["atv"][device_id] = atv
    return web.Response(
        text=json_text(f"Connected to device {device_id}"),
        content_type="application/json",
        headers=cors_headers,
    )


@routes.get("/remote_control/{id}/{command}")
@web_command
async def remote_control(request, atv):
    """Handle remote control command request."""
    try:
        await getattr(atv.remote_control, request.match_info["command"])()
    except Exception as ex:
        print(f"ERR {ex}")
        return web.Response(
            text=json_error(f"Remote control command failed: {ex}"),
            content_type="application/json",
            headers=cors_headers,
        )
    return web.Response(
        text=json_text("OK"), content_type="application/json", headers=cors_headers
    )


@routes.get("/playing/{id}")
@web_command
async def playing(request, atv):
    """Handle request for current play status."""
    try:
        status = await atv.metadata.playing()
    except Exception as ex:
        return web.Response(text=f"Remote control command failed: {ex}")
    return web.Response(text=str(status))


@routes.get("/close/{id}")
@web_command
async def close_connection(request, atv):
    """Handle request to close a connection."""
    atv.close()
    return web.Response(text="OK")


@routes.get("/ws/{id}")
@web_command
async def websocket_handler(request, atv):
    """Handle incoming websocket requests."""
    device_id = request.match_info["id"]

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
    """Call when application is shutting down."""
    for atv in app["atv"].values():
        atv.close()


def main():
    """Script starts here."""
    print("server starting")
    app = web.Application()
    app.current_pairing = None
    app["pair_requests"] = {}
    app["atv"] = {}
    app["listeners"] = []
    app["clients"] = {}
    app["CORS"] = cors_headers
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app)


if __name__ == "__main__":
    main()
