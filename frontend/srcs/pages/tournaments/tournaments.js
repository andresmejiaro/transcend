const tournamentsContainer = document.getElementById("tournaments");
const matchesContainer = document.getElementById("matches");
const usersContainer = document.getElementById("user");

const getListofTournaments = async () => {
	console.log("HEHEHE")
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/tournament/`;
		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const data = await makeRequest(true, url, options, "");
		console.log(data);
		if (data.data.length === 0) {
			const tournamentElement = document.createElement("div");
			tournamentElement.innerHTML = `<p>There are currently no tournaments</p>`;
			tournamentsContainer.appendChild(tournamentElement);
		} else {
			tournamentsContainer.innerHTML = "";
			const userId = await getUserId();
			data.data.forEach((tournament) => {
				const userIsInTournament = tournament.players.includes(userId);
				if (userIsInTournament) {
					const tournamentElement = document.createElement("div");

					tournamentElement.classList.add(userIsInTournament ? "user-in-tournament" : "user-not-in-tournament");

					tournamentElement.innerHTML = `
			  <div class="d-flex justify-content-between align-items-center py-3 m-1">
				<div class="d-flex align-items-center">
				  <i class="bi bi-person me-2"></i>
				  <p class="m-0">${tournament.name}</p>
				</div>
				<div class="d-flex align-items-center">
				  <p style="margin-bottom: 0 !important; margin-right: 8px;">${tournament.players.length}</p>
				  <img src="./srcs/assets/imgs/adri.svg" style="margin-right: 8px;" />
				  <button type="button" class="btn join-tournament-btn" data-tournament-id="${tournament.id}">
					<img src="./srcs/assets/buttons/join-tournament.svg" alt="" class="img-fluid">
				  </button> 
				</div>        
			  </div>
			`;
					tournamentsContainer.appendChild(tournamentElement);
				}
			});
			data.data.forEach((tournament) => {
				const userIsInTournament = tournament.players.includes(userId);
				if (!userIsInTournament) {
					const tournamentElement = document.createElement("div");

					tournamentElement.classList.add(userIsInTournament ? "user-in-tournament" : "user-not-in-tournament");

					tournamentElement.innerHTML = `
			  <div class="d-flex justify-content-between align-items-center py-3 m-1">
				<div class="d-flex align-items-center">
				  <i class="bi bi-person me-2"></i>
				  <p class="m-0">${tournament.name}</p>
				</div>
				<div class="d-flex align-items-center">
				  <p style="margin-bottom: 0 !important; margin-right: 8px;">${tournament.players.length}</p>
				  <img src="./srcs/assets/imgs/adri.svg" style="margin-right: 8px;" />
				  <button type="button" class="btn join-tournament-btn" data-tournament-id="${tournament.id}">
					<span class="button-join-tor-text">JOIN</span>
					</button>
				</div>        
			  </div>
			`;
					tournamentsContainer.appendChild(tournamentElement);
				}
			});
		}
		addEventListenerButtons();
	} catch (error) {
		console.log(error);
	}
};

getListofTournaments();

const addEventListenerButtons = () => {
	let buttons = document.querySelectorAll('.join-tournament-btn');
	buttons.forEach(function(button) {
	  button.addEventListener('click', function() {
		var tournamentId = this.getAttribute('data-tournament-id');
		// console.log("CLICK ", tournamentId)
		handleJoin(tournamentId);
	  });
	});
  }