import asyncio
import json
from aiohttp import web
import aiohttp

class ChatServer:
    def __init__(self):
        self.clients = {}  # {websocket: username}
        self.messages = []
    
    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            async for msg in ws.iter_any():
                if isinstance(msg, str):
                    data = json.loads(msg)
                    
                    if data['type'] == 'join':
                        username = data['user']
                        self.clients[ws] = username
                        await self.broadcast_users()
                    
                    elif data['type'] == 'message':
                        username = self.clients.get(ws)
                        if username:
                            message = data['message']
                            self.messages.append({'user': username, 'message': message})
                            await self.broadcast_message(username, message)
        
        finally:
            if ws in self.clients:
                del self.clients[ws]
                await self.broadcast_users()
        
        return ws
    
    async def broadcast_users(self):
        users = list(self.clients.values())
        msg = json.dumps({'type': 'users', 'users': users})
        for ws in self.clients:
            if not ws.is_closed():
                await ws.send_str(msg)
    
    async def broadcast_message(self, user, message):
        msg = json.dumps({'type': 'message', 'user': user, 'message': message})
        for ws in self.clients:
            if not ws.is_closed():
                await ws.send_str(msg)

async def main():
    chat = ChatServer()
    app = web.Application()
    app.router.add_get('/ws', chat.handle_websocket)
    app.router.add_get('/', lambda r: web.FileResponse('index.html'))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print('Chat server running on port 8080')
    print('Access from: http://YOUR_PUBLIC_IP:8080')
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
