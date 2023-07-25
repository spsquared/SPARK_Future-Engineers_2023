// capture display
let maxHistory = 1000;
const history = [];
const historyControls = {
    slider: document.getElementById('historySlider'),
    previousButton: document.getElementById('historyPrevious'),
    nextButton: document.getElementById('historyNext'),
    index: 0,
    back: false,
    forward: false,
    slowmode: false,
    quickmode: false,
    maxSize: 5000,
    drawOverlays: window.localStorage.getItem('hc-drawOverlays') ?? true,
    drawRaw: window.localStorage.getItem('hc-drawRaw') ?? true,
    drawDistances: window.localStorage.getItem('hc-drawDistances') ?? true,
    drawWaypoints: window.localStorage.getItem('hc-drawWaypoints') ?? true,
    rawDump: false
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
const carImg = new Image();
carImg.src = './assets/car.png';
window.onresize = () => {
    map.width = 620;
    map.height = 620;
    overlay0.width = 544;
    overlay0.height = 308;
    overlay1.width = 544;
    overlay1.height = 308;
    display();
};
window.onresize();
function addCapture(images) {
    let encoding = images[2] ? 'data:image/png;base64,' : 'data:image/jpeg;base64,';
    history.unshift({
        type: 0,
        images: [
            encoding + images[0],
            encoding + images[1],
            images[3] ?? 0
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
            encoding + data.images[1],
            data.images[3]
        ],
        distances: data.distances,
        heights: data.heights,
        pos: [data.pos[0], 300 - data.pos[1], data.pos[2]],
        landmarks: data.landmarks.map((([x, y, t, f, d]) => [x, 300 - y, f])),
        rawLandmarks: [data.rawLandmarks[0].map(([x, y, d, a, c]) => [x, -y]), data.rawLandmarks[1].map(([x, y, d, a, c]) => [x, -y]), data.rawLandmarks[2].map(([l, h, c]) => [l[0], -l[1]])],
        contours: data.contours,
        wallLines: data.wallLines,
        walls: [data.walls[0].map(([x, y, d, a]) => [x, -y]), data.walls[1].map(([l0, l1]) => [l0[0], -l0[1], l1[0], -l1[1]]), (data.walls[2] ?? []).map(([t, d, a]) => t)],
        steering: Math.min(100, Math.max(-100, data.steering)),
        waypoints: [data.waypoints[0].map(([x, y]) => [x, -y]), [data.waypoints[1][0], -data.waypoints[1][1]], data.waypoints[2]],
        rawDump: data.raw,
        fps: fps
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
    wallStarts: [164, 154],
    undistortedWallStarts: [166, 160],
    undistortCrop: 140
};
function display() {
    const data = history[historyControls.index];
    if (data === undefined) return;
    display0Img.src = data.images[0];
    display1Img.src = data.images[1];
    if (data.type == 1) {
        ctx0.clearRect(0, 0, 544, 308);
        ctx1.clearRect(0, 0, 544, 308);
        if (historyControls.drawOverlays) drawOverlays(data);
        mctx.resetTransform();
        mctx.clearRect(0, 0, 620, 620);
        mctx.translate(10, 10);
        mctx.scale(2, 2);
        mctx.globalAlpha = 1;
        drawLandmarks(data.landmarks);
        if (historyControls.drawRaw) drawRawLandmarks(data.rawLandmarks, data.pos);
        if (historyControls.drawDistances) {
            drawDistances(data.distances, data.pos);
            drawWalls(data.walls, data.pos);
        }
        if (historyControls.drawWaypoints) drawWaypoints(data.waypoints, data.pos);
        drawCar(data.pos, data.steering);
        if (historyControls.rawDump) appendLog(JSON.stringify(data.rawDump), 'skyblue');
    } else {
        ctx0.clearRect(0, 0, 544, 308);
        ctx1.clearRect(0, 0, 544, 308);
        mctx.resetTransform();
        mctx.clearRect(0, 0, 620, 620);
    }
};
// debug displays
// screen-space overlays
function drawOverlays(data) {
    function draw(camera, ctx) {
        let wallStart = (data.images[2] ? carConstants.undistortedWallStarts[camera] - carConstants.undistortCrop : carConstants.wallStarts[camera]) + 1;
        ctx.globalAlpha = 0.5;
        // wall heights
        ctx.fillStyle = 'rgb(255, 255, 255)';
        for (let i in data.heights[camera]) {
            ctx.fillRect(i, wallStart, 1, data.heights[camera][i]);
        }
        ctx.globalAlpha = 1;
        // contours and contour areas
        ctx.fillStyle = 'rgb(255, 0, 0)';
        for (let i in data.contours[camera][0]) {
            ctx.fillRect(data.contours[camera][0][i][0], 0, 1, 308);
        }
        ctx.fillStyle = 'rgb(0, 255, 0)';
        for (let i in data.contours[camera][1]) {
            ctx.fillRect(data.contours[camera][1][i][0], 0, 1, 308);
        }
        ctx.globalAlpha = 0.4;
        ctx.fillStyle = 'rgb(255, 0, 0)';
        for (let i in data.contours[camera][0]) {
            ctx.fillRect(data.contours[camera][0][i][0] - data.contours[camera][0][i][1], 0, data.contours[camera][0][i][1] * 2 + 1, 308);
        }
        ctx.fillStyle = 'rgb(0, 255, 0)';
        for (let i in data.contours[camera][1]) {
            ctx.fillRect(data.contours[camera][1][i][0] - data.contours[camera][1][i][1], 0, data.contours[camera][1][i][1] * 2 + 1, 308);
        }
        if (data.wallLines != undefined) {
            // wall lines
            ctx.setLineDash([]);
            ctx.strokeStyle = 'rgb(255, 0, 255)'; // spink
            ctx.lineWidth = 3;
            ctx.beginPath();
            for (let houghLine of data.wallLines[camera]) {
                ctx.moveTo(houghLine[0], houghLine[1] + wallStart);
                ctx.lineTo(houghLine[2], houghLine[3] + wallStart);
            }
            ctx.stroke();
        }
    };
    draw(0, ctx0);
    draw(1, ctx1);
};
// SLAM landmarks + car - absolute positioning
function drawLandmarks(landmarks) {
    // draw outer walls
    mctx.globalAlpha = 1;
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
        if (landmarks[i][2]) mctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw green pillars
    mctx.fillStyle = 'rgb(68, 214, 44)';
    for (let i = 16; i < 24; i++) {
        if (landmarks[i][2]) mctx.fillRect(landmarks[i][0] - 2.5, landmarks[i][1] - 2.5, 5, 5);
    }
    // draw landmark POI "dots"
    mctx.fillStyle = 'rgb(255, 255, 255)';
    for (let landmark of landmarks) {
        if (landmark[2]) mctx.fillRect(landmark[0] - 1, landmark[1] - 1, 2, 2);
    }
};
function drawCar(pos, steering) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[2]);
    mctx.globalAlpha = 1;
    mctx.setLineDash([]);
    mctx.strokeStyle = 'rgb(255, 255, 255)';
    mctx.lineWidth = 0.5;
    // definitely didn't calculate the steering angle for each wheel
    mctx.beginPath();
    mctx.moveTo(0, 3.4);
    mctx.lineTo(-Math.sin(steering * 0.45 * Math.PI / 180) * 30, -Math.cos(steering * 0.45 * Math.PI / 180) * 30);
    mctx.stroke();
    mctx.drawImage(carImg, -6.25, -10, 12.5, 24);
    mctx.restore();
};
// raw data - relative positioning
function drawRawLandmarks(rawLandmarks, pos) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[2]);
    mctx.globalAlpha = 1;
    mctx.setLineDash([]);
    mctx.lineWidth = 1;
    // draw wall things
    mctx.fillStyle = 'rgb(0, 0, 255)';
    for (let landmark of rawLandmarks[2]) {
        mctx.fillRect(landmark[0] - 1, landmark[1] - 1, 2, 2);
    }
    // draw red pillars
    mctx.strokeStyle = 'rgb(255, 0, 0)';
    for (let landmark of rawLandmarks[0]) {
        mctx.strokeRect(landmark[0] - 2.5, landmark[1] - 2.5, 5, 5);
    }
    // draw green pillars
    mctx.strokeStyle = 'rgb(0, 255, 0)';
    for (let landmark of rawLandmarks[1]) {
        mctx.strokeRect(landmark[0] - 2.5, landmark[1] - 2.5, 5, 5);
    }
    mctx.restore();
};
function drawWalls(walls, pos) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[2]);
    mctx.globalAlpha = 1;
    mctx.setLineDash([]);
    mctx.strokeStyle = 'rgb(255, 160, 0)';
    mctx.lineWidth = 1;
    mctx.font = '12px monospace';
    mctx.fillStyle = 'rgb(255, 255, 255';
    mctx.textAlign = 'center';
    mctx.textBaseline = 'middle';
    mctx.beginPath();
    let labels = ['?', 'L', 'C', 'R'];
    for (let i in walls[1]) {
        mctx.moveTo(walls[1][i][0], walls[1][i][1]);
        mctx.lineTo(walls[1][i][2], walls[1][i][3]);
        if (walls[2][i] != undefined) {
            mctx.fillText(labels[walls[2][i] + 1], (walls[1][i][0] + walls[1][i][2]) / 2, (walls[1][i][1] + walls[1][i][3]) / 2);
        }
    }
    mctx.stroke();
    mctx.fillStyle = 'rgb(255, 255, 0)';
    for (let corner of walls[0]) {
        mctx.fillRect(corner[0] - 1, corner[1] - 1, 2, 2);
    }
    mctx.restore();
};
function drawDistances(distances, pos) {
    mctx.save();
    mctx.translate(pos[0], pos[1]);
    mctx.rotate(pos[2]);
    mctx.globalAlpha = 0.5;
    mctx.setLineDash([]);
    mctx.strokeStyle = 'rgb(255, 255, 255)';
    mctx.fillStyle = 'rgb(255, 255, 255)';
    mctx.lineWidth = 1;
    mctx.beginPath();
    for (let dist of distances) {
        mctx.fillRect(Math.round(dist[0] - 1), Math.round(dist[1] - 1), 3, 3);
        mctx.moveTo(dist[0], dist[1]);
        mctx.lineTo(0, 0);
    }
    mctx.globalAlpha = 0.2;
    mctx.setLineDash([2, 2]);
    mctx.stroke();
    mctx.restore();
};
// waypoints - both (SLAM uses absolute but simple uses relative)
function drawWaypoints(waypoints, pos) {
    if (waypoints[2]) {
        mctx.save();
        mctx.translate(pos[0], pos[1]);
        mctx.rotate(pos[2]);
    }
    mctx.globalAlpha = 1;
    mctx.setLineDash([]);
    mctx.strokeStyle = 'rgb(0, 255, 255)';
    mctx.fillStyle = 'rgb(0, 255, 255)';
    mctx.lineWidth = 0.5;
    mctx.beginPath();
    if (waypoints[0].length > 0) {
        mctx.moveTo(waypoints[0][0], waypoints[0][1]);
        for (let waypoint of waypoints[0]) {
            mctx.lineTo(waypoint[0], waypoint[1]);
            mctx.fillRect(waypoint[0] - 1, waypoint[1] - 1, 2, 2);
        }
    }
    mctx.fillRect(waypoints[1][0] - 2, waypoints[1][1] - 2, 4, 4);
    mctx.moveTo(waypoints[1][0], waypoints[1][1]);
    if (waypoints[2]) mctx.lineTo(0, 0);
    else mctx.lineTo(pos[0], pos[1]);
    mctx.stroke();
    if (waypoints[2]) {
        mctx.restore();
    }
};
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    fps = fpsTimes.length;
    fpsDisplay.innerText = 'FPS: ' + fps;
}, 50);

// controls 0
const hcDrawOverlays = document.getElementById('hcDrawOverlays');
hcDrawOverlays.addEventListener('click', (e) => {
    historyControls.drawOverlays = hcDrawOverlays.checked;
    window.localStorage.setItem('hc-drawOverlays', historyControls.drawOverlays);
    display();
});
const hcDrawRaw = document.getElementById('hcDrawRaw');
hcDrawRaw.addEventListener('click', (e) => {
    historyControls.drawRaw = hcDrawRaw.checked;
    window.localStorage.setItem('hc-drawRaw', historyControls.drawRaw);
    display();
});
const hcDrawDistances = document.getElementById('hcDrawDistances');
hcDrawDistances.addEventListener('click', (e) => {
    historyControls.drawDistances = hcDrawDistances.checked;
    window.localStorage.setItem('hc-drawDistances', historyControls.drawDistances);
    display();
});
const hcDrawWaypoints = document.getElementById('hcDrawWaypoints');
hcDrawWaypoints.addEventListener('click', (e) => {
    historyControls.drawWaypoints = hcDrawWaypoints.checked;
    window.localStorage.setItem('hc-drawWaypoints', historyControls.drawWaypoints);
    display();
});
const hcRawDump = document.getElementById('hcRawDump');
hcRawDump.addEventListener('click', (e) => {
    historyControls.rawDump = hcRawDump.checked;
    display();
});
hcDrawOverlays.checked = historyControls.drawOverlays;
hcDrawRaw.checked = historyControls.drawRaw;
hcDrawDistances.checked = historyControls.drawDistances;
hcDrawWaypoints.checked = historyControls.drawWaypoints;
hcRawDump.checked = historyControls.rawDump;

// controls
historyControls.slider.oninput = (e) => {
    historyControls.index = history.length - parseInt(historyControls.slider.value);
    display();
};
historyControls.nextButton.onclick = (e) => {
    if (historyControls.index == 0) return;
    historyControls.index--;
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
historyControls.previousButton.onclick = (e) => {
    if (historyControls.index == history.length - 1) return;
    historyControls.index++;
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
function downloadFrame() {
    const render = document.createElement('canvas');
    render.width = 1088;
    render.height = 308;
    const rctx = render.getContext('2d');
    rctx.drawImage(display0Img, 0, 0);
    rctx.drawImage(display1Img, 544, 0);
    rctx.drawImage(overlay0, 0, 0);
    rctx.drawImage(overlay1, 544, 0);
    const a = document.createElement('a');
    a.href = render.toDataURL('image/png');
    let current = new Date();
    a.download = `SPARK-img_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.png`;
    a.click();
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
document.getElementById('downloadFrame').onclick = downloadFrame;
document.getElementById('importSession').onclick = importSession;
document.getElementById('exportSession').onclick = exportSession;
document.addEventListener('keydown', (e) => {
    if (e.key == 'ArrowLeft') {
        historyControls.back = true;
    } else if (e.key == 'ArrowRight') {
        historyControls.forward = true;
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
        historyControls.forward = false;
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
    if (historyControls.back && historyControls.forward) return;
    if (historyControls.back) {
        if (historyControls.index == history.length - 1) return;
        historyControls.previousButton.onclick();
        sounds.tick();
    } else if (historyControls.forward) {
        if (historyControls.index == 0) return;
        historyControls.nextButton.onclick();
        sounds.tick();
    }
}, 10);
hasFocus = false;
if (typeof window.requestIdleCallback == 'function') {
    setInterval(() => {
        window.requestIdleCallback(() => {
            if (hasFocus && !document.hasFocus()) {
                historyControls.slowmode = false;
                historyControls.quickmode = false;
                historyControls.back = false;
                historyControls.forward = false;
            }
            hasFocus = document.hasFocus();
        }, { timeout: 40 });
    }, 50);
} else {
    setInterval(() => {
        if (hasFocus && !document.hasFocus()) {
            historyControls.slowmode = false;
            historyControls.quickmode = false;
            historyControls.back = false;
            historyControls.forward = false;
        }
        hasFocus = document.hasFocus();
    }, 50);
}
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