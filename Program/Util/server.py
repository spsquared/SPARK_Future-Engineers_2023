import socketio
import asyncio
import typing

# connects to internal proxy and uses that as server

__socket = socketio.AsyncClient()

async def __start():
    await __socket.connect('http://localhost:4041')
asyncio.run(__start())

def on(ev: str, cb: typing.Callable[[typing.Any], None]):
    @__socket.on(ev)
    def handle(data):
        cb(data)

async def __emit(ev, data):
    await __socket.emit(ev, data)
def emit(ev: str, data):
    asyncio.create_task(__emit(ev, data))
