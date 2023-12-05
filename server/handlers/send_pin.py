import json
from aiohttp import web


async def handler(request):
    if request.app.current_pairing is None:
        return web.Response(
            text=json.dumps({"error": "No pairing in progress"}),
            content_type="application/json",
            status=400,
        )

    try:
        body = await request.json()
        request.app.current_pairing.pin(body["pin"])

        await request.app.current_pairing.finish()
        await request.app.current_pairing.close()

        if request.app.current_pairing.has_paired:
            return web.Response(
                text=json.dumps({
                    "status": "paired",
                    "protocol": str(request.app.current_pairing.protocol),
                }),
                content_type="application/json",
            )
        else:
            return web.Response(
                text=json.dumps({"error": "failed to pair"}),
                status=400,
                content_type="application/json",
            )
    except Exception as ex:
        print(ex)
        return web.Response(
            text=json.dumps({
                "error": "Failed to pair with pin",
                "debug": f"{ex}"
                }),
            content_type="application/json",
            status=500,
        )
