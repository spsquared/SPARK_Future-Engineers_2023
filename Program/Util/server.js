const express = require('express');
const app = express();
const server = require('http').Server(app);

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
    });
});

server.listen(4040);