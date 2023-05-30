window.addEventListener('error', (e) => {
    // appendLog(`An error occured:<br>${e.message}<br>${e.filename} ${e.lineno}:${e.colno}`, 'red');
    appendLog('An error occured!');
});
const ip = '192.168.1.151';

socket = new WebSocket('ws://' + ip + ':4040');

const log = document.getElementById('eventLogBody');
const callbacks = [];
let connected = false;
let toReconnect = false;
let autoReconnect = true;
function addListener(event, cb) {
    callbacks[event] = cb;
};
function send(event, data) {
    if (connected) {
        socket.send(JSON.stringify({
            event: event,
            data: data
        }));
    }
};
socket.onmessage = function (e) {
    if (e.data != 'ping') {
        let json = JSON.parse(e.data);
        for (let i in callbacks) {
            if (i == json.event) {
                callbacks[i](json.data);
            }
        }
    }
};
socket.onopen = function () {
    connected = true;
    appendLog('Connected!', 'lime');
};
socket.onclose = function () {
    connected = false;
    if (autoReconnect) toReconnect = true;
    appendLog('Connection closed<button class="connectNow" onclick="reconnect(true);">RECONNECT NOW</button>', 'red');
    setTimeout(reconnect, 10000);
};
function reconnect(force) {
    if (toReconnect || force) {
        toReconnect = false;
        autoReconnect = true;
        document.querySelectorAll('.connectNow').forEach(button => button.remove());
        appendLog('Attempting to reconnect...');
        let newsocket = new WebSocket('ws://' + ip + ':4040');
        newsocket.onmessage = socket.onmessage;
        newsocket.onopen = socket.onopen;
        newsocket.onclose = socket.onclose;
        socket = newsocket;
    }
};

// messages
const pendingsounds = [];
let first = true;
async function playSound() {
    if (first) {
        for (let i = 0; i < 10; i++) {
            await new Promise(function (resolve, reject) {
                let ping = new Audio('./sounds/ping.mp3');
                ping.preload = true;
                ping.addEventListener('loadeddata', function () {
                    pendingsounds.push(ping);
                    resolve();
                });
            });
        }
        first = false;
    }
    pendingsounds[0].play();
    pendingsounds.shift();
    let ping = new Audio('./sounds/ping.mp3');
    ping.preload = true;
    ping.addEventListener('loadeddata', function () {
        pendingsounds.push(ping);
    });
};
function appendLog(text, color) {
    const div = document.createElement('div');
    div.classList.add('logBlock');
    div.innerHTML = text;
    div.style.backgroundColor = color ?? '';
    let scroll = false;
    if (log.scrollTop + log.clientHeight >= log.scrollHeight - 5) scroll = true;
    log.appendChild(div);
    if (scroll) log.scrollTop = log.scrollHeight;
};
addListener('message', function (data) {
    playSound();
    appendLog(data);
});

// keys
document.onkeydown = function (e) {
    const key = e.key.toLowerCase();
    send('key', { key: key });
};
document.onkeyup = function (e) {
    const key = e.key.toUpperCase();
    send('key', { key: key });
};

// joystick
const joystick = document.getElementById('joystick');
const joystickPin = document.getElementById('joystickPin');
const sliderX = document.getElementById('sliderX');
const sliderY = document.getElementById('sliderY');

let grabbing = false;
let grabbingtouch = false;
let throttle = 0;
let steering = 0;
joystick.onmousedown = function (e) {
    grabbing = true;
};
joystick.addEventListener('touchstart', function (e) {
    grabbingtouch = true;
}, { passive: true });
document.onmouseup = function (e) {
    if (grabbing) {
        grabbing = false;
        joystickPin.style.right = '114px';
        joystickPin.style.bottom = '114px';
        sliderX.style.bottom = '140px';
        sliderY.style.right = '140px';
        throttle = 0;
        steering = 0;
        send('joystick', { throttle: 0, steering: 0 });
    }
};
document.addEventListener('touchend', function (e) {
    if (grabbingtouch) {
        grabbingtouch = false;
        joystickPin.style.right = '110px';
        joystickPin.style.bottom = '110px';
        sliderX.style.bottom = '140px';
        sliderY.style.right = '140px';
        throttle = 0;
        steering = 0;
        send('joystick', { throttle: 0, steering: 0 });
    }
}, { passive: true });
document.addEventListener('touchcancel', function (e) {
    if (grabbingtouch) {
        grabbingtouch = false;
        joystickPin.style.right = '114px';
        joystickPin.style.bottom = '114px';
        sliderX.style.bottom = '140px';
        sliderY.style.right = '140px';
        throttle = 0;
        steering = 0;
        send('joystick', { throttle: 0, steering: 0 });
    }
}, { passive: true });
document.onmousemove = function (e) {
    if (grabbing) {
        let x = Math.max(-110, Math.min(e.clientX - window.innerWidth + 150, 110));
        let y = Math.max(-110, Math.min(e.clientY - window.innerHeight + 150, 110));
        throttle = Math.round(-y * 90 / 99);
        steering = Math.round(x * 90 / 99);
        joystickPin.style.bottom = 114 - y + 'px';
        joystickPin.style.right = 114 - x + 'px';
        sliderX.style.bottom = 140 - y + 'px';
        sliderY.style.right = 140 - x + 'px';
    }
};
document.addEventListener('touchmove', function (e) {
    if (grabbingtouch) {
        for (let i in e.touches) {
            if (joystick.contains(e.touches[i].target)) {
                let x = Math.max(-110, Math.min(e.touches[i].clientX - window.innerWidth + 150, 110));
                let y = Math.max(-110, Math.min(e.touches[i].clientY - window.innerHeight + 150, 110));
                throttle = Math.round(-y * 90 / 99);
                steering = Math.round(x * 90 / 99);
                joystickPin.style.bottom = 114 - y + 'px';
                joystickPin.style.right = 114 - x + 'px';
                sliderX.style.bottom = 140 - y + 'px';
                sliderY.style.right = 140 - x + 'px';
                break;
            }
        }
    }
}, { passive: true });

// controllers
let trim = 0;
let trim2 = 0.05;
let pressedbuttons = [];
function updateControllers() {
    let controllers = navigator.getGamepads();
    for (let i in controllers) {
        if (controllers[i] instanceof Gamepad) {
            let controller = controllers[i];
            throttle = Math.round(controller.axes[1] * -100);
            steering = Math.round((controller.axes[2] - trim2) * 100) - trim;
            if (controller.buttons[8].pressed && pressedbuttons.indexOf(8) == -1) {
                if (controller.buttons[7].pressed) document.getElementById('captureFilterButton').click();
                else document.getElementById('captureButton').click();
                pressedbuttons.push(8);
            } else if (!controller.buttons[8].pressed && pressedbuttons.indexOf(8) != -1) {
                pressedbuttons.splice(pressedbuttons.indexOf(8), 1);
            }
            if (controller.buttons[9].pressed && pressedbuttons.indexOf(9) == -1) {
                if (controller.buttons[7].pressed) document.getElementById('captureFilterStreamButton').click();
                else document.getElementById('captureStreamButton').click();
                pressedbuttons.push(9);
            } else if (!controller.buttons[9].pressed && pressedbuttons.indexOf(9) != -1) {
                pressedbuttons.splice(pressedbuttons.indexOf(9), 1);
            }
            if (controller.buttons[0].pressed && pressedbuttons.indexOf(0) == -1) {
                if (controller.buttons[7].pressed) document.getElementById('filterStreamButton').click();
                else document.getElementById('streamButton').click();
                pressedbuttons.push(0);
            } else if (!controller.buttons[0].pressed && pressedbuttons.indexOf(0) != -1) {
                pressedbuttons.splice(pressedbuttons.indexOf(0), 1);
            }
            if (controller.buttons[1].pressed && pressedbuttons.indexOf(1) == -1) {
                document.getElementById('predictionButton').click();
                pressedbuttons.push(1);
            } else if (!controller.buttons[1].pressed && pressedbuttons.indexOf(1) != -1) {
                pressedbuttons.splice(pressedbuttons.indexOf(1), 1);
            }
            joystickPin.style.bottom = 114 - (controller.axes[1] * 110) + 'px';
            joystickPin.style.right = 114 - (controller.axes[2] * 110) + 'px';
            sliderX.style.bottom = 140 - (controller.axes[1] * 110) + 'px';
            sliderY.style.right = 140 - (controller.axes[2] * 110) + 'px';
            break;
        }
    }
};
setInterval(function () {
    updateControllers()
}, 25);

// send
setInterval(function () {
    if (throttle != 0 || steering != 0) {
        send('joystick', { throttle: throttle, steering: steering });
    }
}, 50);

// capture
document.getElementById('captureButton').onclick = function (e) {
    send('capture', {});
};
let streaming = false;
document.getElementById('captureStreamButton').onclick = function (e) {
    streaming = !streaming;
    send('captureStream', { state: streaming });
    if (streaming) {
        document.getElementById('captureStreamButton').innerText = 'STOP CAPTURE STREAM';
        document.getElementById('captureStreamButton').style.backgroundColor = 'lightcoral';
    } else {
        document.getElementById('captureStreamButton').innerText = 'START CAPTURE STREAM';
        document.getElementById('captureStreamButton').style.backgroundColor = 'lightgreen';
    }
};
document.getElementById('captureFilterButton').onclick = function (e) {
    let arr = [];
    for (let i in sliders) {
        arr.push(sliders[i].value);
    }
    send('captureFilter', arr);
};
let filterstreaming = false;
document.getElementById('captureFilterStreamButton').onclick = function (e) {
    let arr = [];
    for (let i in sliders) {
        arr.push(sliders[i].value);
    }
    filterstreaming = !filterstreaming;
    send('captureFilterStream', { colors: arr, state: filterstreaming });
    if (filterstreaming) {
        document.getElementById('captureFilterStreamButton').innerText = 'STOP FILTERED CAPTURE STREAM';
        document.getElementById('captureFilterStreamButton').style.backgroundColor = 'lightcoral';
    } else {
        document.getElementById('captureFilterStreamButton').innerText = 'START FILTERED CAPTURE STREAM';
        document.getElementById('captureFilterStreamButton').style.backgroundColor = 'lightgreen';
    }
};

// filtered capture (ignore the terrible coding practices this was intended to be a temporary thing)
let sliders = [
    document.getElementById('redHMax'),
    document.getElementById('greenHMax'),
    document.getElementById('blueHMax'),
    document.getElementById('redSMax'),
    document.getElementById('greenSMax'),
    document.getElementById('blueSMax'),
    document.getElementById('redVMax'),
    document.getElementById('greenVMax'),
    document.getElementById('blueVMax'),
    document.getElementById('redHMin'),
    document.getElementById('greenHMin'),
    document.getElementById('blueHMin'),
    document.getElementById('redSMin'),
    document.getElementById('greenSMin'),
    document.getElementById('blueSMin'),
    document.getElementById('redVMin'),
    document.getElementById('greenVMin'),
    document.getElementById('blueVMin')
];
function updateSlider(i) {
    document.getElementById(sliders[i].id + 'indicator').innerText = sliders[i].value;
    if (sliders[i].id.includes('H')) {
        sliders[i].style.setProperty('--hue', sliders[i].value * 2);
        sliders[i + 3].style.setProperty('--hue', sliders[i].value * 2);
        sliders[i + 6].style.setProperty('--hue', sliders[i].value * 2);
    } else if (sliders[i].id.includes('S')) {
        sliders[i].style.setProperty('--saturation', sliders[i].value * (100 / 255) + '%');
        sliders[i + 3].style.setProperty('--saturation', sliders[i].value * (100 / 255) + '%');
    } else if (sliders[i].id.includes('V')) {
        sliders[i].style.setProperty('--value', sliders[i].value * (50 / 255) + '%');
    }
};
function setColors(colors) {
    for (let i in colors) {
        sliders[i].value = colors[i];
        updateSlider(parseInt(i));
    }
};
addListener('colors', setColors);

// non capture streams and iamges
document.getElementById('viewButton').onclick = function (e) {
    send('view', {});
};
document.getElementById('viewFilterButton').onclick = function (e) {
    let arr = [];
    for (let i in sliders) {
        arr.push(sliders[i].value);
    }
    send('viewFilter', arr)
};
let streaming2 = false;
let filterstreaming2 = false;
document.getElementById('streamButton').onclick = function (e) {
    streaming2 = !streaming2;
    send('stream', { state: streaming2 });
    if (streaming2) {
        document.getElementById('streamButton').innerText = 'STOP STREAM';
        document.getElementById('streamButton').style.backgroundColor = 'lightcoral';
    } else {
        document.getElementById('streamButton').innerText = 'START STREAM';
        document.getElementById('streamButton').style.backgroundColor = 'lightgreen';
    }
};
document.getElementById('filterStreamButton').onclick = function (e) {
    filterstreaming2 = !filterstreaming2;
    let arr = [];
    for (let i in sliders) {
        arr.push(sliders[i].value);
    }
    send('filterstream', { colors: arr, state: filterstreaming2 });
    if (filterstreaming2) {
        document.getElementById('filterStreamButton').innerText = 'STOP FILTERED STREAM';
        document.getElementById('filterStreamButton').style.backgroundColor = 'lightcoral';
    } else {
        document.getElementById('filterStreamButton').innerText = 'START FILTEREDSTREAM';
        document.getElementById('filterStreamButton').style.backgroundColor = 'lightgreen';
    }
};

// prediction view
document.getElementById('predictionButton').onclick = function (e) {
    send('prediction', {});
};

// bad coding practices
let initcolors = [
    [
        25, 255, 255,
        0, 95, 75
    ],
    [
        110, 255, 255,
        30, 30, 40
    ],
    [
        140, 255, 255,
        90, 80, 70
    ],
];
sliders[0].value = initcolors[0][0];
sliders[1].value = initcolors[1][0];
sliders[2].value = initcolors[2][0];
sliders[3].value = initcolors[0][1];
sliders[4].value = initcolors[1][1];
sliders[5].value = initcolors[2][1];
sliders[6].value = initcolors[0][2];
sliders[7].value = initcolors[1][2];
sliders[8].value = initcolors[2][2];
sliders[9].value = initcolors[0][3];
sliders[10].value = initcolors[1][3];
sliders[11].value = initcolors[2][3];
sliders[12].value = initcolors[0][4];
sliders[13].value = initcolors[1][4];
sliders[14].value = initcolors[2][4];
sliders[15].value = initcolors[0][5];
sliders[16].value = initcolors[1][5];
sliders[17].value = initcolors[2][5];
for (let i in sliders) {
    updateSlider(parseInt(i));
}

// capture display
let maxHistory = 1000;
let data = 0;
const history = [];
let index = 0;
let lefting = false;
let righting = false;
let fasting = false;
let slowing = false;
const fpsTimes = [];
const displayImg = document.getElementById('displayImg');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext("2d");
const canvas2 = document.getElementById('canvas2');
const ctx2 = canvas2.getContext("2d");
const historySlider = document.getElementById('historySlider');
const FPS = document.getElementById('fps');
const strPredict = document.getElementById('strPredict');
const wallStrPredict = document.getElementById('wallStrPredict');
const pillarStrPredict = document.getElementById('pillarStrPredict');
const strReason = document.getElementById('strReason');
const wallHeightLeft = document.getElementById('wallHeightLeft');
const wallHeightCenter = document.getElementById('wallHeightCenter');
const wallHeightRight = document.getElementById('wallHeightRight');
const turnsMade = document.getElementById('turnsMade');
const turnCooldown = document.getElementById('turnCooldown');
const justTurned = document.getElementById('justTurned');
const passedPillar = document.getElementById('passedPillar');
canvas.width = 272;
canvas.height = 154;
canvas2.width = 272;
canvas2.height = 154;
let displayTimer = 0;
let drawn = false;
let displayDelay = 5;
window.onresize = () => {
    canvas.width = 272;
    canvas.height = 154;
    canvas2.width = 272;
    canvas2.height = 154;
    displayChange();
    // imgRenderCanvas.width = 272;
    // imgRenderCanvas.height = 154;
};
function addCapture(img) {
    // imgRenderCtx.clearRect(0, 0, 272, 154);
    // const tempImg = new Image();
    // tempImg.src = 'data:image/png;base64,'+img;
    // tempImg.onload = () => {
    //     imgRenderCtx.drawImage(tempImg, 0, 0);
    //     // imgRenderCtx.fillStyle = '#FF0000'
    //     // imgRenderCtx.fillRect(0, 0, 272, 154)
    //     const imgData = imgRenderCtx.getImageData(0, 0, 272, 154);
    //     console.log(imgData)
    //     for (let i = 3; i < 167552; i += 4) { // 272 * 154 * 4
    //         imgData.data[i] = 255;
    //     }
    //     imgRenderCtx.putImageData(imgData, 0, 0);
    //     let procImg = imgRenderCanvas.toDataURL('image/png');
    // };
    history.unshift({
        img: 'data:image/png;base64,' + img,
        blobs: [[], [], [], []],
        steer: [0, 'none', 0, 0],
        wall: {
            heights: []
        },
        turns: [false, 0, 0],
        passed: 0
    });
    index = 0;
    if (history.length > maxHistory) {
        history.pop();
    }
    historySlider.max = history.length;
    historySlider.value = history.length;
    displayTimer = performance.now();
    drawn = false;

    let now = performance.now();
    while (fpsTimes.length > 0 && fpsTimes[0] <= now - 1000) {
        fpsTimes.shift();
    }
    fpsTimes.push(now);
    FPS.innerHTML = 'FPS: ' + fpsTimes.length;
};
function addBlobs(data) {
    index = 0;
    history[index].blobs = data;
    if (history.length > maxHistory) {
        history.pop();
    }
    displayTimer = performance.now();
    drawn = false;
};
function drawBlobs() {
    let data = history[index].blobs;
    ctx.clearRect(0, 0, 272, 154);
    for (let i of data[1]) {
        drawLightBlob(i, 0);
    }
    for (let i of data[3]) {
        drawLightBlob(i, 1);
    }
    drawBlob(data[0], 0);
    drawBlob(data[2], 1);
};
function drawBlob(blob, blobColor) {
    if (!blob) {
        return;
    }
    ctx.beginPath();
    if (blobColor === 0) {
        ctx.strokeStyle = "#f00";
        ctx.fillStyle = "#F005";
    }
    else {
        ctx.strokeStyle = "#0f0"
        ctx.fillStyle = "#0F05";
    }
    ctx.arc(blob[0], blob[1], blob[2] * 2, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
};
function drawLightBlob(blob, blobColor) {
    if (!blob) {
        return;
    }
    ctx.beginPath();
    if (blobColor === 0) {
        ctx.strokeStyle = "#f00";
        ctx.fillStyle = "#F005";
    }
    else {
        ctx.strokeStyle = "#0f0"
        ctx.fillStyle = "#0F05";
    }
    ctx.arc(blob[0], blob[1], blob[2] * 2, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
};
function addData(data) {
    index = 0;
    // steering data
    history[index].steer = data[0];
    // wall data
    for (var i = 0; i < 8; i += 1) {
        history[index].wall.heights[i] = JSON.parse(data[1][i]);
    }
    // history[index].wall[0] = parseFloat(data[1]);
    // history[index].wall[1] = parseFloat(data[2]);
    // history[index].wall[2] = parseFloat(data[3]);
    // history[index].wall[3] = JSON.parse(data[4]);
    // history[index].wall[4] = JSON.parse(data[5]);
    // history[index].wall[5] = JSON.parse(data[6]);
    // history[index].wall[6] = JSON.parse(data[7]);
    // history[index].wall[7] = JSON.parse(data[8]);
    // history[index].wall[8] = JSON.parse(data[9]);
    // turn data
    // if (data[10][0] == 'True') data[10][0] = true;
    // else if (data[10][0] == 'False') data[10][0] = false;
    // data[10][1] = parseInt(data[10][1]);
    // data[10][2] = parseInt(data[10][2]);
    // history[index].turns = data[10];
    // // pass data
    // history[index].passed = parseInt(data[11]);
    if (history.length > maxHistory) {
        history.pop();
    }
    displayTimer = performance.now();
    drawn = false;
};
function showPredictions() {
    let data = history[index].steer;
    strPredict.innerText = 'Final Steering: ' + Math.round(data[0]);
    strReason.innerText = data[1];
    wallStrPredict.innerText = 'Wall Steering: ' + Math.round(data[2]);
    pillarStrPredict.innerText = 'Pillar Steering: ' + Math.round(data[3]);
};
function showWallData() {
    let data = history[index].wall.heights;
    if (data.length === 0) {
        return;
    }
    canvas2.width = 272;
    canvas2.height = 154;
    ctx2.clearRect(0, 0, 272, 154);
    ctx2.fillStyle = '#FFF9';
    for (let i = 0; i < 8; i++) {
        for (var j = 0; j < 34; j++) {
            try {
                ctx2.fillRect(i * 34 + j, 78, 1, data[i][j]);
            }
            catch (err) {
                appendLog("'data'", '#c4c4c4');
            }
        }
    }
    // wallHeightLeft.innerText = 'L: ' + data[0];
    // wallHeightCenter.innerText = 'C: ' + data[1];
    // wallHeightRight.innerText = 'R: ' + data[2];
};
function showTurnPassData() {
    let data = history[index].turns;
    justTurned.innerText = data[0];
    turnCooldown.innerText = data[1];
    turnsMade.innerText = data[2];
    passedPillar.innerText = history[index].passed;
};
function displayBack() {
    index = Math.min(index + 1, history.length - 1);
    historySlider.max = history.length;
    historySlider.value = history.length - index;
    displayTimer = performance.now();
    drawn = false;
};
function displayFront() {
    index = Math.max(index - 1, 0);
    historySlider.max = history.length;
    historySlider.value = history.length - index;
    displayTimer = performance.now();
    drawn = false;
};
function displayChange() {
    historySlider.max = history.length;
    index = history.length - parseInt(historySlider.value);
    if (history[index]) {
        displayImg.src = history[index].img;
        drawBlobs();
        showWallData();
        showPredictions();
        showTurnPassData();
    }
};
function downloadFrame() {
    const downloadCanvas = document.createElement('canvas');
    downloadCanvas.width = 272;
    downloadCanvas.height = 154;
    const downloadctx = downloadCanvas.getContext('2d');
    downloadctx.drawImage(displayImg, 0, 0);
    downloadctx.drawImage(canvas, 0, 0);
    downloadctx.drawImage(canvas2, 0, 0);
    // set data
    let data = downloadCanvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = data;
    let current = new Date();
    a.download = `SPARK-img_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.png`;
    a.click();
};
function downloadSession() {
    // data...
    const data = 'data:text/json;charset=UTF-8,' + encodeURIComponent(JSON.stringify(history));
    const a = document.createElement('a');
    a.href = data;
    let current = new Date();
    a.download = `SPARK-data_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.json`;
    a.click();
};
function importSession() {
    // create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.click();
    input.oninput = () => {
        // read files
        let files = input.files;
        if (files.length == 0) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            // set history
            let raw = JSON.parse(e.target.result);
            history.splice(0, history.length);
            for (let i in raw) {
                history.push(raw[i]);
            }
            historySlider.max = 0;
            displayChange();
        };
        reader.readAsText(files[0]);
    };
};
addListener('capture', addCapture);
addListener('blobs', addBlobs);
addListener('values', addData);
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    FPS.innerHTML = 'FPS: ' + fpsTimes.length;
}, 1000);
setInterval(() => {
    if (performance.now() - displayTimer >= displayDelay && !drawn) {
        drawn = true;
        displayChange();
    }
}, 1);
document.addEventListener('keydown', (e) => {
    if (e.key == 'ArrowLeft') {
        lefting = true;
    } else if (e.key == 'ArrowRight') {
        righting = true;
    } else if (e.key == 'Control') {
        fasting = true;
    } else if (e.key == 'Shift') {
        slowing = true;
    } else if (e.key.toLowerCase() == 's' && e.ctrlKey) {
        downloadSession();
        e.preventDefault();
    } else if (e.key.toLowerCase() == 'o' && e.ctrlKey) {
        importSession();
        e.preventDefault();
    }
});
document.addEventListener('keyup', (e) => {
    if (e.key == 'ArrowLeft') {
        lefting = false;
    } else if (e.key == 'ArrowRight') {
        righting = false;
    } else if (e.key == 'Control') {
        fasting = false;
    } else if (e.key == 'Shift') {
        slowing = false;
    }
});
let timer = 0;
setInterval(() => {
    timer++;
    if ((slowing && timer > 10) || (!slowing && timer > 2) || fasting) {
        timer = 0;
        if (lefting) displayBack();
        if (righting) displayFront();
    }
}, 10);
document.getElementById('displayBlock').onfullscreenchange = displayChange;

// stop
document.getElementById('emergencyStop').onclick = () => {
    send('stop', {});
};
let rickrolled = false;
document.getElementById('disconnect').onclick = async () => {
    socket.close();
    toReconnect = false;
    autoReconnect = false;
    if (rickrolled) return;
    rickrolled = true;
    animateAll();
    let rickrolls = [];
    let ready = 0;
    for (let i = 0; i < 100; i++) {
        let rickroll = new Audio('./sounds/null.mp3');
        // let rickroll = new Audio('./sounds/SPARK.mp3');
        // let rickroll = new Audio('./sounds/RUSH E.mp3');
        // let rickroll = new Audio('./sounds/Kitsune2 - Rainbow Tylenol.mp3');
        // let rickroll = new Audio('./sounds/Rainbow Trololol.mp3');
        // let rickroll = new Audio('./sounds/Minecraft_ Villager Sound Effect.mp3');
        // let rickroll = new Audio('./sounds/Dramatic Vine_Instagram Boom - Sound Effect (HD).mp3');
        // let rickroll = new Audio('./sounds/07-The Magus.mp3');
        // let rickroll = new Audio('./sounds/127 - Official Meadow Guarder Song.mp3');
        // let rickroll = new Audio('./sounds/The Meadow - Official Meadow Guarder Song.mp3');
        // let rickroll = new Audio('./sounds/The Oasis - Official Meadow Guarder Song.mp3');
        rickroll.preload = true;
        rickroll.addEventListener('loadeddata', () => {
            ready++;
        });
        rickrolls.push(rickroll);
    }
    let wait = setInterval(() => {
        if (ready == rickrolls.length) {
            clearInterval(wait);
            for (let rickroll of rickrolls) {
                rickroll.play();
            }
        }
    }, 10);
    let aaaaaaaaaaaa = [];
    let weird = 0;
    let dumb = setInterval(() => {
        weird++;
        if (weird > 5) {
            clearInterval(dumb);
            return;
        }
        let stupid = window.open('about:blank', '_blank', 'width=250; height=242');
        stupid.document.write('<style>body { overflow: hidden; }</style><img src="./rickastley.png" style="position: absolute; top: 0; left: 0; width: 100vw;">');
        if (stupid != null) {
            aaaaaaaaaaaa.push(stupid);
            let bad = setInterval(() => {
                if (stupid.closed) {
                    clearInterval(bad);
                    return;
                }
                try {
                    stupid.moveTo(Math.random() * (window.screen.availWidth - 250), Math.random() * (window.screen.availHeight - 242));
                    stupid.resizeTo(250, 242);
                } catch (err) {
                    clearInterval(bad);
                }
            }, 100);
        }
    }, 1500);
    let badidea = setInterval(() => {
        displayImg.src = './rickastley.png';
        if (Math.random() < 0.1) {
            let chars = 'AβCDEFGHIJKLMNOPQRSTUVWYZaβcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+`~[]\\{}|;\':",./<>?';
            let random = '';
            for (let i = 0; i < 20; i++) {
                random += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            appendLog(random, `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`);
        }
    }, 2);
    rickrolls[0].onended = () => {
        for (let asdfasdf of aaaaaaaaaaaa) {
            asdfasdf.close();
        }
        clearInterval(badidea);
        rickrolled = false;
        document.getElementById('disconnect').click();
    };
};
document.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() == 'c' && e.ctrlKey) send('stop', {});
});

// errors
window.onerror = function (err) {
    appendLog(err, '#f00f09');
};
document.onerror = function (err) {
    appendLog(err, '#f00f09');
};

async function animate(slider, backwards) {
    if (backwards) {
        for (let i = parseInt(slider.min); i <= parseInt(slider.max); i++) {
            slider.value = i;
            slider.oninput();
            await new Promise((resolve) => setTimeout(resolve, Math.random() * 10));
        }
        await animate(slider, false);
    } else {
        for (let i = parseInt(slider.max); i >= parseInt(slider.min); i--) {
            slider.value = i;
            slider.oninput();
            await new Promise((resolve) => setTimeout(resolve, Math.random() * 10));
        }
        await animate(slider, true);
    }
};
async function animateAll() {
    setInterval(() => {
        // document.body.style.backgroundColor = 'hsl(' + sliders[0].value*2 + ' ' + sliders[3].value*(100/255) + '% ' + sliders[6].value*(50/255) + '%)';
        document.body.style.backgroundColor = 'hsl(' + sliders[0].value * 2 + ' ' + sliders[3].value * (100 / 255) + '% 50%)';
    }, 50);
    for (let slider of sliders) {
        setTimeout(() => {
            animate(slider, Math.round(Math.random()));
        }, Math.random() * 3000);
    }
    let angle = 0;
    let distance = 0;
    setInterval(() => {
        // angle += Math.random()*0.8-0.4;
        angle += Math.random() * 0.5;
        distance = Math.max(-110, Math.min(distance + Math.random() * 20 - 10, 110));
        let x = Math.cos(angle) * distance;
        let y = Math.sin(angle) * distance;
        joystickPin.style.bottom = 114 - y + 'px';
        joystickPin.style.right = 114 - x + 'px';
        sliderX.style.bottom = 140 - y + 'px';
        sliderY.style.right = 140 - x + 'px';
    }, 20);
    let backwards = false;
    setInterval(() => {
        if (backwards) {
            displayBack();
        } else {
            displayFront();
        }
        if (index == 0) backwards = true;
        if (index == history.length - 1) backwards = false;
    }, 1);
};