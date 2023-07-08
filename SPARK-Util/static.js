const express = require('express');
const app = express();
const server = require('http').Server(app);

const static = express.static(__dirname);
app.use('/', (req, res, next) => {
    if (req.ip != '127.0.0.1' && req.ip != '::1') res.sendStatus(403);
    if (Math.random() < 0.001) {
        res.sendStatus(418);
    }
    static(req, res, next);
});
server.listen(8081);