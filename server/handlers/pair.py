import asyncio
import json
from aiohttp import web
from pyatv import scan, pair
from pyatv.const import Protocol
from server.headers import cors_headers


def handler(request):
    device_id = request.match_info["id"]
    protocol = request.match_info["protocol"]

    try:
        loop = asyncio.get_event_loop()
        atvs = await scan(loop=asyncio.get_event_loop())
        devices = [
            foundAtv for foundAtv in atvs if foundAtv.identifier == device_id]

        request.app.current_pairing = await pair(devices[0], protocol, loop, name="Android")
        await request.app.current_pairing.begin()
        return web.Response(
            text=json.dumps({"status": "pairing_begun"}),
            content_type="application/json",
            headers=cors_headers,
        )
    except Exception as ex:
        print(ex)
        return web.Response(
            text=json.dumps(
                {"error": "Failed to start pairing because: {ex}"}),
            content_type="application/json",
            status=500,
            headers=cors_headers,
        )
