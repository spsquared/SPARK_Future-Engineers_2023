const express = require('express');
const app = express();
const server = require('http').Server(app);
app.use('/', express.static(__dirname));
server.listen(8081);