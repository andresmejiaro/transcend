
let lobbySocket;

const connectWebSocket = async () => {
  const userId = await getUserId();

  if (lobbySocket && lobbySocket.readyState === WebSocket.OPEN) {
    console.log("WebSocket is already connected.");
    return Promise.resolve(lobbySocket);
  }

  return new Promise((resolve, reject) => {
    lobbySocket = new WebSocket(
      `ws://localhost:8001/ws/lobby2/?client_id=${userId}`
    );

    lobbySocket.addEventListener("open", (event) => {
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

    lobbySocket.onmessage = (event) => {
      parseAndHandleMessage(event.data);
    };

    sendWebSocketMessage("command", {
      command: "list_of_users",
      data: {},
    });
  } catch (error) {
    console.error("Error while connecting to WebSocket:", error.message);
  }
};

const parseAndHandleMessage = async (message) => {
    const data = JSON.parse(message);
    console.log(data)
    if (data.type == "user_joined")
        updateFriendStatus(data);
    else if (data.type == "user_left")
        updateFriendStatus(data);
    else if (data.type == "send_friend_request")
        await updateSendFriendRequests(data);
    else if (data.type == "friend_request")
        await updateReceiveFriendRequests(data);
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
