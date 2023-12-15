
let lobbySocket;

const connectWebSocket = async () => {
  const userId = await getUserId();

  if (lobbySocket && lobbySocket.readyState === WebSocket.OPEN) {
    console.log("WebSocket is already connected.");
    return Promise.resolve(lobbySocket);
  }

  return new Promise((resolve, reject) => {
    lobbySocket = new WebSocket(
      `ws://localhost:8001/ws/lobby/?client_id=${userId}`
    );

    lobbySocket.addEventListener("open", (event) => {
      console.log("WebSocket connection opened:", event);
      sendWebSocketMessage('command', {
        command: "get_user_info",
        data: {},
      });
      resolve(lobbySocket); // Resolve with the WebSocket object
    });

    lobbySocket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "message") {
        console.log(data.group_name, data.message);
      }
    });

    lobbySocket.addEventListener("close", (event) => {
      console.log("WebSocket connection closed:", event);
      reject(new Error("WebSocket connection closed."));
    });

    lobbySocket.addEventListener("error", (event) => {
      console.error("WebSocket error:", event);
      reject(new Error("WebSocket connection error."));
    });
  });
};

const getOnlineUsers = async () => {
  try {
    await connectWebSocket();

    lobbySocket.addEventListener("message", (event) => {
      parseAndHandleMessage(event.data);
    });

    lobbySocket.addEventListener("user_left", (event) => {
      console.log(event)
      console.log(event.data)
      // parseAndHandleMessage(event.data);
    });

    lobbySocket.onmessage = (event) => {
      parseAndHandleMessage(event.data);
    };

    
    sendWebSocketMessage("command", {
      command: "get_website_user_list",
      data: {},
    });
  } catch (error) {
    console.error("Error while connecting to WebSocket:", error.message);
  }
};

const parseAndHandleMessage = async (message) => {
    const data = JSON.parse(message);
    console.log("ws", data)
    if (data.data)
        updateFriendStatus(data.data);
}

const sendWebSocketMessage = (messageType, payload) => {
  if (lobbySocket && lobbySocket.readyState === WebSocket.OPEN) {
    lobbySocket.send(
      JSON.stringify({
        type: messageType,
        ...payload,
      })
    );
  } else {
    console.error("WebSocket is not in the OPEN state.");
    // Handle the case where WebSocket is not open (e.g., display a user-friendly message)
  }
};

const joinLobby = async () => {
  try {
    await getOnlineUsers();
  } catch (error) {
    console.error("Error while connecting to WebSocket:", error.message);
    // Handle error as needed (e.g., display an error message to the user)
  }
};
