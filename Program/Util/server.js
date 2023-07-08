const express = require('express');
const app = express();
const server = require('http').Server(app);
const cors = require('cors');
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'DELETE', 'UPDATE', 'PUT', 'PATCH']
}));

app.get('/', (req, res) => res.send('OK'));

const io = require('socket.io')(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST', 'DELETE', 'UPDATE', 'PUT', 'PATCH']
    }
});

const authIds = require('./auth.json');

io.on('connection', (socket) => {
    socket.emit('authenticate');
    socket.once('authenticateResponse', (id) => {
        if (!authIds.includes(id)) {
            socket.disconnect();
            return;
        }
        socket.emit('test');
    });
});

server.listen(4040);