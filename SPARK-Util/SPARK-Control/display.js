

// capture display
let maxHistory = 1000;
let historyIndex = 0;
const history = [];
const historyControls = {
    back: false,
    forwards: false,
    slowmode: false,
    quickmode: false,
};
const fpsTimes = [];
const displayImg = document.getElementById('displayImg');
const FPS = document.getElementById('fps');
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
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    // FPS.innerHTML = 'FPS: ' + fpsTimes.length;
}, 1000);
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
document.getElementById('displayBlock').onfullscreenchange = displayChange;
socket.on('capture', (images) => console.log(images));
socket.on('data', () => 'idk');