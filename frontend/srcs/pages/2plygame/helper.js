

function SetUpListeners(matchId, player1Id, player2Id, clientId, scoreLimit,
    game) {
  return new Promise((resolve, reject) => {
    const uri = `ws://localhost:8001/ws/pong/${matchId}/?player_1_id=${player1Id}&player_2_id=${player2Id}&client_id=${clientId}&scorelimit=${scoreLimit}`;

    ws = new WebSocket(uri);

    ws.addEventListener("open", () => {
      console.log("WebSocket connection opened.");
      resolve(ws); // Resolve the promise with the WebSocket instance
    });

    ws.addEventListener("close", () => {
      console.log("WebSocket connection closed.");
      reject("WebSocket connection closed."); // Reject the promise with an error message
    });

    ws.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);

      console.log("Received message:", data);

      updateGameCanvas(data, game);
    });
   
    //ws.addEventListener("player_list", (event) => {
    //  const data = JSON.parse(event.data);

    //  console.log("Received message:", data);
      //manejar de manera sensible
    //  game.updatePlayerNames(data);
    //});
    
    // add event listener for game_update
  });
}

function sendJson(jsonMessage) {
  console.log("WebSocket readyState:", ws.readyState);

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(jsonMessage);
    console.log("Sent JSON message:", jsonMessage);
  } else {
    console.error("WebSocket connection not open.");
  }
}

function updateGameCanvas(data, game) {
  //console.log("Updating game canvas with data:", data);
  //console.log(data)
  if (data.type === "player_list") {
    //console.log("Received player list:", data.data);
    game.updatePlayerNames(data);
    
  } else if (data.type === "update_buffer") {
    // Handle game update data
    //console.log("game data:", data.data);
    drawPongGame(data.data[0]["game_update"], game);
    game.scoreUpdate(data.data[0]["score_update"]);
  } else if (data.type === "paddle_update") {
      game.paddleRemoteUpdate(data);
  } else {
    // Handle game update data
    //console.log("game data:", data.data);
    console.error("Invalid message type:", data.type);
  }
}

function drawPongGame(data,game) {
  game.receiveRemoteCanvas(data);
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

function sendPaddle(id, paddle) {
  const jsonMessage = JSON.stringify({
    command: "paddle_update",
    [id]:{
      position: paddle.getPosition,
      size: paddle.getSize,
      speed: paddle.getSpeed
    }
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
};

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
};

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
        player2: player2Id,
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
};

const joinMatch = async (matchId, game) => {
  const playerId = await getUserId();
  const matchData = await getMatchInfo(matchId);
  await updateMatchInDb(matchId, playerId);
  await SetUpListeners(matchId, matchData.data.player1, playerId, playerId, 11, game);

};

const activateGame = async () => {
  const param = '{"command":"start_game"}';
  sendJson(param);
};

const createAndJoinMatch = async (game) => {
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

  SetUpListeners(response.match_id, userId, "", userId, 11, game);
};

const handleMatchmaking = async (game) => {
  const hasToJoinMatch = await canJoinAGame();
  if (hasToJoinMatch) {
    await joinMatch(hasToJoinMatch, game);
    //activateGame();
  } else {
    createAndJoinMatch(game);
  }
};



