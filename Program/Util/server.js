const express = require('express');
const app = express();
const server = require('http').Server(app);
const server2 = require('http').Server(app);
const rateLimit = require('express-rate-limit');
const cors = require('cors');
const { Server: SocketIO } = require('socket.io');
const limiter = rateLimit({
    windowMs: 100,
    max: 5,
    handler: function (req, res, options) {
        console.log('Rate limiting triggered by ' + req.ip ?? req.socket.remoteAddress);
    }
});
const subprocess = require('node:child_process');
const path = require('node:path');

app.use(cors({
    origin: '*',
    methods: ['GET']
}));
app.use(limiter);
app.get('/', (req, res) => res.send('OK'));

const hostio = new SocketIO(server);
const io = new SocketIO(server2, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST', 'DELETE', 'UPDATE', 'PUT', 'PATCH']
    }
});
const authIds = require('./auth.json');

// no input validation to be found here!!!!
// what could go wrong??

let hostConnected = false;
hostio.on('connection', (socket) => {
    const ip = socket.handshake.headers['x-forwarded-for'] ?? socket.handshake.address ?? socket.request.socket.remoteAddress ?? socket.client.conn.remoteAddress ?? 'un-ip';
    if (!ip.replace('::ffff:', '').startsWith('127.') && !(ip.endsWith(':1') && ip.replace(/[^0-9]/ig, '').split('').reduce((prev, curr) => prev + parseInt(curr), 0) == 1)) {
        console.log(`Kicked ${ip} from server connection`);
        socket.disconnect();
        socket.onevent = (packet) => {};
        return;
    }
    console.log('Connection from server');
    if (hostConnected) {
        console.warn('Multiple hosts attempted to connect!');
        socket.disconnect();
        return;
    }
    hostConnected = true;
    let handleDisconnect = () => {
        hostConnected = false;
        io.emit('#programStopped');
    };
    socket.on('disconnect', handleDisconnect);
    socket.on('timeout', handleDisconnect);
    socket.on('error', handleDisconnect);
    socket.onAny((event, ...args) => { // python socketio only allows 1 argument but sure
        io.emit(event, ...args);
    });
    io.emit('#programRunning');
});
io.on('connection', (socket) => {
    const ip = socket.handshake.headers['x-forwarded-for'] ?? socket.handshake.address ?? socket.request.socket.remoteAddress ?? socket.client.conn.remoteAddress ?? 'unknown';
    socket.emit('#authenticate');
    socket.once('#authenticateResponse', (id) => {
        if (!authIds.includes(id)) {
            console.log(`Kicked ${ip} from client connection`);
            socket.disconnect();
            socket.onevent = (packet) => {};
            return;
        }
        console.log('Connection from client');
        socket.on('error', (err) => console.log(err));
        socket.on('#runProgram', (type) => runProgram(type == 'manual' ? 'manualdrive.py' : 'autodrive.py')); 
        const onevent = socket.onevent;
        socket.onevent = (packet) => {
            if (packet.data[0] === '#runProgram') return;
            if (packet.data[0] == null) {
                socket.disconnect();
                return;
            }
            onevent.call(socket, packet);
        };
        socket.onAny((event, ...args) => {
            hostio.emit(event, args); // arguments are condensed into one array for python socketio
        });
    });
});

function runProgram(file) {
    // check if is already running
    let cmd;
    switch (process.platform) {
        case 'win32': cmd = 'taskList'; break;
        case 'darwin': cmd = 'ps -ax | grep '
        case 'linux': cmd = 'ps -A'; break;
        default: break;
    }
    if (cmd != undefined) {
        let stdout = subprocess.execSync(cmd);
        if (stdout.toString('utf8').toLowerCase().includes(file)) return;
    }
    const program = subprocess.spawn('python3', [path.resolve(file)]);
    program.stdout.pipe(process.stdout);
    program.stderr.pipe(process.stderr);
};

server.listen(4041);
server2.listen(4040);