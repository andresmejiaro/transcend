const matchIdInput = document.getElementById("matchId");
const player1IdInput = document.getElementById("player1Id");
const player2IdInput = document.getElementById("player2Id");
const clientIdInput = document.getElementById("clientId");
const scoreLimitInput = document.getElementById("scoreLimit");
const jsonInput = document.getElementById("jsonInput");
const gameCanvas = document.getElementById("gameCanvas");
const ctx = gameCanvas.getContext("2d");

let ws;

function startGame() {
  const matchId = matchIdInput.value;
  const player1Id = player1IdInput.value;
  const player2Id = player2IdInput.value;
  const clientId = clientIdInput.value;
  const scoreLimit = scoreLimitInput.value;

  const uri = `ws://localhost:8001/ws/pong/${matchIdInput.value}/?player_1_id=${player1IdInput.value}&player_2_id=${player2IdInput.value}&client_id=${clientIdInput.value}&scorelimit=${scoreLimitInput.value}`;

  ws = new WebSocket(uri);

  ws.addEventListener("open", () => {
    console.log("WebSocket connection opened.");
  });

  ws.addEventListener("close", () => {
    console.log("WebSocket connection closed.");
  });

  ws.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    console.log("Received message:", data);

    updateGameCanvas(data);
  });
}

function sendJson() {
  const jsonMessage = jsonInput.value;

  // Send the JSON message to the server
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

document.addEventListener("keydown", (event) => {
  // Handle arrow key presses and send messages to the server
  handleArrowKeyPress(event.key);
});

document.addEventListener("keyup", (event) => {
  // Handle arrow key releases and send messages to the server
  handleArrowKeyRelease(event.key);
});

function updateGameCanvas(data) {
  console.log("Updating game canvas with data:", data);

  if (data.type === "player_list") {
    // Handle player list data if needed
    console.log("Received player list:", data.data);
  } else if (data.type === "game_update") {
    // Handle game update data
    drawPongGame(data.data);
  } else {
    console.error("Invalid message type:", data.type);
  }
}

function drawPongGame(data) {
  // Check if the required properties exist in the data object
  if (
    data &&
    data.canvas &&
    data.canvas.ball &&
    data.canvas.leftPaddle &&
    data.canvas.rightPaddle
  ) {
    ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    drawRect(data.canvas.ball.position, data.canvas.ball.size, "blue");
    drawRect(
      data.canvas.leftPaddle.position,
      data.canvas.leftPaddle.size,
      "green"
    );
    drawRect(
      data.canvas.rightPaddle.position,
      data.canvas.rightPaddle.size,
      "red"
    );

    const scores = data.score;
    ctx.fillStyle = "black";
    ctx.font = "20px Arial";
    ctx.fillText(
      `${player1IdInput.value}: ${scores[player1IdInput.value]} - ${
        player2IdInput.value
      }: ${scores[player2IdInput.value]}`,
      10,
      20
    );
  } else {
    console.error("Invalid data format:", data);
  }
}

function drawRect(position, size, color) {
  ctx.fillStyle = color;
  ctx.fillRect(position.x, position.y, size.x, size.y);
}

function handleArrowKeyPress(key) {
  // Customize this based on your game's key bindings
  switch (key) {
    case "ArrowUp":
      sendKeyPress("up");
      break;
    case "ArrowDown":
      sendKeyPress("down");
      break;
    case "ArrowLeft":
      sendKeyPress("left");
      break;
    case "ArrowRight":
      sendKeyPress("right");
      break;
  }
}

function sendKeyPress(key) {
  const jsonMessage = JSON.stringify({
    command: "keyboard",
    key_status: "on_press",
    key: key,
  });

  // Send the JSON message to the server
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

function handleArrowKeyRelease(key) {
  // Customize this based on your game's key bindings
  switch (key) {
    case "ArrowUp":
      sendRelease("up");
      break;
    case "ArrowDown":
      sendRelease("down");
      break;
    case "ArrowLeft":
      sendRelease("left");
      break;
    case "ArrowRight":
      sendRelease("right");
      break;
  }
}

function sendRelease(key) {
  const jsonMessage = JSON.stringify({
    command: "keyboard",
    key_status: "on_release",
    key: key,
  });

  // Send the JSON message to the server
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

// const userId = await getUserId();

const canJoinAGame = async () => {
	try {
        const url = `${window.DJANGO_API_BASE_URL}/api/user/${userId}/friendlist/`;
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

		const data = await makeRequest(true, url, options);
        
        if (data.status == "ok") {

		}

    } catch (error) {
        console.error("Error:", error.message);
    }
}


const handleMatchmaking = async () => {
	const hasToJoinMatch = canJoinAGame();
	if (hasToJoinMatch)

}

handleMatchmaking();