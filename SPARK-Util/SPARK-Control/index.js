window.addEventListener('error', (e) => {
    appendLog(`An error occured:<br>${e.message}<br>${e.filename} ${e.lineno}:${e.colno}`, 'red');
});

const initcolors = [
    [
        [25, 255, 255],
        [0, 95, 75]
    ],
    [
        [110, 255, 255],
        [30, 30, 40]
    ],
];

const socket = io(ip + ':4040', {
    autoConnect: false,
    reconnection: false
});

let connected = false;
let toReconnect = false;
let autoReconnect = true;
socket.on('connect', () => {
    let num = Math.random();
    socket.on('pong', function confirm(n) {
        if (n == num) {
            clearInterval(pingspam)
            connected = true;
            appendLog('Connected!', 'lime');
            socket.off('pong', confirm);
            stream.disabled = false;
            capture.disabled = false;
            rawcapture.disabled = false;
            socket.emit('getStreamState');
            socket.emit('getColors');
        }
    });
    let pingspam = setInterval(() => {
        socket.emit('ping', num);
    }, 500);
});
let ondisconnect = () => {
    connected = false;
    if (autoReconnect) toReconnect = true;
    appendLog('Connection closed<button class="connectNow" onclick="reconnect(true);">RECONNECT NOW</button>', 'red');
    setTimeout(reconnect, 10000);
    stream.disabled = true;
    capture.disabled = true;
    rawcapture.disabled = true;
};
socket.on('disconnect', ondisconnect);
socket.on('timeout', ondisconnect);
socket.on('error', ondisconnect);
socket.on('authenticate', () => {
    socket.emit('authenticateResponse', auth_uuid);
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
const log = document.getElementById('log');
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
socket.on('message', (data) => {
    playSound();
    appendLog(data);
});

// manual driving
const controls = {
    forward: 0,
    backward: 0,
    left: 0,
    right: 0,
    throttle: 0,
    steering: 0,
    trim: 0.05,
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
            controls.backward = -0;
            controls.updated = true;
            break;
        case 'a':
            controls.left = -0;
            controls.updated = true;
            break;
        case 'd':
            controls.right = 0;
            controls.updated = true;
            break;
    }
};
let pressedbuttons = [];
function updateControllers() {
    let controllers = navigator.getGamepads();
    for (let i in controllers) {
        if (controllers[i] instanceof Gamepad) {
            let controller = controllers[i];
            throttle = Math.round(controller.axes[1] * -100);
            steering = Math.round((controller.axes[2] - controls.trim) * 100);
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
function updateSlider(i) {
    document.getElementById(sliders[i].id + 'Indicator').innerText = sliders[i].value;
    if (sliders[i].id.includes('H')) {
        sliders[i].style.setProperty('--hue', sliders[i].value * 2);
        sliders[i + 2].style.setProperty('--hue', sliders[i].value * 2);
        sliders[i + 4].style.setProperty('--hue', sliders[i].value * 2);
    } else if (sliders[i].id.includes('S')) {
        sliders[i].style.setProperty('--saturation', sliders[i].value * (100 / 255) + '%');
        sliders[i + 2].style.setProperty('--saturation', sliders[i].value * (100 / 255) + '%');
    } else if (sliders[i].id.includes('V')) {
        sliders[i].style.setProperty('--value', sliders[i].value * (50 / 255) + '%');
    }
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
socket.on('colors', setColors);

// stop
// document.getElementById('emergencyStop').onclick = () => {
//     send('stop', {});
// };
document.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() == 'c' && e.ctrlKey) socket.emit('stop');
});

let rickrolled = false;
document.getElementById('disconnect').onclick = async () => {
    socket.disconnect();
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
async function animateAll2() {
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