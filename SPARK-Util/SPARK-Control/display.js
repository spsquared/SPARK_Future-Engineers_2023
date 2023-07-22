// capture display
let maxHistory = 1000;
const history = [];
const historyControls = {
    slider: document.getElementById('historySlider'),
    previousButton: document.getElementById('historyPrevious'),
    nextButton: document.getElementById('historyNext'),
    index: 0,
    back: false,
    forwards: false,
    slowmode: false,
    quickmode: false,
    maxSize: 5000,
    drawRaw: window.localStorage.getItem('hc-drawRaw') ?? true,
    drawDistances: window.localStorage.getItem('hc-drawDistances') ?? true
};
const fpsTimes = [];
let fps = 0;
const fpsDisplay = document.getElementById('fps');
const display0Img = document.getElementById('display0Img');
const display1Img = document.getElementById('display1Img');
const overlay0 = document.getElementById('display0Overlay');
const overlay1 = document.getElementById('display1Overlay');
const ctx0 = overlay0.getContext('2d');
const ctx1 = overlay1.getContext('2d');
const map = document.getElementById('map');
const mctx = map.getContext('2d');
window.onresize = () => {
    map.width = 620;
    map.height = 620;
    overlay0.width = 544;
    overlay0.height = 308;
    overlay1.width = 544;
    overlay1.height = 308;
};
window.onresize();
function addCapture(images) {
    let encoding = images[2] ? 'data:image/png;base64,' : 'data:image/jpeg;base64,';
    history.unshift({
        type: 0,
        images: [
            encoding + images[0],
            encoding + images[1]
        ],
        fps: fps
    });
    if (images[3] == 0) sounds.ding();
    if (history.length > historyControls.maxSize) history.pop();
    let scrollWith = historyControls.slider.value == historyControls.slider.max;
    historyControls.slider.max = history.length;
    if (scrollWith) {
        historyControls.slider.value = history.length;
        display();
    }
    fpsTimes.push(performance.now());
};
function addData(data) {
    let encoding = data.images[2] ? 'data:image/png;base64,' : 'data:image/jpeg;base64,';
    history.unshift({
        type: 1,
        images: [
            encoding + data.images[0],
            encoding + data.images[1]
        ],
        distances: data.distances,
        heights: data.heights,
        pos: [data.pos[0], 300 - data.pos[1], data.pos[2]],
        landmarks: data.landmarks.map((([x, y, e]) => [x, 300 - y, e])),
        rawLandmarks: data.rawLandmarks.map((([x, y, e]) => [x, 300 - y, e])),
        blobs: data.blobs,
        steering: data.steering,
        waypoints: data.waypoints,
        fps: fps,
    });
    if (data.images[3] == 0) sounds.ding();
    if (history.length > historyControls.maxSize) history.pop();
    let scrollWith = historyControls.slider.value == historyControls.slider.max;
    historyControls.slider.max = history.length;
    if (scrollWith) {
        historyControls.slider.value = history.length;
        display();
    }
    fpsTimes.push(performance.now());
};
const carConstants = {
    wallStarts: [164, 154]
};
function display() {
    const data = history[historyControls.index];
    if (data === undefined) return;
    display0Img.src = data.images[0];
    display1Img.src = data.images[1];
    if (data.type == 1) {
        drawOverlays(data);
        mctx.resetTransform();
        mctx.clearRect(0, 0, 620, 620);
        mctx.translate(10, 10);
        mctx.scale(2, 2);
        mctx.globalAlpha = 1;
        drawLandmarks(data.landmarks);
        if (historyControls.drawRaw) drawRawLandmarks();
        drawDistances(data.distances, data.pos);
        drawCar(data.pos);
    }
};
function drawOverlays(data) {
    function draw(camera, ctx) {
        let wallStart = carConstants.wallStarts[camera] + 1;
        ctx.clearRect(0, 0, 544, 308);
        ctx.globalAlpha = 0.5;
        ctx.fillStyle = 'rgb(255, 255, 255)';
        for (let i in data.heights[camera]) {
            ctx.fillRect(i, wallStart, 1, data.heights[camera][i]);
        }
        ctx.fillStyle = 'rgb(255, 0, 0)';
        for (let i in data.blobs[camera][0]) {
            ctx.fillRect(data.blobs[camera][1][i][0], wallStart, 1, data.heights[camera][i])
        }
        ctx.fillStyle = 'rgb(0, 255, 0)';
        for (let i in data.blobs[camera][1]) {
            ctx.fillRect(data.blobs[camera][1][i][0], wallStart, 1, data.heights[camera][i])
        }
        ctx.globalAlpha = 0.2;
        ctx.fillStyle = 'rgb(255, 0, 0)';
        for (let i in data.blobs[camera][0]) {
            ctx.fillRect(data.blobs[camera][1][i][0] - data.blobs[camera][1][i][1], wallStart, data.blobs[camera][1][i][1] * 2 + 1, data.heights[camera][i]);
        }
        ctx.fillStyle = 'rgb(0, 255, 0)';
        for (let i in data.blobs[camera][1]) {
            ctx.fillRect(data.blobs[camera][1][i][0] - data.blobs[camera][1][i][1], wallStart, data.blobs[camera][1][i][1] * 2 + 1, data.heights[camera][i]);
        }
    };
    draw(0, ctx0);
    draw(1, ctx1);
};
function drawLandmarks(landmarks) {
    // draw outer walls
    mctx.setLineDash([]);
    mctx.strokeStyle = 'rgb(80, 80, 80)';
    mctx.lineWidth = 10;
    mctx.strokeRect(-5, -5, 310, 310);
    // draw inner walls
    mctx.beginPath();
    mctx.lineCap = 'square';
    mctx.moveTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    if (landmarks[4][2]) mctx.lineTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    if (landmarks[5][2]) mctx.lineTo(landmarks[5][0] - 5, landmarks[5][1] + 5);
    if (landmarks[6][2]) mctx.lineTo(landmarks[6][0] - 5, landmarks[6][1] - 5);
    if (landmarks[7][2]) mctx.lineTo(landmarks[7][0] + 5, landmarks[7][1] - 5);
    if (landmarks[4][2]) mctx.lineTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    mctx.stroke();
    // draw red pillars
    mctx.fillStyle = 'rgb(238, 39, 55)';
    for (let i = 8; i < 16; i++) {
        mctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw green pillars
    mctx.fillStyle = 'rgb(68, 214, 44)';
    for (let i = 16; i < 24; i++) {
        mctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw landmark POI "dots"
    mctx.fillStyle = 'rgb(255, 255, 255)';
    for (let landmark of landmarks) {
        if (landmark[2]) mctx.fillRect(landmark[0] - 1, landmark[1] - 1, 2, 2);
    }
};
function drawRawLandmarks(rawLandmarks) {
    mctx.globalAlpha = 0.5;
    drawLandmarks(rawLandmarks);
};
function drawCar(pos, steering) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[3]);
    mctx.fillStyle = 'rgb(50, 50, 50)';
    mctx.fillRect(-12, -6.65, 24, 13.3);
    mctx.restore();
};
function drawDistances(distances, pos) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[3]);
    mctx.globalAlpha = 1;
    mctx.fillStyle = 'rgb(255, 255, 255)';
    mctx.beginPath();
    for (let dist of distances) {
        mctx.fillRect(Math.round(dist[0] - 1), Math.round(dist[1] - 1), 3, 3);
        mctx.moveTo(dist[0], dist[1]);
        mctx.lineTo(0, 0);
    }
    mctx.globalAlpha = 0.2;
    mctx.setLineDash([2, 2]);
    mctx.restore();
};
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    fps = fpsTimes.length;
    fpsDisplay.innerText = 'FPS: ' + fps;
}, 50);

// controls 0
const hcDrawRaw = document.getElementById('hcDrawRaw');
hcDrawRaw.addEventListener('click', (e) => {
    historyControls.drawRaw = hcDrawRaw.checked;
    window.localStorage.setItem('hc-drawRaw', historyControls.drawRaw);
});
const hcDrawDistances = document.getElementById('hcDrawDistances');
hcDrawDistances.addEventListener('click', (e) => {
    historyControls.drawDistances = hcDrawDistances.checked;
    window.localStorage.setItem('hc-drawDistances', historyControls.drawDistances);
});
hcDrawRaw.checked = historyControls.drawRaw;
hcDrawDistances.checked = historyControls.drawDistances;

// controls
historyControls.slider.oninput = (e) => {
    historyControls.index = history.length - parseInt(historyControls.slider.value);
    display();
};
historyControls.nextButton.onclick = (e) => {
    historyControls.index = Math.max(0, historyControls.index - 1);
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
historyControls.previousButton.onclick = (e) => {
    historyControls.index = Math.min(history.length - 1, historyControls.index + 1);
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
function exportSession() {
    const data = 'data:text/json;charset=UTF-8,' + encodeURIComponent(JSON.stringify(history));
    const a = document.createElement('a');
    a.href = data;
    let current = new Date();
    a.download = `SPARK-data_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.json`;
    a.click();
};
function importSession() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.click();
    input.oninput = () => {
        let files = input.files;
        if (files.length == 0) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            let raw = JSON.parse(e.target.result);
            history.length = 0;
            for (let i in raw) {
                history.push(raw[i]);
            }
            historyControls.slider.max = history.length;
            historyControls.slider.value = history.length;
            sounds.ping();
            display();
        };
        reader.readAsText(files[0]);
    };
};
document.getElementById('importSession').onclick = importSession;
document.getElementById('exportSession').onclick = exportSession;
document.addEventListener('keydown', (e) => {
    if (e.key == 'ArrowLeft') {
        historyControls.back = true;
    } else if (e.key == 'ArrowRight') {
        historyControls.forwards = true;
    } else if (e.key == 'Control') {
        historyControls.quickmode = true;
    } else if (e.key == 'Shift') {
        historyControls.slowmode = true;
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
        historyControls.back = false;
    } else if (e.key == 'ArrowRight') {
        historyControls.forwards = false;
    } else if (e.key == 'Control') {
        historyControls.quickmode = false;
    } else if (e.key == 'Shift') {
        historyControls.slowmode = false;
    }
});
historyControls.slider.onkeydown = (e) => {
    historyControls.slider.blur()
};
let timer = 0;
setInterval(() => {
    timer = (timer + 1) % 20;
    if (historyControls.slowmode && timer % 20 != 0) return;
    if (!historyControls.quickmode && timer % 10 != 0) return;
    if (historyControls.back && historyControls.forwards) return;
    if (historyControls.back) {
        historyControls.previousButton.onclick();
        sounds.tick();
    } else if (historyControls.forwards) {
        historyControls.nextButton.onclick();
        sounds.tick();
    }
}, 10);
socket.on('capture', addCapture); // 0 is jpeg, 1 is png
socket.on('data', addData);

// controls 2: electric boogaloo
const streamModSave = document.getElementById('streamModSave');
const streamModFilter = document.getElementById('streamModFilter');
const captureModSave = document.getElementById('captureModSave');
const captureModFilter = document.getElementById('captureModFilter');
const stream = document.getElementById('stream');
const capture = document.getElementById('capture');
const rawcapture = document.getElementById('rawCapture');
const streamToggle = document.getElementById('streamToggle');
socket.on('streamState', (state) => {
    streamToggle.checked = state[0];
    streamModFilter.checked = state[1];
    streamModSave.checked = state[2];
    if (streamToggle.checked) {
        stream.style.backgroundColor = 'red';
        stream.style.borderColor = 'firebrick';
        stream.innerText = 'STOP STREAM';
        streamModFilter.disabled = true;
        streamModSave.disabled = true;
        sounds.start();
    } else {
        stream.style.backgroundColor = '';
        stream.style.borderColor = '';
        stream.innerText = 'START STREAM';
        streamModFilter.disabled = false;
        streamModSave.disabled = false;
        sounds.stop();
    }
});
stream.onclick = () => {
    streamToggle.checked = !streamToggle.checked;
    socket.emit('stream', { save: streamModSave.checked, filter: streamModFilter.checked, colors: getColors() });
};
capture.onclick = () => {
    socket.emit('capture', { save: captureModSave.checked, filter: captureModFilter.checked, colors: getColors() });
};
rawcapture.onclick = () => {
    socket.emit('rawCapture');
};
stream.disabled = true;
capture.disabled = true;
rawcapture.disabled = true;