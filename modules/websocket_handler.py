from aiohttp import web, WSMsgType
from typing import Set

class WebSocketHandler:
    def __init__(self):
        self.connections = set()
        self.healthy = True

    async def handle_connection(self, request):
        ws = web.WebSocketResponse(heartbeat=120)
        await ws.prepare(request)
        self.connections.add(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    if msg.data == 'ping':
                        await ws.send_str('pong')
                        self.healthy = True
                elif msg.type == web.WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
                    self.healthy = False
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.healthy = False
        finally:
            self.connections.remove(ws)
        return ws

    async def broadcast(self, data: dict):
        for ws in self.connections:
            try:
                await ws.send_json(data)
            except:
                continue

async def setup(bot):
    pass