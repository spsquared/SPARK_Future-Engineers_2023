import asyncio
import websockets
import json as JSON
import typing
from threading import Thread
from IO import io
import time

# WebSocket server module for testing only

running = False

# listeners and broadcast
callbacks = {}
sendlist = []
def addListener(event: str, cb: typing.Callable[[typing.Any], None]):
    global callbacks, running
    if running:
        if event in callbacks:
            callbacks[event].append(cb)
        else:
            callbacks[event] = [cb]
def broadcast(event: str, data: typing.Any):
    global sendlist, running
    if running:
        for arr in sendlist:
            arr.append(JSON.dumps({'event': event, 'data': data}))

thread = None
threadLoop = asyncio.new_event_loop()

def open():
    global running, thread, threadLoop
    thread.start()

def close():
    global running, thread, threadLoop
    if running == True:
        running = False
        threadLoop.stop()
        thread.join()
        return True
    return False

async def __server(websocket, path):
    global sendlist
    index = len(sendlist)
    sendlist.append([])
    connected = True
    try:
        async def receive():
            global callbacks, running
            nonlocal connected
            # receive events
            while connected and running:
                json = await websocket.recv()
                res = JSON.loads(json)
                if res['event'] in callbacks:
                    for cb in callbacks[res['event']]:
                        cb(res['data'])
        async def send():
            global sendlist, running
            nonlocal connected, index
            # send events
            while connected and running:
                try:
                    if len(sendlist) > index:
                        if len(sendlist[index]) > 0:
                            data = sendlist[index][0]
                            del sendlist[index][0]
                            await websocket.send(data)
                            time.sleep(0.002)
                        else:
                            time.sleep(0.05)
                    else:
                        time.sleep(0.1)
                except websockets.exceptions.ConnectionClosedOK:
                    connected = False
                    try:
                        del sendlist[index]
                    except Exception:
                        True
                except websockets.exceptions.ConnectionClosedError:
                    connected = False
                    try:
                        del sendlist[index]
                    except Exception:
                        True
                except RuntimeError:
                    continue
        def send2():
            # middle function that allows async functions running in separate thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send())
                loop.close()
            except Exception:
                send2()
        sendThread = Thread(target = send2)
        sendThread.start()
        await receive()
        sendThread.join()
    except websockets.exceptions.ConnectionClosedOK:
        connected = False
        try:
            del sendlist[index]
        except Exception:
            True
    except websockets.exceptions.ConnectionClosedError:
        connected = False
        try:
            del sendlist[index]
        except Exception:
            True
    except KeyboardInterrupt:
        connected = False
        try:
            del sendlist[index]
        except Exception:
            True
    except Exception as err:
        connected = False
        try:
            del sendlist[index]
        except Exception:
            True
        print(err)
        io.error()

def __start():
    global running, __server, threadLoop
    running = True
    asyncio.set_event_loop(threadLoop)
    server = websockets.serve(__server, '192.168.1.151', 4040)
    threadLoop.run_until_complete(server)
    threadLoop.run_forever()

thread = Thread(target = __start)