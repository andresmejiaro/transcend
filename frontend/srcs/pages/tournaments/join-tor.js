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
};
