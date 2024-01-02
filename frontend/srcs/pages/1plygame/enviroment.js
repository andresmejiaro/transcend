// starting setting env
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const keysPressed = {};
canvas.width = 858;
canvas.height= 525;
document.addEventListener('keydown', (event) => {
    keysPressed[event.key] = true;
});
document.addEventListener('keyup', (event) => {
    keysPressed[event.key] = false;
});
ctx.font = '20px Arial';
ctx.fillStyle = 'white';

let ws;

