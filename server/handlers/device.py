import json
import asyncio
from aiohttp import web
from pyatv import scan


async def handler(request):
    loop = asyncio.get_event_loop()
    device_id = request.match_info["id"]
    atvs = await scan(loop=loop, storage=request.app["storage"])
    devices = [
        foundAtv for foundAtv in atvs if foundAtv.identifier == device_id]
    result = devices[0]

    if result is None:
        return web.Response(
            text=json.dumps({
                "error": "device not found"
                }),
            status=404,
            content_type="application/json",
        )

    services = []
    for service in result.services:
        services.append({
            "name": service.protocol.name
        })

    atv = {
            "name": result.name,
            "services": services,
            "identifier": result.identifier
            }

    return web.Response(
        text=json.dumps(atv),
        content_type="application/json",
    )
