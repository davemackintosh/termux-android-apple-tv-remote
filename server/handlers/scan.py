import json
import asyncio
from aiohttp import web
from pyatv import scan


async def handler(request):
    loop = asyncio.get_event_loop()
    results = await scan(loop=loop, storage=request.app["storage"])
    devices = []
    for result in results:
        services = []
        for service in result.services:
            services.append({
                "name": service.protocol.name
            })
        devices.append({
            "name": result.name,
            "identifier": result.identifier,
            "services": services,
        })

    return web.Response(
        text=json.dumps(devices),
        content_type="application/json",
    )
