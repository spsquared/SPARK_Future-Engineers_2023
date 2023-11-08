const log = document.getElementById('log');
function appendLog(text, color, clean = true) {
    const div = document.createElement('div');
    div.classList.add('logBlock');
    if (clean) div.innerHTML = text;
    else div.innerText = text;
    div.style.backgroundColor = color ?? '';
    let scroll = false;
    if (log.scrollTop + log.clientHeight >= log.scrollHeight - 5) scroll = true;
    log.appendChild(div);
    if (scroll) log.scrollTop = log.scrollHeight;
};
window.addEventListener('error', (e) => {
    appendLog(`<strong>[LOCAL]</strong> An error occured:<br>${e.message}<br>${e.filename} ${e.lineno}:${e.colno}`, 'red');
    sounds.ping();
});

// autogenerating toggles
let toggleGens = document.querySelectorAll('.generateToggle');
for (const div of toggleGens) {
    if (div.hasAttribute('toggleLabel')) {
        const label = document.createElement('label');
        label.innerHTML = div.getAttribute('toggleLabel');
        div.appendChild(label);
    }
    const toggleLabel = document.createElement('label');
    toggleLabel.classList.add('toggle');
    const toggleInput = document.createElement('input');
    toggleInput.type = 'checkbox';
    toggleInput.id = div.getAttribute('toggleID');
    toggleInput.classList.add('toggleInput');
    toggleLabel.appendChild(toggleInput);
    const toggleSlider = document.createElement('span');
    toggleSlider.classList.add('toggleSlider');
    toggleLabel.appendChild(toggleSlider);
    div.appendChild(toggleLabel);
}

const initcolors = [
    [
        [22, 255, 125],
        [0, 0, 70]
    ],
    [
        [115, 255, 255],
        [50, 0, 30]
    ],
];

appendLog('Connecting...');
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
    appendLog('Connected!', 'lime');
    runManual.disabled = false;
    runAuto.disabled = false;
    runStop.disabled = true;
    statusConnected.style.filter = 'brightness(1)';
    sounds.connect();
});
socket.on('idManual', () => {
    stream.disabled = false;
    capture.disabled = false;
    predict.disabled = false;
    resetPredictor.disabled = false;
    filterApply.disabled = false;
});
socket.on('#programStarting', (mode) => {
    appendLog('Running program - ' + mode);
    runManual.disabled = true;
    runAuto.disabled = true;
    statusRunning.style.animationName = 'blink';
    document.querySelectorAll('.killPrograms').forEach(button => button.remove());
});
socket.on('#programRunning', () => {
    appendLog('Program running', 'lime');
    runManual.disabled = true;
    runAuto.disabled = true;
    runStop.disabled = false;
    statusRunning.style.animationName = 'blink';
    document.querySelectorAll('.killPrograms').forEach(button => button.remove());
    socket.emit('getStreamState');
    socket.emit('getColors');
    socket.emit('idManual');
    sounds.connect();
});
socket.on('#programStopped', () => {
    appendLog('Program stopped', 'red');
    stream.disabled = true;
    capture.disabled = true;
    predict.disabled = true;
    resetPredictor.disabled = true;
    filterApply.disabled = true;
    runManual.disabled = false;
    runAuto.disabled = false;
    runStop.disabled = true;
    statusRunning.style.animationName = '';
    statusError.style.animationName = '';
    sounds.disconnect();
});
socket.on('#programAlreadyRunning', () => {
    document.querySelectorAll('.killPrograms').forEach(button => button.remove());
    appendLog('Program already running!<button class="killPrograms" onclick="socket.emit(\'#killPrograms\');">KILL</button>');
});
socket.on('#killedPrograms', () => {
    document.querySelectorAll('.killPrograms').forEach(button => button.remove());
    appendLog('Programs killed', 'red');
    stream.disabled = true;
    capture.disabled = true;
    predict.disabled = true;
    resetPredictor.disabled = true;
    filterApply.disabled = true;
    runManual.disabled = false;
    runAuto.disabled = false;
    runStop.disabled = true;
    statusRunning.style.animationName = '';
    statusError.style.animationName = '';
    sounds.stop();
});
let onDisconnect = () => {
    connected = false;
    if (autoReconnect) toReconnect = true;
    appendLog('Connection closed<button class="connectNow" onclick="reconnect(true);">RECONNECT NOW</button>', 'red');
    setTimeout(reconnect, 10000);
    stream.disabled = true;
    capture.disabled = true;
    predict.disabled = true;
    resetPredictor.disabled = true;
    filterApply.disabled = true;
    runManual.disabled = true;
    runAuto.disabled = true;
    runStop.disabled = true;
    statusConnected.style.filter = 'brightness(0.5)';
    statusRunning.style.animationName = '';
    statusError.style.animationName = '';
    sounds.disconnect();
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
        if (autoReconnect) toReconnect = true;
        appendLog('Connection failed<button class="connectNow" onclick="reconnect(true);">RECONNECT NOW</button>', 'red');
        setTimeout(reconnect, 10000);
    };
    req.send();
};
window.addEventListener('load', connect);

// log
socket.on('message', (msg) => {
    appendLog(msg);
    sounds.ding();
});
socket.on('unsafemessage', (msg) => {
    appendLog(msg, clean = false);
    sounds.ding();
});
socket.on('programError', (err) => {
    appendLog(`<strong>[REMOTE]</strong> An error occured:<br>${err}`, 'red');
    statusError.style.animationName = 'flash';
    sounds.ping();
});

// manual driving
const controls = {
    forward: 0,
    backward: 0,
    left: 0,
    right: 0,
    throttle: 0,
    steering: 0,
    updated: false
};
document.onkeydown = function (e) {
    switch (e.key.toLowerCase()) {
        case 'w':
            controls.forward = 100;
            controls.updated = true;
            break;
        case 's':
            controls.backward = -100;
            controls.updated = true;
            break;
        case 'a':
            controls.left = -100;
            controls.updated = true;
            break;
        case 'd':
            controls.right = 100;
            controls.updated = true;
            break;
    }
};
document.onkeyup = function (e) {
    switch (e.key.toLowerCase()) {
        case 'w':
            controls.forward = 0;
            controls.updated = true;
            break;
        case 's':
            controls.backward = 0;
            controls.updated = true;
            break;
        case 'a':
            controls.left = 0;
            controls.updated = true;
            break;
        case 'd':
            controls.right = 0;
            controls.updated = true;
            break;
    }
};
let pressedbuttons = new Set();
function updateControllers() {
    let controllers = navigator.getGamepads();
    for (let i in controllers) {
        if (controllers[i] instanceof Gamepad) {
            let controller = controllers[i];
            let lastthrottle = controls.throttle;
            let laststeering = controls.steering;
            controls.throttle = Math.abs(controller.axes[1]) < 0.05 ? 0 : Math.round(controller.axes[1] * -100);
            controls.steering = Math.abs(controller.axes[2]) < 0.1 ? 0 :Math.round(controller.axes[2] * 100);
            // yeah this is all useless
            // updateButtonState(controller.buttons, 0, () => captureModFilter.checked = !captureModFilter.checked);
            // updateButtonState(controller.buttons, 1, () => captureModSave.checked = !captureModSave.checked);
            // updateButtonState(controller.buttons, 2, () => streamModFilter.checked = !streamModFilter.checked);
            // updateButtonState(controller.buttons, 3, () => streamModSave.checked = !streamModSave.checked);
            // updateButtonState(controller.buttons, 8, () => capture.click());
            // updateButtonState(controller.buttons, 9, () => stream.click());
            if (lastthrottle != controls.throttle || laststeering != controls.steering) controls.updated = true;
            break;
        }
    }
};
function updateButtonState(buttons, b, onpress, onrelease) {
    if (buttons[b].pressed && !pressedbuttons.has(b)) {
        pressedbuttons.add(b);
        typeof onpress == 'function' && onpress();
    } else if (!buttons[b].pressed && pressedbuttons.has(b)) {
        pressedbuttons.delete(b);
        typeof onrelease == 'function' && onrelease();
    }
};
setInterval(function () {
    updateControllers();
    if (controls.updated) {
        if (controls.throttle != 0 || controls.steering != 0) {
            socket.emit('drive', { throttle: controls.throttle, steering: controls.steering });
        } else {
            socket.emit('drive', { throttle: controls.forward + controls.backward, steering: controls.left + controls.right });
        }
        controls.updated = false;
    }
}, 50);

// filter adjuster
let sliders = [];
const filterAdjust = document.getElementById('filterAdjust');
const filterAdjustSliders = document.getElementById('filterAdjustSliders');
const filterAdjustIndicators = document.getElementById('filterAdjustIndicators');
const filterApply = document.getElementById('filterApply');
// this is arguably worse than the hard coded tables
{
    let indicators = {
        red: {
            Max: [],
            Min: []
        },
        green: {
            Max: [],
            Min: []
        },
    };
    let i = 0;
    let minmax = 'Max';
    let l1 = () => {
        let hsv = 'H';
        let max = 180;
        let step = 1;
        let l2 = () => {
            let color = 'red';
            let l3 = () => {
                const slider = document.createElement('input');
                slider.type = 'range';
                slider.classList.add('slider');
                slider.classList.add('slider' + hsv);
                slider.id = color + hsv + minmax;
                slider.min = 0;
                slider.max = max;
                slider.step = step;
                let j = i;
                slider.oninput = () => updateSlider(j);
                sliders.push(slider);
                const label = document.createElement('span');
                label.innerHTML = hsv + '&nbsp;' + minmax;
                const indicator = document.createElement('span');
                indicator.id = color + hsv + minmax + 'Indicator';
                indicator.style.marginRight = '4px';
                filterAdjustSliders.appendChild(label);
                filterAdjustSliders.appendChild(slider);
                indicators[color][minmax].push(indicator);
                i++;
            };
            l3();
            color = 'green';
            l3();
        };
        l2();
        hsv = 'S';
        max = 255;
        step = 5;
        l2();
        hsv = 'V';
        l2();
    };
    l1();
    minmax = 'Min';
    l1();
    for (let a in indicators) {
        for (let b in indicators[a]) {
            const block = document.createElement('div');
            const label = document.createElement('span');
            label.innerHTML = '&nbsp;&nbsp;' + b + ':&nbsp;';
            block.appendChild(label);
            for (let c in indicators[a][b]) {
                block.appendChild(indicators[a][b][c]);
            }
            filterAdjustIndicators.appendChild(block);
        }
    }
}
function hsv2hsl(hsvH, hsvS, hsvV) {
	let hslL = (200 - hsvS) * hsvV / 200;
    let hslS = hslL === 0 || hslL === 100 ? 0 : hsvS * hsvV / (hslL <= 50 ? hslL * 2 : 100 - hslL);
	return [ hsvH, hslS, hslL ];
};
function updateSlider(i) {
    document.getElementById(sliders[i].id + 'Indicator').innerText = sliders[i].value;
    let hueSlider = i;
    if (sliders[i].id.includes('H')) {
    } else if (sliders[i].id.includes('S')) {
        hueSlider -= 2;
    } else if (sliders[i].id.includes('V')) {
        hueSlider -= 4;
    }
    let [hslH, hslS, hslL] = hsv2hsl(sliders[hueSlider].value * 2, sliders[hueSlider + 2].value * (100 / 255), sliders[hueSlider + 4].value * (100 / 255));
    sliders[hueSlider].style.setProperty('--hue', hslH);
    sliders[hueSlider + 2].style.setProperty('--hue', hslH);
    sliders[hueSlider + 4].style.setProperty('--hue', hslH);
    sliders[hueSlider + 2].style.setProperty('--saturation', hslS + '%');
    sliders[hueSlider + 4].style.setProperty('--saturation', hslS + '%');
    sliders[hueSlider + 4].style.setProperty('--value', hslL + '%');
    sliders[i].title = sliders[i].value;
};
function getColors() {
    let colors = [];
    for (let i in sliders) {
        colors[i] = sliders[i].value;
    }
    return colors;
};
function setColors(colors) {
    for (let i in colors) {
        sliders[i].value = colors[i];
        updateSlider(parseInt(i));
    }
};
{
    // THIS IS BORKEN
    let k = 0;
    for (let i = 0; i < 2; i++) {
        for (let j = 0; j < 6; j++) {
            sliders[k++].value = initcolors[j % 2][i][j % 3];
        }
    }
    for (let i in sliders) {
        updateSlider(parseInt(i));
    }
}
filterApply.onclick = (e) => {
    socket.emit('setColors', getColors());
};
filterApply.disabled = true;
socket.on('colors', setColors);

// start/stop
const runManual = document.getElementById('runManual');
const runAuto = document.getElementById('runAuto');
const runStop = document.getElementById('runStop');
runManual.onclick = (e) => {
    socket.emit('#runProgram', 'manual');
};
runAuto.onclick = (e) => {
    socket.emit('#runProgram', 'auto');
};
runStop.onclick = (e) => {
    socket.emit('stop');
};
document.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() == 'c' && e.ctrlKey && !e.shiftKey) socket.emit('stop');
});
runManual.disabled = true;
runAuto.disabled = true;
runStop.disabled = true;

async function animateRickroll(widetanmu = true) {
    if (window.bdnmteuwuiufds) return;
    window.bdnmteuwuiufds = true;
    animateAll();
    let eeeeeeeeee = [];
    let oof = 0;
    for (let i = 0; i < 50; i++) {
        let vbuh = new Audio('./assets/null.mp3');
        // let vbuh = new Audio('./assets/SPARK.mp3');
        // let vbuh = new Audio('./assets/RUSH E.mp3');
        // let vbuh = new Audio('./assets/Fused - RKVC.mp3');
        // let vbuh = new Audio('./assets/Newsroom - Riot.mp3');
        // let vbuh = new Audio('./assets/EEEEEEEEEEEEEEEEEEEEEEEEEELECTROMAN ADVENTURES FULL VERSION GEOMETRY DASH 2.11 ADSFADSFDSA FDSAFDSAFDSA FFSAFDSAF DSAF AS FDSA FDSA FDSA.mp3');
        // let vbuh = new Audio('./assets/Kitsune2 - Rainbow Tylenol.mp3');
        // let vbuh = new Audio('./assets/Rainbow Trololol.mp3');
        // let vbuh = new Audio('./assets/Minecraft_ Villager Sound Effect.mp3');
        // let vbuh = new Audio('./assets/Dramatic Vine_Instagram Boom - Sound Effect (HD).mp3');
        // let vbuh = new Audio('./assets/07-The Magus.mp3');
        // let vbuh = new Audio('./assets/Askerad - Home (KSP2 FanMade attempt at a menu theme).mp3');
        // let vbuh = new Audio('./assets/corruption pixel sound effects.mp3');
        // let vbuh = new Audio('./assets/percussion.mp3');
        // let vbuh = new Audio('./assets/200 - Pixl\'d.mp3');
        // let vbuh = new Audio('./assets/400 - Corruption.mp3');
        // let vbuh = new Audio('./assets/404 - Pixel Not Found.mp3');
        // let vbuh = new Audio('./assets/127 - Official Meadow Guarder Song.mp3');
        // let vbuh = new Audio('./assets/The Meadow - Official Meadow Guarder Song.mp3');
        // let vbuh = new Audio('./assets/The Oasis - Official Meadow Guarder Song.mp3');
        vbuh.preload = true;
        vbuh.addEventListener('loadeddata', () => {
            oof++;
        });
        eeeeeeeeee.push(vbuh);
    }
    let wait = setInterval(() => {
        if (oof == eeeeeeeeee.length) {
            clearInterval(wait);
            for (let rickroll of eeeeeeeeee) {
                rickroll.play();
            }
        }
    }, 10);
    let aaaaaaaaaaaa = [];
    let weird = 0;
    if (widetanmu) {
        let dumb = setInterval(() => {
            weird++;
            if (weird > 5) {
                clearInterval(dumb);
                return;
            }
            let stupid = window.open('about:blank', '_blank', 'width=250; height=242');
            stupid.document.write('<style>body { overflow: hidden; }</style><img src="./assets/rickastley.png" style="position: absolute; top: 0; left: 0; width: 100vw;">');
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
    }
    let badidea = setInterval(() => {
        display0Img.src = './assets/rickastley.png';
        display1Img.src = './assets/rickastley.png';
        if (Math.random() < 0.1) {
            let chars = 'AβCDEFGHIJKLMNOPQRSTUVWYZaβcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+`~[]\\{}|;\':",./<>?';
            let random = '';
            for (let i = 0; i < 20; i++) {
                random += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            appendLog(random, `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`);
        }
    }, 2);
    eeeeeeeeee[0].onended = () => {
        for (let asdfasdf of aaaaaaaaaaaa) {
            asdfasdf.close();
        }
        clearInterval(badidea);
        window.bdnmteuwuiufds = false;
        animateRickroll(widetanmu);
    };
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
    if (window.djfhnmkhuehfklkd) return;
    window.djfhnmkhuehfklkd = true;
    const rawDumpContainer = document.getElementById('rawDumpContainer');
    const dropdown = document.getElementById('dropdown');
    let lsd = 0;
    setInterval(() => {
        document.body.style.filter = `hue-rotate(${lsd % 360}deg)`;
        document.body.style.backgroundColor = `hsl(${lsd = (lsd + 20) % 360}, 100%, 50%)`;
        log.style.backgroundColor = `hsl(${(lsd + 50) % 360}, 100%, 50%)`;
        map.style.backgroundColor = `hsl(${(lsd + 100) % 360}, 100%, 50%)`;
        rawDumpContainer.style.backgroundColor = `hsl(${(lsd + 150) % 360}, 100%, 50%)`;
        dropdown.style.backgroundColor = `hsl(${(200 + 150) % 360}, 100%, 50%)`;
    }, 50);
    for (let slider of sliders) {
        setTimeout(() => {
            animate(slider, Math.round(Math.random()));
        }, Math.random() * 3000);
    }
    let backwards = false;
    setInterval(() => {
        if (backwards) {
            historyControls.back = true;
            historyControls.forward = false;
        } else {
            historyControls.back = false;
            historyControls.forward = true;
        }
        if (historyControls.index == 0) backwards = true;
        if (historyControls.index == history.length - 1) backwards = false;
    }, 1);
};
async function animateAll2() {
    if (window.dutjkremvfdsdf) return;
    window.dutjkremvfdsdf = true;
    animateAll();
    var hue = 0;
    var brightness = 1;
    var brightnessDirection = 1;
    var contrast = 1;
    var contrastDirection = -1;
    var saturation = 1;
    var saturationDirection = 1;
    var scale = 1;
    var scaleDirection = 1;
    var rotate = 1;
    var rotateDirection = 1;
    var blur = 0;
    var invert = 0;
    document.body.style.transformOrigin = "center center";
    ultraSecretInterval = setInterval(function () {
        hue += Math.random() * 2;
        brightness += Math.random() * 0.01 * brightnessDirection;
        contrast += Math.random() * 0.01 * contrastDirection;
        saturation += Math.random() * 0.01 * saturationDirection;
        scale += Math.random() * 0.01 * scaleDirection;
        rotate += Math.random() * 20 - 10;
        if (brightness > Math.random() * 0.5 + 1) {
            brightnessDirection = -1;
        }
        else if (brightness < Math.random() * 0.5 + 0.5) {
            brightnessDirection = 1;
        }
        if (contrast > Math.random() * 0.5 + 1) {
            contrastDirection = -1;
        }
        else if (contrast < Math.random() * 0.5 + 0.5) {
            contrastDirection = 1;
        }
        if (saturation > Math.random() * 0.5 + 1) {
            saturationDirection = -1;
        }
        else if (saturation < Math.random() * 0.5 + 0.5) {
            saturationDirection = 1;
        }
        if (scale > Math.random() * 5 + 1) {
            scaleDirection = -1;
        }
        else if (scale < 1) {
            scale = 1;
            scaleDirection = 1;
        }
        blur = Math.random();
        if (Math.random() < 0.5) {
            invert = Math.min(1, invert + 0.05);
        }
        else {
            invert = Math.max(0, invert - 0.05);
        }
        document.body.style.filter = "hue-rotate(" + hue + "deg) brightness(" + brightness + ") contrast(" + contrast + ") saturate(" + saturation + ") invert(" + Math.round(invert) + ") blur(" + blur + "px)";
        document.body.style.transform = "scale(" + scale + ") rotate(" + rotate + "deg) translate(" + (Math.random() * 30 - 15) + "px, " + (Math.random() * 30 - 15) + "px)";
    }, 5);
};

document.getElementById('slideoutTabCheckbox').addEventListener('click', () => sounds.click());
document.getElementById('dropdownTabCheckbox').addEventListener('click', () => sounds.click());