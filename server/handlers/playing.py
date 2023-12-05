import json
from aiohttp import web


async def handler(request):
    device_id = request.match_info["id"]
    atv = request.app["atv"].get(device_id)
    try:
        status = await atv.metadata.playing()
    except Exception as ex:
        return web.Response(text=json.dumps({
            "error": f"Remote control command failed: {ex}"
        }))
    return web.Response(text=json.dumps({"status": status}))
