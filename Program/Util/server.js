const express = require('express');
const app = express();
const server = require('http').Server(app);
const server2 = require('http').Server(app);
const { Server: SocketIO } = require('socket.io');

app.get('/', (req, res) => res.send('OK'));

const hostio = new SocketIO(server);
const io = new SocketIO(server2, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST', 'DELETE', 'UPDATE', 'PUT', 'PATCH']
    }
});
const authIds = require('./auth.json');

const recentData = {};
let hostConnectionCount = 0;
hostio.on('connection', (socket) => {
    hostConnectionCount++;
    socket.on('disconnect', () => hostConnectionCount--);
    socket.on('timeout', () => hostConnectionCount--);
    socket.on('error', () => hostConnectionCount--);
    if (hostConnectionCount > 1) {
        io.emit('multipleHosts');
        hostio.emit('multipleHosts');
    }
    socket.onAny((event, ...args) => { // python socketio only allows 1 argument but sure
        io.emit(event, ...args);
        if (event === 'data') {
            // store in recentData
        }
    });
});
io.on('connection', (socket) => {
    socket.emit('authenticate');
    socket.once('authenticateResponse', (id) => {
        if (!authIds.includes(id)) {
            socket.disconnect();
            return;
        }
        socket.on('error', (err) => console.log(err));
        const onevent = socket.onevent;
        socket.onevent = (packet) => {
            if (packet.data[0] == null) {
                socket.disconnect();
                return;
            }
            onevent.call(socket, packet);
        };
        socket.onAny((event, ...args) => {
            if (event === 'error') return;
            if (event === 'getRecentData') {
                socket.emit('recentData', recentData);
                return;
            }
            hostio.emit(event, args); // arguments are condensed into one array for python socketio
        });
    });
});

server.listen(4041);
server2.listen(4040);