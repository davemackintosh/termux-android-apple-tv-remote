import asyncio
import json
from aiohttp import web
from pyatv import scan, pair
from pyatv.const import Protocol


def protocolFromRequest(protocol: str) -> Protocol:
    return Protocol.Companion


async def handler(request):
    device_id = request.match_info["id"]
    body = await request.json()
    print(body)
    protocol = body["protocol"]

    try:
        loop = asyncio.get_event_loop()
        atvs = await scan(loop=loop, storage=request.app["storage"])
        devices = [
            foundAtv for foundAtv in atvs if foundAtv.identifier == device_id]

        request.app.current_pairing = await pair(
            devices[0],
            protocol=protocolFromRequest(protocol),
            loop=loop,
            name="Android",
            storage=request.app["storage"]
        )
        await request.app.current_pairing.begin()
        return web.Response(
            text=json.dumps({"status": "pairing_begun"}),
            content_type="application/json",
        )
    except Exception as ex:
        print(ex)
        return web.Response(
            text=json.dumps(
                {
                    "error": "Failed to start pairing because",
                    "debug": ex
                 }),
            content_type="application/json",
            status=500,
        )
