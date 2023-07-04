const express = require('express');
const app = express();
const server = require('http').Server(app);
const cors = require('cors');
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'DELETE', 'UPDATE', 'PUT', 'PATCH']
}));

const io = require('socket.io')(server);

const authIds = require('./auth.json');

io.on('connection', (socket) => {
    socket.emit('authenticate');
    socket.once('authenticateResponse', (id) => {
        if (!authIds.includes(id)) {
            socket.disconnect();
            return;
        }
        socket = socket;
        socket.emit('test')
    });
});

server.listen(4040);