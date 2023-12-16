let torSocket;

const connectWebSocketTor = async (tournamentId) => {
    return new Promise((resolve, reject) => {
        torSocket = new WebSocket(`ws://localhost:8001/ws/touurnament/?id=${tournamentId}`);

        torSocket.addEventListener('open', (event) => {
            console.log('WebSocket connection opened:', event);
            resolve(torSocket);  // Resolve with the WebSocket object
        });

        torSocket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'message') {
                console.log(data.group_name, data.message);
            }
        });

        torSocket.addEventListener('close', (event) => {
            console.log('WebSocket connection closed:', event);
            reject(new Error('WebSocket connection closed.'));
        });

        torSocket.addEventListener('error', (event) => {
            console.error('WebSocket error:', event);
            reject(new Error('WebSocket connection error.'));
        });
    });
};

const handleJoinTorSocket = async (tournamentId) => {
	await connectWebSocket(tournamentId);
};


const handleJoinTor = async (tournamentId, userId) => {
  const url = `http://localhost:8000/api/tournament/${tournamentId}/`;
  const options = {
    method: "PUT",
    mode: "cors",
    credentials: "include",
    body: JSON.stringify({
      players: [userId],
    }),
  };

  try {
    const data = await makeRequest(true, url, options, "");
    if (data.status == "ok") {
      window.location = `/tournament?id=${tournamentId}`;
    }
  } catch (error) {
    console.log(error);
  }
};

const handleJoin = async (tournamentId) => {
	const userId = await getUserId();
	await handleJoinTor(tournamentId, userId);
	// await handleJoinTorSocket(tournamentId);
};
