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
        console.info('Rate limiting triggered by ' + req.ip ?? req.socket.remoteAddress);
    }
});
const subprocess = require('child_process');
const path = require('path');

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
        console.info(`Kicked ${ip} from server connection`);
        socket.disconnect();
        socket.onevent = (packet) => {};
        return;
    }
    console.info('Connection from server');
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
            console.info(`Kicked ${ip} from client connection`);
            socket.disconnect();
            socket.onevent = (packet) => {};
            return;
        }
        console.info('Connection from client');
        socket.on('error', () => {});
        socket.on('#runProgram', (mode) => runProgram(mode)); 
        if (hostConnected) socket.emit('#programRunning');
        const onevent = socket.onevent;
        socket.onevent = (packet) => {
            if (packet.data[0] == null) {
                socket.disconnect();
                return;
            }
            onevent.call(socket, packet);
        };
        socket.onAny((event, ...args) => {
            if (event[0] === '#') return;
            hostio.emit(event, args); // arguments are condensed into one array for python socketio
        });
    });
});

function runProgram(mode) {
    console.info(`[RUN] Running program - ${mode} mode`);
    // check if already running
    let processes = subprocess.execSync('ps aux --no-header | grep "python3"').toString('utf8').split('\n');
    for (let i in processes) {
        if ((processes[i].includes('manualdrive.py') || processes[i].includes('autodrive.py')) && processes[i].includes('R')) {
            console.info('[RUN] Could not run: a program is already running!');
            return;
        }
    }
    io.emit('#programStarting');
    const program = subprocess.spawn('python3', [path.resolve(mode == 'manual' ? 'manualdrive.py' : 'autodrive.py')]);
    program.stdout.pipe(process.stdout);
    program.stderr.pipe(process.stderr);
    program.on('close', (code) => console.info('[RUN] Program stopped with exit code ' + code));
};

server.listen(4041);
server2.listen(4040);