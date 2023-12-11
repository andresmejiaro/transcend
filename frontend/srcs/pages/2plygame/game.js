const gameCanvas = document.getElementById("gameCanvas");
const ctx = gameCanvas.getContext("2d");

let ws;

function startGame(matchId, player1Id, player2Id, clientId, scoreLimit) {
  const uri = `ws://localhost:8001/ws/pong/${matchId}/?player_1_id=${player1Id}&player_2_id=${player2Id}&client_id=${clientId}&scorelimit=${scoreLimit}`;

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

function sendJson(jsonMessage) {

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
}

const getMatchInfo = async (matchId) => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/`;		
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

		const data = await makeRequest(true, url, options);
        console.log(data);
        if (data.status == "ok") {
			return data;
		}

		return null;

    } catch (error) {
        console.error("Error:", error.message);
    }
}

const updateMatchInDb = async (matchId, player2Id) => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/`;		
        const options = {
			method: "PUT",
			mode: "cors",
			credentials: "include",
			headers: {
			  "Content-Type": "application/json",
			},
			body: JSON.stringify({
			  player2: player2Id
			}),
        };

		const data = await makeRequest(true, url, options);
        console.log(data);
        if (data.status == "ok") {
			return data;
		}

		return null;

    } catch (error) {
        console.error("Error:", error.message);
    }
}


const joinMatch = async (matchId) => {
	const playerId = await getUserId();
	const matchData = await getMatchInfo(matchId);
	await updateMatchInDb(matchId, playerId);
	startGame(matchId, matchData.data.player1, playerId, playerId, 11);
}

const activateGame = async () => {
	const param = '{"command":"start_game"}'
	sendJson(param)
}

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
		  player1: userId
		}),
	});

	console.log(response);

	startGame(response.id, userId, "", userId, 11);
}

const handleMatchmaking = async () => {
	const hasToJoinMatch = await canJoinAGame();
	if (hasToJoinMatch) {
		await joinMatch(hasToJoinMatch);
		activateGame();
	} else {
		createAndJoinMatch();
	}
}

handleMatchmaking();
