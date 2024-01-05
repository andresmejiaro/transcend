const handleJoinTor = async (tournamentId, userId) => {
  const url = `${window.DJANGO_API_BASE_URL}/api/tournament/${tournamentId}/`;
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
