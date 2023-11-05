var ctx = canvas.getContext("2d");
canvas.width = 544 * 2;
canvas.height = 308;


var image0 = null;
var image1 = null;

upload.onclick = function() {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = ".png";
    input.click();
    input.oninput = function() {
        if (input.files.length == 0) {
            return;
        }
        var reader = new FileReader();
        reader.onload = async function() {
            image0 = new Image();
            image0.src = reader.result;
            image1 = null;
            setTimeout(function() {
                refresh();
            });
        };
        reader.readAsDataURL(input.files[0]);
    };
};

var inputs = [left1, left2, left3, left4, left5, left6, left7, left8, right1, right2, right3, right4, right5, right6, right7, right8];
var startInputs = [35, 33, 30, 29, 28, 27, 27, 27, 17, 19, 19, 20, 20, 20, 19, 18];

var refresh = function() {
    if (image0 == null) {
        if (darkMode.checked) {
            ctx.fillStyle = "#000000";
            ctx.fillRect(0, 0, 544 * 2, 308);
        }
        else {
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(0, 0, 544 * 2, 308);
        }
        return;
    }
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, 544 * 2, 308);
    ctx.drawImage(image0, 0, 0);
    if (image1 != null) {
        ctx.drawImage(image1, 544, 0);
    }
    if (!darkMode.checked) {
        ctx.globalCompositeOperation = "difference";
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, 544 * 2, 308);
        ctx.globalCompositeOperation = "source-over";
    }
    ctx.fillStyle = "#0000ff99";
    for (var i = 0; i < 16; i++) {
        ctx.fillRect(i * 544 / 8, Number(inputs[i].value), 544 / 8, 1);
    }
};

if (localStorage.getItem("darkMode") == "true") {
    darkMode.checked = true;
    refresh();
}
darkMode.oninput = function() {
    localStorage.setItem("darkMode", darkMode.checked);
    refresh();
};

for (var i in inputs) {
    inputs[i].type = "number";
    inputs[i].value = startInputs[i];
    inputs[i].min = 0;
    inputs[i].max = 308;
    inputs[i].oninput = refresh;
}


const socket = io(ip + ':4040', {
    autoConnect: false,
    reconnection: false
});
let connected = false;
let toReconnect = false;
let autoReconnect = true;
const statusConnected = document.getElementById('statusConnected');
const statusRunning = document.getElementById('statusRunning');
const statusError = document.getElementById('statusError');
socket.on('connect', () => {
    connected = true;
});
var onDisconnect = function() {
    connected = false;
    setTimeout(reconnect, 1000);
};
socket.on('disconnect', onDisconnect);
socket.on('timeout', onDisconnect);
socket.on('error', onDisconnect);
socket.on('#authenticate', () => {
    socket.emit('#authenticateResponse', auth_uuid);
});
function reconnect(force) {
    if (toReconnect || force) {
        toReconnect = false;
        autoReconnect = true;
        document.querySelectorAll('.connectNow').forEach(button => button.remove());
        appendLog('Attempting to reconnect...');
        connect();
    }
};
function connect() {
    const req = new XMLHttpRequest();
    req.open('GET', `http://${ip}:4040`);
    req.onload = (res) => {
        if (req.status != 200) {
            req.onerror();
            return;
        }
        if (!socket.connected) socket.connect();
    };
    req.onerror = (err) => {
        connected = false;
        setTimeout(reconnect, 10000);
    };
    req.send();
};
window.addEventListener('load', connect);

var addCapture = function(images) {
    let encoding = images[2] ? 'data:image/png;base64,' : 'data:image/jpeg;base64,';
    image0 = new Image();
    image1 = new Image();
    image0.src = encoding + images[0];
    image1.src = encoding + images[1];
    setTimeout(function() {
        refresh();
    });
}
socket.on('capture', addCapture); // 0 is jpeg, 1 is png
capture.onclick = function() {
    socket.emit('capture', { save: false, filter: true, undistort: true, colors: false });
}