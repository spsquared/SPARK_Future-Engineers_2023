const express = require('express');
const app = express();
const server = require('http').Server(app);
const server2 = require('http').Server(app);
const cors = require('cors');
const { Server: SocketIO } = require('socket.io');

app.use(cors({
    origin: '*',
    methods: ['GET']
}));
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
    const ip = socket.handshake.headers['x-forwarded-for'] ?? socket.handshake.address ?? socket.request.socket.remoteAddress ?? socket.client.conn.remoteAddress ?? 'unknown';
    if (!ip.replace('::ffff:', '').startsWith('127.') && !(ip.endsWith(':1') && ip.replace(/[^0-9]/ig, '').split('').reduce((prev, curr) => prev + parseInt(curr), 0) == 1)) {
        console.log(`Kicked ${ip} from server connection`);
        socket.disconnect();
        socket.onevent = (packet) => {};
        return;
    }
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
    const ip = socket.handshake.headers['x-forwarded-for'] ?? socket.handshake.address ?? socket.request.socket.remoteAddress ?? socket.client.conn.remoteAddress ?? 'unknown';
    socket.emit('authenticate');
    socket.once('authenticateResponse', (id) => {
        if (!authIds.includes(id)) {
            console.log(`Kicked ${ip} from client connection`);
            socket.disconnect();
            socket.onevent = (packet) => {};
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