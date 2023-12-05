import json
import asyncio
from aiohttp import web
from server.headers import cors_headers
from pyatv import scan


async def handler(request):
    loop = asyncio.get_event_loop()
    results = await scan(loop=loop)
    devices = []
    services = []
    for result in results:
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
        headers=cors_headers,
    )
