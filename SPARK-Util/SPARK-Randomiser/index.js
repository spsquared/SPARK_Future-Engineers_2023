ctx = canvas.getContext('2d');

canvas.width = 3100;
canvas.height = 3100;
ctx.scale(10,10);

const redPillar = 'rgba(238,39,55,1)';
const greenPillar = 'rgba(68,214,44,1)';
const orangeLine = 'rgba(255,102,0,1)';
const blueLine = 'rgba(0,51,255,1)';
var resetField = function(){
    canvas.width = 3100;
    canvas.height = 3100;
    ctx.scale(10,10);
    ctx.clearRect(0, 0, 310, 310);
    ctx.fillStyle = 'rgba(255, 255, 255, 1)';
    ctx.fillRect(0, 0, 310, 310);
    ctx.translate(155,155);
    for (let i = 0; i < 4; i++) {
        ctx.translate(50, 50);
        ctx.rotate(Math.PI/6);
        ctx.fillStyle = orangeLine;
        ctx.fillRect(-3, -1.5, 120, 3);
        ctx.rotate(Math.PI/6);
        ctx.fillStyle = blueLine;
        ctx.fillRect(-3, -1.5, 120, 3);
        ctx.rotate(-Math.PI/3);
        ctx.translate(-50, -50);
        ctx.rotate(-Math.PI/2);
    }
    ctx.translate(-155,-155);
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(0,0,310,5);
    ctx.fillRect(305,0,5,310);
    ctx.fillRect(0,305,310,5);
    ctx.fillRect(0,0,5,310);
    ctx.fillRect(105,105,100,100);
    for(var i = 0;i < 4;i++){
        drawPillarCircle(105,45);
        drawPillarCircle(105,65);
        drawPillarCircle(155,45);
        drawPillarCircle(155,65);
        drawPillarCircle(205,45);
        drawPillarCircle(205,65);
        ctx.translate(155,155);
        ctx.rotate(0.5 * Math.PI);
        ctx.translate(-155,-155);
    }
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(104.5, 44.5, 101, 1);
    ctx.fillRect(104.5, 64.5, 101, 1);
    ctx.fillRect(0, 104.5, 310, 1);
    ctx.fillRect(0, 154.5, 310, 1);
    ctx.fillRect(0, 204.5, 310, 1);
    ctx.fillRect(104.5, 244.5, 101, 1);
    ctx.fillRect(104.5, 264.5, 101, 1);
    ctx.translate(155,155);
    ctx.rotate(0.5*Math.PI);
    ctx.translate(-155,-155);
    ctx.fillRect(104.5, 44.5, 101, 1);
    ctx.fillRect(104.5, 64.5, 101, 1);
    ctx.fillRect(0, 104.5, 310, 1);
    ctx.fillRect(0, 154.5, 310, 1);
    ctx.fillRect(0, 204.5, 310, 1);
    ctx.fillRect(104.5, 244.5, 101, 1);
    ctx.fillRect(104.5, 264.5, 101, 1);
}
var drawPillarCircle = function(x,y){
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(x - 1,y - 1,2,2);
    ctx.beginPath();
    ctx.arc(x,y,4,0,2 * Math.PI);
    ctx.stroke();
}
var drawStartingPosition = function(rotations,position,direction){
    ctx.fillStyle = 'rgba(255,255,0,0.5)';
    ctx.translate(155,155);
    ctx.rotate(0.5 * Math.PI * rotations);
    if(position === 0){
        ctx.fillRect(-50,-150,50,40);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-50,-150,10,40);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-10,-150,10,40);
        }
    }
    else if(position === 1){
        ctx.fillRect(0,-150,50,40);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(0,-150,10,40);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(40,-150,10,40);
        }
    }
    else if(position === 2){
        ctx.fillRect(-50,-110,50,20);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-50,-110,10,20);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-10,-110,10,20);
        }
    }
    else if(position === 3){
        ctx.fillRect(0,-110,50,20);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(0,-110,10,20);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(40,-110,10,20);
        }
    }
    else if(position === 4){
        ctx.fillRect(-50,-90,50,40);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-50,-90,10,40);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(-10,-90,10,40);
        }
    }
    else if(position === 5){
        ctx.fillRect(0,-90,50,40);
        if(direction === 0){
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(0,-90,10,40);
        }
        else{
            ctx.fillStyle = 'rgba(0,255,255,0.5)';
            ctx.fillRect(40,-90,10,40);
        }
    }
    ctx.rotate(-0.5 * Math.PI * rotations);
    ctx.translate(-155,-155);
}
var drawPillar = function(color,rotations,position){
    ctx.fillStyle = color;
    ctx.translate(155,155);
    ctx.rotate(0.5 * Math.PI * rotations);
    if(position === 0){
        ctx.fillRect(-52.5,-112.5,5,5);
    }
    else if(position === 1){
        ctx.fillRect(-2.5,-112.5,5,5);
    }
    else if(position === 2){
        ctx.fillRect(47.5,-112.5,5,5);
    }
    else if(position === 3){
        ctx.fillRect(-52.5,-92.5,5,5);
    }
    else if(position === 4){
        ctx.fillRect(-2.5,-92.5,5,5);
    }
    else if(position === 5){
        ctx.fillRect(47.5,-92.5,5,5);
    }
    ctx.rotate(-0.5 * Math.PI * rotations);
    ctx.translate(-155,-155);
}
var images = [];
images.push(new Image());
images[images.length - 1].src = "./images/grep.png";
images.push(new Image());
images[images.length - 1].src = "./images/meadowguarder.png";
images.push(new Image());
images[images.length - 1].src = "./images/oceanguarder.png";
images.push(new Image());
images[images.length - 1].src = "./images/Ten Eyed One.png";
images.push(new Image());
images[images.length - 1].src = "./images/the blob.png";
images.push(new Image());
images[images.length-1].src = './images/piston-large.png';
images.push(new Image());
images[images.length-1].src = './images/Preview.png';
images.push(new Image());
images[images.length-1].src = './images/World.png';
images.push(new Image());
images[images.length-1].src = './images/11-25-21-b.png';
images.push(new Image());
images[images.length-1].src = './images/mountainguarder.png';
images.push(new Image());
images[images.length-1].src = './images/rickastley.png';
var drawGaruderPillar = function(rotations,position){
    ctx.translate(155,155);
    ctx.rotate(0.5 * Math.PI * rotations);
    if(position === 0){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],-52.5,-112.5,15,15);
    }
    else if(position === 1){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],-2.5,-112.5,15,15);
    }
    else if(position === 2){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],47.5,-112.5,15,15);
    }
    else if(position === 3){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],-52.5,-92.5,15,15);
    }
    else if(position === 4){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],-2.5,-92.5,15,15);
    }
    else if(position === 5){
        ctx.drawImage(images[Math.floor(Math.random() * images.length)],47.5,-92.5,15,15);
    }
    ctx.rotate(-0.5 * Math.PI * rotations);
    ctx.translate(-155,-155);
}

resetField();

randomiseWithoutPillars.onclick = function(){
    resetField();
    startX = 0;
    startY = 0;
    endX = 0;
    endY = 0;
    if(Math.random() < 0.5){
        startX = 105;
    }
    else{
        startX = 65;
    }
    if(Math.random() < 0.5){
        startY = 105;
    }
    else{
        startY = 65;
    }
    if(Math.random() < 0.5){
        endX = 205;
    }
    else{
        endX = 245;
    }
    if(Math.random() < 0.5){
        endY = 205;
    }
    else{
        endY = 245;
    }
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(startX,startY,endX - startX,endY - startY);
    startingLocation = Math.floor(Math.random() * 4);
    if(startingLocation === 0){
        if(startY === 105){
            startingPosition = Math.floor(Math.random() * 6);
            drawStartingPosition(0,startingPosition,Math.floor(Math.random() * 2));
        }
        else{
            startingPosition = Math.floor(Math.random() * 4);
            drawStartingPosition(0,startingPosition,Math.floor(Math.random() * 2));
        }
    }
    else if(startingLocation === 1){
        if(endX === 205){
            startingPosition = Math.floor(Math.random() * 6);
            drawStartingPosition(1,startingPosition,Math.floor(Math.random() * 2));
        }
        else{
            startingPosition = Math.floor(Math.random() * 4);
            drawStartingPosition(1,startingPosition,Math.floor(Math.random() * 2));
        }
    }
    else if(startingLocation === 2){
        if(endY === 205){
            startingPosition = Math.floor(Math.random() * 6);
            drawStartingPosition(2,startingPosition,Math.floor(Math.random() * 2));
        }
        else{
            startingPosition = Math.floor(Math.random() * 4);
            drawStartingPosition(2,startingPosition,Math.floor(Math.random() * 2));
        }
    }
    else if(startingLocation === 3){
        if(startX === 105){
            startingPosition = Math.floor(Math.random() * 6);
            drawStartingPosition(3,startingPosition,Math.floor(Math.random() * 2));
        }
        else{
            startingPosition = Math.floor(Math.random() * 4);
            drawStartingPosition(3,startingPosition,Math.floor(Math.random() * 2));
        }
    }
}
randomiseWithPillars.onclick = function(){
    resetField();
    let straightSection = Math.floor(Math.random() * 4);
    let sections = [
        [[1,5]],
        [[0,5]],
        [[1,4]],
        [[0,4]],
        [[1,3]],
        [[0,3]],
        [[1,2]],
        [[0,2]],
        [[1,1]],
        [[0,1]],
        [[1,0]],
        [[0,0]],

        [[1,2],[1,3]],
        [[1,2],[0,3]],
        [[0,2],[1,3]],
        [[1,2],[0,3]],
        [[0,2],[1,3]],
        [[0,2],[0,3]],
        
        [[1,0],[1,5]],
        [[1,0],[0,5]],
        [[0,0],[1,5]],
        [[1,0],[0,5]],
        [[0,0],[1,5]],
        [[0,0],[0,5]],
        
        [[1,3],[1,5]],
        [[1,3],[0,5]],
        [[0,3],[1,5]],
        [[1,3],[0,5]],
        [[0,3],[1,5]],
        [[0,3],[0,5]],
        
        [[1,0],[1,2]],
        [[1,0],[0,2]],
        [[0,0],[1,2]],
        [[1,0],[0,2]],
        [[0,0],[1,2]],
        [[0,0],[0,2]],
    ];
    let pillarLocations = [
        "",
        "",
        "",
        "",
    ];
    let drawLocations = [];
    if(Math.random() < 0.5){
        drawLocations.push([redPillar,straightSection,1]);
        sections.splice(9,1);
    }
    else{
        drawLocations.push([greenPillar,straightSection,1]);
        sections.splice(8,1);
    }
    pillarLocations[straightSection] = "center";
    for(var i = straightSection + 1;i < straightSection + 4;i++){
        let randomSection = Math.floor(Math.random() * sections.length);
        let numberOfPillars = 0;
        var position = 0;
        for(var j in sections[randomSection]){
            position = sections[randomSection][j][1];
            if(sections[randomSection][j][0] === 0){
                drawLocations.push([redPillar,i,sections[randomSection][j][1]]);
            }
            else{
                drawLocations.push([greenPillar,i,sections[randomSection][j][1]]);
            }
            numberOfPillars += 1;
        }
        if(numberOfPillars === 2){
            pillarLocations[i % 4] = "both";
        }
        else{
            if(position === 0 || position === 3){
                pillarLocations[i % 4] = "right";
            }
            if(position === 1 || position === 4){
                pillarLocations[i % 4] = "center";
            }
            if(position === 2 || position === 5){
                pillarLocations[i % 4] = "left";
            }
        }
        sections.splice(randomSection,1);
    }
    let startingLocation = Math.floor(Math.random() * 4);
    if(pillarLocations[startingLocation] === "both"){
        if(Math.random() < 0.5){
            drawStartingPosition(startingLocation,2,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "left"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,3,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "center"){
        startingPosition = Math.floor(Math.random() * 2);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,1);
        }
    }
    if(pillarLocations[startingLocation] === "right"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    for (let location of drawLocations) {
        drawPillar(location[0], location[1], location[2]);
    }
}
randomiseWeirdly.onclick = function(){
    resetField();
    startX = 0;
    startY = 0;
    endX = 0;
    endY = 0;
    if(Math.random() < 0.5){
        startX = 105;
    }
    else if(Math.random() < 0.5){
        startX = 65;
    }
    else if(Math.random() < 0.9){
        startX = 45;
    }
    else{
        startX = 5;
    }
    if(Math.random() < 0.5){
        startY = 105;
    }
    else if(Math.random() < 0.5){
        startY = 65;
    }
    else if(Math.random() < 0.9){
        startY = 45;
    }
    else{
        startY = 5;
    }
    if(Math.random() < 0.5){
        endX = 205;
    }
    else if(Math.random() < 0.5){
        endX = 245;
    }
    else if(Math.random() < 0.9){
        endX = 265;
    }
    else{
        endX = 305;
    }
    if(Math.random() < 0.5){
        endY = 205;
    }
    else if(Math.random() < 0.5){
        endY = 245;
    }
    else if(Math.random() < 0.9){
        endY = 265;
    }
    else{
        endY = 305;
    }
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(startX,startY,endX - startX,endY - startY);
    let straightSection = Math.floor(Math.random() * 4);
    let sections = [
        [[0,1],[1,5]],
        [[1,1],[0,5]],
        [[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)],[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)]],
        [[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)],[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)]],
        [[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)],[0,Math.floor(Math.random() * 6)],[1,Math.floor(Math.random() * 6)]],
    ];
    let pillarLocations = [
        "",
        "",
        "",
        "",
    ];
    let drawLocations = [];
    if(Math.random() < 0.5){
        drawLocations.push([redPillar,straightSection,1]);
        sections.splice(9,1);
    }
    else{
        drawLocations.push([greenPillar,straightSection,1]);
        sections.splice(8,1);
    }
    pillarLocations[straightSection] = "center";
    for(var i = straightSection + 1;i < straightSection + 4;i++){
        let randomSection = Math.floor(Math.random() * sections.length);
        let numberOfPillars = 0;
        var position = 0;
        for(var j in sections[randomSection]){
            position = sections[randomSection][j][1];
            if(sections[randomSection][j][0] === 0){
                drawLocations.push([redPillar,i,sections[randomSection][j][1]]);
            }
            else{
                drawLocations.push([greenPillar,i,sections[randomSection][j][1]]);
            }
            numberOfPillars += 1;
        }
        if(numberOfPillars === 2){
            pillarLocations[i % 4] = "both";
        }
        else{
            if(position === 0 || position === 3){
                pillarLocations[i % 4] = "right";
            }
            if(position === 1 || position === 4){
                pillarLocations[i % 4] = "center";
            }
            if(position === 2 || position === 5){
                pillarLocations[i % 4] = "left";
            }
        }
        sections.splice(randomSection,1);
    }
    let startingLocation = Math.floor(Math.random() * 4);
    if(pillarLocations[startingLocation] === "both"){
        if(Math.random() < 0.5){
            drawStartingPosition(startingLocation,2,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "left"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,3,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "center"){
        startingPosition = Math.floor(Math.random() * 2);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,1);
        }
    }
    if(pillarLocations[startingLocation] === "right"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    drawStartingPosition(Math.floor(Math.random() * 4), Math.floor(Math.random()*6), Math.floor(Math.random()*2));
    for (let location of drawLocations) {
        drawPillar(location[0], location[1], location[2]);
    }
}
randomiseGaruder.onclick = function(){
    resetField();
    startX = 0;
    startY = 0;
    endX = 0;
    endY = 0;
    if(Math.random() < 0.5){
        startX = 105;
    }
    else if(Math.random() < 0.5){
        startX = 65;
    }
    else{
        startX = 45;
    }
    if(Math.random() < 0.5){
        startY = 105;
    }
    else if(Math.random() < 0.5){
        startY = 65;
    }
    else{
        startY = 45;
    }
    if(Math.random() < 0.5){
        endX = 205;
    }
    else if(Math.random() < 0.5){
        endX = 245;
    }
    else{
        endX = 265;
    }
    if(Math.random() < 0.5){
        endY = 205;
    }
    else if(Math.random() < 0.5){
        endY = 245;
    }
    else{
        endY = 265;
    }
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(startX,startY,endX - startX,endY - startY);
    let sections = [
        [[1,5]],
        [[0,5]],
        [[1,4]],
        [[0,4]],
        [[1,3]],
        [[0,3]],
        [[1,2]],
        [[0,2]],
        [[1,1]],
        [[0,1]],
        [[1,0]],
        [[0,0]],

        [[1,2],[1,3]],
        [[1,2],[0,3]],
        [[0,2],[1,3]],
        [[1,2],[0,3]],
        [[0,2],[1,3]],
        [[0,2],[0,3]],
        
        [[1,0],[1,5]],
        [[1,0],[0,5]],
        [[0,0],[1,5]],
        [[1,0],[0,5]],
        [[0,0],[1,5]],
        [[0,0],[0,5]],
        
        [[1,3],[1,5]],
        [[1,3],[0,5]],
        [[0,3],[1,5]],
        [[1,3],[0,5]],
        [[0,3],[1,5]],
        [[0,3],[0,5]],
        
        [[1,0],[1,2]],
        [[1,0],[0,2]],
        [[0,0],[1,2]],
        [[1,0],[0,2]],
        [[0,0],[1,2]],
        [[0,0],[0,2]],
    ];
    let pillarLocations = [
        "",
        "",
        "",
        "",
    ];
    let drawLocations = [];
    for(var i = 0;i < 4;i++){
        let randomSection = Math.floor(Math.random() * sections.length);
        let numberOfPillars = 0;
        var position = 0;
        for(var j in sections[randomSection]){
            position = sections[randomSection][j][1];
            if(sections[randomSection][j][0] === 0){
                drawLocations.push([i,sections[randomSection][j][1]]);
            }
            else{
                drawLocations.push([i,sections[randomSection][j][1]]);
            }
            numberOfPillars += 1;
        }
        if(numberOfPillars === 2){
            pillarLocations[i % 4] = "both";
        }
        else{
            if(position === 0 || position === 3){
                pillarLocations[i % 4] = "right";
            }
            if(position === 1 || position === 4){
                pillarLocations[i % 4] = "center";
            }
            if(position === 2 || position === 5){
                pillarLocations[i % 4] = "left";
            }
        }
        sections.splice(randomSection,1);
    }
    let startingLocation = Math.floor(Math.random() * 4);
    if(pillarLocations[startingLocation] === "both"){
        if(Math.random() < 0.5){
            drawStartingPosition(startingLocation,2,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "left"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,3,1);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    if(pillarLocations[startingLocation] === "center"){
        startingPosition = Math.floor(Math.random() * 2);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,1);
        }
    }
    if(pillarLocations[startingLocation] === "right"){
        startingPosition = Math.floor(Math.random() * 3);
        if(startingPosition === 0){
            drawStartingPosition(startingLocation,2,1);
        }
        else if(startingPosition === 1){
            drawStartingPosition(startingLocation,2,0);
        }
        else{
            drawStartingPosition(startingLocation,3,0);
        }
    }
    drawStartingPosition(Math.floor(Math.random() * 4), Math.floor(Math.random()*6), Math.floor(Math.random()*2));
    for (let location of drawLocations) {
        drawGaruderPillar(location[0], location[1]);
    }
}
reset.onclick = resetField;

window.onresize = function() {
    if (window.innerWidth > 3000) {
        document.getElementById('rickastley').style.display = 'block';
    } else {
        document.getElementById('rickastley').style.display = 'none';
    }
}