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
console.log(sessionStorage.getItem("jwt"));
const keysPressed = {};

let ws;

