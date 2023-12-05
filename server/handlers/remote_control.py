import json
from aiohttp import web


async def handler(request):
    device_id = request.match_info["id"]
    atv = request.app["atv"].get(device_id)
    body = await request.json()

    print(dir(atv.remote_control))
    try:
        await getattr(atv.remote_control, body["command"])()
    except Exception as ex:
        print(ex)
        return web.Response(
            text=json.dumps({"error": f"Remote control command failed: {ex}"}),
            content_type="application/json",
        )
    return web.Response(
        text=json.dumps({"status": "OK"}), content_type="application/json"
    )
