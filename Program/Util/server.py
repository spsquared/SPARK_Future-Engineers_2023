import socketio
import asyncio
import typing

# connects to internal proxy and uses that as server

__socket = socketio.AsyncClient()

def open():
    asyncio.get_event_loop().run_until_complete(__socket.connect('http://localhost:4041')) # because we can't have Python 3.7 or higher
def close():
    asyncio.get_event_loop().run_until_complete(__socket.disconnect())

def on(ev: str, cb: typing.Callable[[typing.Any], None]):
    @__socket.on(ev)
    def handle(data):
        cb(data)

async def __emit(ev, data):
    await __socket.emit(ev, data)
def emit(ev: str, data):
    asyncio.create_task(__emit(ev, data))

@__socket.event
def disconnect():
    print('disconnected')

open()