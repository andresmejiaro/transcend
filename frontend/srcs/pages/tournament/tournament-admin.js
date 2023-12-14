const startNextRoundTor = async (tourId) => {
  const url = `http://localhost:8000/api/tournament/${tourId}/matchmaking`;
  const options = {
    method: "GET",
    mode: "cors",
    credentials: "include",
  };

  try {
    const data = await makeRequest(true, url, options, "");
    console.log(data);
    if (data.status == "ok") {
      window.location.reload;
    }
  } catch (error) {
    console.log(error);
  }
};

const startNextRound = document.getElementById("start-round-btn");
startNextRound.addEventListener("click", function () {
  startNextRoundTor(tournamentId);
});

function showTournamentAdmin(data) {
  let tournamentAdminDiv = document.getElementById("tournament-admin");
  if (tournamentAdminDiv) {
    tournamentAdminDiv.classList.remove("d-none");
    tournamentAdminDiv.classList.add("d-block");
  }

  if (data.winner) {
    document.getElementById("status-admin").innerHTML =
      "No ADMIN, tournament ended";
  }
}
