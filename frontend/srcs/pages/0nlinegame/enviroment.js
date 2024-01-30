// starting setting env
const matchIdInput = document.getElementById('matchId');
const tokenInput = document.getElementById('tokenId');
const jsonInput = document.getElementById('jsonInput');
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 858;
canvas.height= 525;
ctx.font = '20px Arial';
ctx.fillStyle = 'white';
const keysPressed = {};
document.addEventListener('keydown', (event) => {
    keysPressed[event.key] = true;
});
document.addEventListener('keyup', (event) => {
    keysPressed[event.key] = false;
});

