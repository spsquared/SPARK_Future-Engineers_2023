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
        console.info('[SERVER] Rate limiting triggered by ' + req.ip ?? req.socket.remoteAddress);
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
        console.info(`[SERVER] Kicked ${ip} from server connection`);
        socket.disconnect();
        socket.onevent = (packet) => {};
        return;
    }
    console.info('[SERVER] Connection from server');
    if (hostConnected) {
        console.warn('[SERVER] Multiple hosts attempted to connect!');
        socket.disconnect();
        return;
    }
    hostConnected = true;
    let handleDisconnect = () => {
        hostConnected = false;
        console.info('[SERVER] Server disconnected');
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
            console.info(`[SERVER] Kicked ${ip} from client connection`);
            socket.disconnect();
            socket.onevent = (packet) => {};
            return;
        }
        console.info('[SERVER] Connection from client');
        socket.on('error', () => {});
        socket.on('#runProgram', (mode) => runProgram(mode)); 
        socket.on('#killPrograms', () => killPrograms()); 
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
    let processes = subprocess.execSync('ps ax --no-header | grep "python3"').toString('utf8').split('\n');
    for (let i in processes) {
        if ((processes[i].includes('manualdrive.py') || processes[i].includes('autodrive.py'))) {
            console.info('[RUN] Could not run: a program is already running!');
            io.emit('#programAlreadyRunning');
            return;
        }
    }
    io.emit('#programStarting', mode);
    const program = subprocess.spawn('python3', [path.resolve(mode == 'manual' ? 'manualdrive.py no_terminal' : 'autodrive.py')]);
    program.stdout.setEncoding('utf8');    
    program.stderr.setEncoding('utf8');
    program.stdout.on('data', (chunk) => {
        process.stdout.write(chunk.replaceAll('\n', '\n[RUN] '));
    });
    program.stderr.on('data', (chunk) => {
        process.stderr.write(chunk.replaceAll('\n', '\n[RUN] '));
    });
    program.on('close', (code) => console.info('[RUN] Program stopped with exit code ' + code));
};
function killPrograms() {
    console.info('[RUN] Killing all programs!');
    subprocess.exec('pkill -9 -f autodrive.py');
    subprocess.exec('pkill -9 -f manualdrive.py');
    io.emit('#killedPrograms');
};

server.listen(4041);
server2.listen(4040);