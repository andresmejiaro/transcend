const urlParams = new URLSearchParams(window.location.search);
const tournamentId = urlParams.get("id");

const getTournamentInfo = async (tournamentId) => {
  const url = `${window.DJANGO_API_BASE_URL}/api/tournament/${tournamentId}/`;
  const options = {
    method: "GET",
    mode: "cors",
    credentials: "include",
  };

  try {
    let data = await makeRequest(true, url, options, "");
    if (data.status == "ok") {
	  data = data.data;

	  changeTournamentName(data.name)
	  changeTournamentRound(data.round)

	  let winner = false;
		console.log(data)
	  if (data.winner !== null)
		winner = true
	  changeTournamentStatus(winner)


	  await changeParticipants(data.players)

      const userId = await getUserId();
      if (data.tournament_admin == userId) {
        showTournamentAdmin(data);
      }
    }
  } catch (error) {
    console.log(error);
  }
};

// getTournamentInfo(tournamentId);
joinTournamentLobby(tournamentId);