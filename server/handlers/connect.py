import json
import asyncio
from aiohttp import web
from pyatv import scan, connect, interface


class DeviceListener(interface.DeviceListener, interface.PushListener):
    """Listener for device and push updates events."""

    def __init__(self, app, identifier):
        """Initialize a new DeviceListener."""
        self.app = app
        self.identifier = identifier

    def connection_lost(self, exception: Exception) -> None:
        """Call when connection was lost."""
        print(exception)
        self._remove()

    def connection_closed(self) -> None:
        """Call when connection was closed."""
        self._remove()

    def _remove(self):
        self.app["atv"].pop(self.identifier)
        self.app["listeners"].remove(self)

    def playstatus_update(self, _, playstatus: interface.Playing) -> None:
        """Call when play status was updated."""
        clients = self.app["clients"].get(self.identifier, [])
        for client in clients:
            asyncio.ensure_future(client.send_str(str(playstatus)))

    def playstatus_error(self, _, exception: Exception) -> None:
        """Call when an error occurred."""
        print(exception)


def add_credentials(config, query):
    """Add credentials to pyatv device configuration."""
    for service in config.services:
        proto_name = service.protocol.name.lower()
        if proto_name in query:
            config.set_credentials(service.protocol, query[proto_name])


async def handler(request):
    loop = asyncio.get_event_loop()
    device_id = request.match_info["id"]

    results = await scan(identifier=device_id, loop=loop, storage=request.app["storage"])
    if not results:
        return web.Response(
            text=json.dumps({"error": "Device not found"}),
            status=500,
            content_type="application/json",
        )

    add_credentials(results[0], request.query)

    try:
        atv = await connect(results[0], loop=loop, storage=request.app["storage"])
    except Exception as ex:
        return web.Response(
            text=json.dumps({"error": f"Failed to connect to device: {ex}"}),
            status=500,
            content_type="application/json",
        )

    listener = DeviceListener(request.app, device_id)
    atv.listener = listener
    atv.push_updater.listener = listener
    atv.push_updater.start()
    request.app["listeners"].append(listener)

    request.app["atv"][device_id] = atv
    return web.Response(
        text=json.dumps({"message": f"Connected to device {device_id}"}),
        content_type="application/json",
    )
