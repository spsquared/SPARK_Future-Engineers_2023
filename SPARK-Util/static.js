const express = require('express');
const app = express();
const server = require('http').Server(app);

const static = express.static(__dirname);
app.get('/', (req, res) => {
    res.writeHead(301, { location: '/SPARK-Control/' }); res.end()
});
app.use('/', (req, res, next) => {
    if (!ip.replace('::ffff:', '').startsWith('127.') && !(ip.endsWith(':1') && ip.replace(/[^0-9]/ig, '').split('').reduce((prev, curr) => prev + parseInt(curr), 0) == 1)) res.sendStatus(403);
    static(req, res, next);
});
server.listen(8081);