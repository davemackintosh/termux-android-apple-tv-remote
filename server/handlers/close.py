from aiohttp import web


async def handler(request):
    device_id = request.match_info["id"]
    atv = request.app["atv"].get(device_id)
    atv.close()

    return web.Response(text="OK")
