// Get your canvas and context
const gameCanvas = document.getElementById("gameCanvas");
const ctx = gameCanvas.getContext("2d");


// Handle keydown event
// document.addEventListener("keydown", (event) => {
//   throttledKeyPress(event.key);
// });

// WebSocket instance
let ws;


// Textures
const textures = {
  ball: new Image(),
  paddleGreen: new Image(),
  paddleRed: new Image(),
};

// Set the source URLs for your images
textures.ball.src = './srcs/assets/game/ball.png';
textures.paddleGreen.src = './srcs/assets/game/green_paddle.png';
textures.paddleRed.src = './srcs/assets/game/purple_paddle.png';


// Function to start the game
function startGame(matchId, player1Id, player2Id, clientId, scoreLimit) {
  return new Promise((resolve, reject) => {
    const uri = `${window.DAPHNE_BASE_URL}/ws/pong/${matchId}/?player_1_id=${player1Id}&player_2_id=${player2Id}&client_id=${clientId}&scorelimit=${scoreLimit}`;

    ws = new WebSocket(uri);

    ws.addEventListener("open", () => {
      console.log("WebSocket connection opened.");
      resolve(ws);
    });

    ws.addEventListener("close", () => {
      console.log("WebSocket connection closed.");
      reject("WebSocket connection closed.");
    });

    ws.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      console.log("Received message:", data);
      updateGameCanvas(data);
    });
  });
}

// Function to send JSON message over WebSocket
const sendJson = (messageType, payload) => {
  return new Promise((resolve, reject) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(
        JSON.stringify({
          type: messageType,
          ...payload,
        })
      );
      resolve();
    } else {
      console.error("WebSocket is not in the OPEN state.");
      reject(new Error("WebSocket is not open"));
    }
  });
};

// Handle keydown event for arrow keys
document.addEventListener("keydown", (event) => {
  handleArrowKeyPress(event.key);
});

// Handle keyup event for arrow keys
document.addEventListener("keyup", (event) => {
  handleArrowKeyRelease(event.key);
});

// Function to update the game canvas
function updateGameCanvas(data) {
  console.log("Updating game canvas with data:", data);

  if (data.type === "player_list") {
    console.log("Received player list:", data.data);
  } else if (data.type === "game_update") {
    drawPongGame(data.data);
  } else if (data.type === "update_buffer") {
    data.data.forEach((update) => {
      console.log("Buffered game update:", update);
      drawPongGame(update.game_update);
    });
  } else {
    console.error("Invalid message type:", data.type);
  }
}

// Function to draw the Pong game on the canvas
// function drawPongGame(data) {
//   if (
//     data &&
//     data.ball &&
//     data.leftPaddle &&
//     data.rightPaddle
//   ) {
//     ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
//     drawRect(data.ball.position, data.ball.size, "blue");
//     drawRect(
//       data.leftPaddle.position,
//       data.leftPaddle.size,
//       "green"
//     );
//     drawRect(
//       data.rightPaddle.position,
//       data.rightPaddle.size,
//       "red"
//     );

//     const scores = data.score;
//     ctx.fillStyle = "black";
//     ctx.font = "20px Arial";
//     ctx.fillText(
//       `${player1IdInput.value}: ${scores[player1IdInput.value]} - ${
//         player2IdInput.value
//       }: ${scores[player2IdInput.value]}`,
//       10,
//       20
//     );
//   } else {
//     console.error("Invalid data format:", data);
//   }
// }

// Function to draw the Pong game on the canvas
function drawPongGame(data) {
  if (
    data &&
    data.ball &&
    data.leftPaddle &&
    data.rightPaddle
  ) {
    ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    drawRectWithImage(
      data.ball.position,
      data.ball.size,
      textures.ball
    );
    drawRectWithImage(
      data.leftPaddle.position,
      data.leftPaddle.size,
      textures.paddleGreen
    );
    drawRectWithImage(
      data.rightPaddle.position,
      data.rightPaddle.size,
      textures.paddleRed
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


function drawRectWithImage(position, size, image) {
  ctx.drawImage(image, position.x, position.y, size.x, size.y);
}

// Function to draw a rectangle on the canvas
// function drawRect(position, size, color) {
//   ctx.fillStyle = color;
//   ctx.fillRect(position.x, position.y, size.x, size.y);
// }

// Handle arrow key press
function handleArrowKeyPress(key) {
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

// Send key press information to the server
function sendKeyPress(key) {
  const jsonMessage = JSON.stringify({
    command: "keyboard",
    key_status: "on_press",
    key: key,
  });

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

// Handle arrow key release
function handleArrowKeyRelease(key) {
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

// Send key release information to the server
function sendRelease(key) {
  const jsonMessage = JSON.stringify({
    command: "keyboard",
    key_status: "on_release",
    key: key,
  });

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

// Function to check if the user can join a game
const canJoinAGame = async () => {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/match/available`;

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
      return data.id;
    }

    return null;
  } catch (error) {
    console.error("Error:", error.message);
  }
};

// Function to join a match
const joinMatch = async (matchId) => {
  const playerId = await getUserId();
  const matchData = await getMatchInfo(matchId);
  await updateMatchInDb(matchId, playerId);
  await startGame(matchId, matchData.data.player1, playerId, playerId, 11);

  activateGame();
};

// Function to activate the game
const activateGame = async () => {
  console.log("activating game")
  await sendJson("command", {
    command: "start_game",
  });
};

// Function to create and join a match
const createAndJoinMatch = async () => {
  const userId = await getUserId();

  const url = `${window.DJANGO_API_BASE_URL}/api/match/create/`;
  const response = await makeRequest(true, url, {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      player1: userId,
    }),
  });

  console.log(response);

  startGame(response.match_id, userId, "", userId, 11);
};

// Function to handle matchmaking
const handleMatchmaking = async () => {
  const hasToJoinMatch = await canJoinAGame();
  if (hasToJoinMatch) {
    await joinMatch(hasToJoinMatch);
    activateGame();
  } else {
    createAndJoinMatch();
  }
};

// Start matchmaking


const urlParams = new URLSearchParams(window.location.search);
const matchId = urlParams.get("matchid");

const handleFirstSteps = async () => {
  if (matchId) {
    await handleMatchmakingFriend(matchId);
  } else {
    handleMatchmaking();
  }
}

handleFirstSteps();