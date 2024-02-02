let matchId = null;
let gameSock;

const connectGameSocket = async (gameInfo) => {
	const authToken = sessionStorage.getItem("jwt");
	console.log("Game info:")
	console.log(gameInfo)
	matchId = gameInfo.match_id;
	
	return new Promise((resolve, reject) => {
		gameSock = new WebSocket(`${window.DAPHNE_BASE_URL}/ws/pong2/${matchId}/?token=${authToken}`);

		gameSock.addEventListener("open", (event) => {
			resolve(gameSock);
		});

		gameSock.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			updateGameCanvas(data, game);
		});

		gameSock.addEventListener("close", (event) => {
			console.log("WebSocket connection closed:", event);
			reject(new Error("WebSocket connection closed."));
		});
	});
};

function sendJson(jsonMessage) {
	if (gameSock && gameSock.readyState === WebSocket.OPEN) {
		gameSock.send(jsonMessage);
	} else {
		console.error("WebSocket connection not open.");
	}
}

function updateGameCanvas(data, game) {
	//console.log("Updating game canvas with data:", data);
	if (data.type == "message") {
		game.connStatus = data.data.message;
	} else if (data.type == "screen_report") {
		game.receiveRemoteCanvas(data);
	} else if (data.type == "match_results") {
		handleFinishedMatchUpdate(data.data)
	} else if (data.type == "match_finished"){
		game.remoteGameEnd(data);
	}
	else{
		console.error("Invalid message type:", data);
	}
}

function sendKeyPress(key, side, frame) {
	const jsonMessage = JSON.stringify({
		command: "keyboard",
		key_status: "on_press",
		key: key,
		side: side,
		frame: frame,
	});

	// Send the JSON message to the server
	if (gameSock && gameSock.readyState === WebSocket.OPEN) {
		gameSock.send(jsonMessage);
		//console.log("Sent JSON message:", jsonMessage);
	} else {
		console.error("WebSocket connection not open.");
	}
}

function sendRelease(key, side, frame) {
	const jsonMessage = JSON.stringify({
		command: "keyboard",
		key_status: "on_release",
		key: key,
		side: side,
		frame: frame,
	});

	// Send the JSON message to the server
	if (gameSock && gameSock.readyState === WebSocket.OPEN) {
		gameSock.send(jsonMessage);
		//console.log("Sent JSON message:", jsonMessage);
	} else {
		console.error("WebSocket connection not open.");
	}
}

// const userId = await getUserId();

function handleArrowKeyRelease(key) {
	// Customize this based on your game's key bindings
	switch (key) {
		case "ArrowUp":
		case "w":
		case "W":
			sendRelease("up");
			break;
		case "ArrowDown":
		case "s":
		case "S":
			sendRelease("down");
			break;
		case "ArrowLeft":
		case "a":
		case "A":
			sendRelease("left");
			break;
		case "ArrowRight":
		case "d":
		case "D":
			sendRelease("right");
			break;
	}
}

const activateGame = async () => {
	const param = '{"command":"start_ball"}';
	sendJson(param);
};

function handleArrowKeyPress(key) {
	// Customize this based on your game's key bindings
	//console.log(key);
	switch (key) {
		case "ArrowUp":
		case "w":
		case "W":
			sendKeyPress("up");
			break;
		case "ArrowDown":
		case "s":
		case "S":
			sendKeyPress("down");
			break;
		case "ArrowLeft":
		case "a":
		case "A":
			sendKeyPress("left");
			break;
		case "ArrowRight":
		case "d":
		case "D":
			sendKeyPress("right");
			break;	
	}
}
