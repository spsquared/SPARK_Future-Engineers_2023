// tick: https://www.beepbox.co/#9n11sbk0l00e00t4Ia2g00j07r3i200o1T0v0u00f0q00d04w2h0E0T2v6u02f0q00d04w4E0b0gp180a8w8so0
// click: https://www.beepbox.co/#9n12s0k0l00e00t4Ia2g00j07r3i0o4T5v1u85f10l7q011d23HK-LBJrttAAAyqhh0E0T2v3u02f10f6q00d04w1E0T3v6u03f0q00d04S____00000000000E0b4hp1f0aow8so0F2e7600
// ding: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v6u00f0qg01d04w2h0E0bwp16FyY760
// start: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v6u00f0qg01d07w2h0E0bwp17FyWlD4w
// stop: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v6u00f0qg01d07w2h0E0bwp17FyXlD4w
// ping: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v4u00f0qg01d0aw2h0E0bwp16FBY74w
// connect: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v6u00f0qg01d0aw2h0E0bwp17FE-BxHw
// disconnect: https://www.beepbox.co/#9n10sbk0l00e00t4Ia2g00j00r3i0o4T0v6u00f0qg01d0aw2h0E0bwp17FE_4EqU

const audioContext = new (window.AudioContext ?? window.webkitAudioContext ?? Error)();
const globalVolume = audioContext.createGain();
globalVolume.connect(audioContext.destination);
const sounds = {
    tick: () => {},
    click: () => {},
    ding: () => {},
    start: () => {},
    stop: () => {},
    ping: () => {},
    connect: () => {},
    disconnect: () => {}
};
for (let id in sounds) {
    const request = new XMLHttpRequest();
    request.open('GET', `./sounds/${id}.mp3`, true);
    request.responseType = 'arraybuffer';
    request.onload = () => {
        if (request.status >= 200 && request.status < 400) audioContext.decodeAudioData(request.response, (buf) => {
            const preloadQueue = [];
            preloadQueue.push(audioContext.createBufferSource());
            preloadQueue[0].buffer = buf;
            preloadQueue[0].connect(globalVolume);
            preloadQueue[0].onended = preloadQueue[0].disconnect;
            sounds[id] = () => {
                preloadQueue.shift().start();
                const nextSource = audioContext.createBufferSource();
                nextSource.buffer = buf;
                nextSource.connect(globalVolume);
                preloadQueue.push(nextSource);
                nextSource.onended = nextSource.disconnect;
            };
        });
    };
    request.send();
}
if (navigator.userActivation) {
    let waitForInteraction = setInterval(() => {
        if (navigator.userActivation.hasBeenActive) {
            audioContext.resume();
            clearInterval(waitForInteraction);
        }
    }, 100);
} else {
    document.addEventListener('click', function c(e) {
        document.removeEventListener('click', c);
        audioContext.resume();
    });
}

document.addEventListener('visibilitychange', () => {
    if (document.hidden) globalVolume.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 1);
    else globalVolume.gain.linearRampToValueAtTime(1, audioContext.currentTime + 1);
});

document.querySelectorAll('button').forEach(el => el.addEventListener('click', () => sounds.click()));
document.querySelectorAll('.slider').forEach(el => el.addEventListener('input', () => sounds.tick()));
document.querySelectorAll('.toggleInput').forEach(el => el.addEventListener('click', () => sounds.click()));
document.getElementById('slideoutTabCheckbox').addEventListener('click', () => sounds.click());
document.getElementById('dropdownTabCheckbox').addEventListener('click', () => sounds.click());