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
    maxSize: 5000
};
const fpsTimes = [];
let fps = 0;
const fpsDisplay = document.getElementById('fps');
const display0Img = document.getElementById('display0Img');
const display1Img = document.getElementById('display1Img');
const map = document.getElementById('map');
const ctx = map.getContext('2d');
map.width = 620;
map.height = 620;
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
    if (images[3] == 0) sounds.ping();
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
        distances: [],
        pos: [data.pos[0], 300 - data.pos[1], data.pos[2]],
        landmarks: data.landmarks.map((([x, y, e]) => [x, 300 - y, e])),
        rawLandmarks: data.rawLandmarks.map((([x, y, e]) => [x, 300 - y, e])),
        blobs: data.blobs,
        fps: fps
    });
    if (data.images[3] == 0) sounds.ping();
    if (history.length > historyControls.maxSize) history.pop();
    let scrollWith = historyControls.slider.value == historyControls.slider.max;
    historyControls.slider.max = history.length;
    if (scrollWith) {
        historyControls.slider.value = history.length;
        display();
    }
    fpsTimes.push(performance.now());
};
function display() {
    const data = history[historyControls.index];
    if (data === undefined) return;
    display0Img.src = data.images[0];
    display1Img.src = data.images[1];
    if (data.type == 1) {
        ctx.resetTransform();
        ctx.translate(10, 10);
        ctx.scale(2, 2);
        drawLandmarks(data.landmarks);
        drawCar(data.pos);
    }
};
function drawLandmarks(landmarks) {
    // draw outer walls
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgb(80, 80, 80)';
    ctx.lineWidth = 10;
    ctx.strokeRect(-5, -5, 310, 310);
    // draw inner walls
    ctx.beginPath();
    ctx.lineCap = 'square';
    ctx.moveTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    if (landmarks[4][2]) ctx.lineTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    if (landmarks[5][2]) ctx.lineTo(landmarks[5][0] - 5, landmarks[5][1] + 5);
    if (landmarks[6][2]) ctx.lineTo(landmarks[6][0] - 5, landmarks[6][1] - 5);
    if (landmarks[7][2]) ctx.lineTo(landmarks[7][0] + 5, landmarks[7][1] - 5);
    if (landmarks[4][2]) ctx.lineTo(landmarks[4][0] + 5, landmarks[4][1] + 5);
    ctx.stroke();
    // draw red pillars
    ctx.fillStyle = 'rgb(238, 39, 55)';
    for (let i = 8; i < 16; i++) {
        ctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw green pillars
    ctx.fillStyle = 'rgb(68, 214, 44)';
    for (let i = 16; i < 24; i++) {
        ctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw landmark POI "dots"
    ctx.fillStyle = 'rgb(255, 255, 255)';
    for (let landmark of landmarks) {
        if (landmark[2]) ctx.fillRect(landmark[0] - 1, landmark[1] - 1, 2, 2);
    }
};
function drawRawLandmarks(rawLandmarks) {
    // probably change some other stuff, maybe dont fill pillars and make walls dashed
    ctx.opacity = 0.5;
    drawLandmarks(rawLandmarks);
};
function drawCar(pos) {
    ctx.save();
    ctx.translate(pos[0], pos[1]);
    ctx.rotate(pos[3]);
    ctx.fillStyle = 'rgb(50, 50, 50)';
    ctx.fillRect(-6.65, -12, 13.3, 24);
    ctx.restore();
};
function drawBlobs(blobs) {

};
function drawDistances(distances) {

};

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
            display();
        };
        reader.readAsText(files[0]);
    };
};
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    fps = fpsTimes.length;
    fpsDisplay.innerText = 'FPS: ' + fps;
}, 50);
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
    timer = (timer + 1) % 8;
    if (historyControls.slowmode && timer % 8 != 0) return;
    if (!historyControls.quickmode && timer % 4 != 0) return;
    if (historyControls.back) historyControls.previousButton.onclick();
    if (historyControls.forwards) historyControls.nextButton.onclick();
}, 25);
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
    } else {
        stream.style.backgroundColor = '';
        stream.style.borderColor = '';
        stream.innerText = 'START STREAM';
        streamModFilter.disabled = false;
        streamModSave.disabled = false;
    }
    sounds.shortDing();
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

// addData({
//     images: ['', ''],
//     landmarks: [
//         [0, 0, true],
//         [300, 0, true],
//         [0, 300, true],
//         [300, 300, true],
//         [60, 100, true],
//         [60, 200, true],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, true],
//         [0, 0, true],
//         [0, 0, true],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, true],
//         [0, 0, true],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//         [0, 0, false],
//     ],
//     rawLandmarks: [],
//     pos: [260, 160, 0]
// });