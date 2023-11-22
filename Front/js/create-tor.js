const tournamentsContainer = document.getElementById("tournaments");

const form = document.getElementById("createTornForm")

const createRequest = async () => {
	console.log("Creating tournament");
	const name = document.getElementById("nameTournament").value;
	try {
		const token = await getCsrfToken();
		const response = await fetch("http://localhost:8000/api/tournament/create/", {
		  method: "POST",
		  mode: "cors",
		  credentials: "include",
		  headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": token,
		  },
		  body: JSON.stringify({
			name: name
		  }),
		});
	
		if (!response.ok) {
		  throw new Error(`HTTP error! Status: ${response.status}`);
		}
	
		const data = await response.json();
	
		console.log(data)
		getListofTournaments();
	} catch (error) {
		console.log(error);
	}
}

const getListofTournaments = async () => {
    console.log("Getting list of tournaments");
    try {
        token = await getCsrfToken();
        const response = await fetch("http://localhost:8000/api/tournament/list/", {
            method: "GET",
            mode: "cors",
            credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": token,
			},
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        // Update the content of the 'tournaments' div with the list of tournaments
        tournamentsContainer.innerHTML = "";
        data.data.forEach(tournament => {
            const tournamentElement = document.createElement("div");
            tournamentElement.innerHTML = `
                Tournament ID: ${tournament.id}, Name: ${tournament.name}
                <button class="delete-button" data-tournament-id="${tournament.id}">Delete</button>
            `;
            tournamentsContainer.appendChild(tournamentElement);
        });

        attachDeleteEventListeners(); // Attach event listeners for delete buttons
    } catch (error) {
        console.log(error);
    }
};

const attachDeleteEventListeners = () => {
    const deleteButtons = document.querySelectorAll(".delete-button");
    deleteButtons.forEach(deleteButton => {
        deleteButton.addEventListener("click", function () {
            const tournamentId = this.dataset.tournamentId;
            deleteTournament(tournamentId);
        });
    });
};

const deleteTournament = async (tournamentId) => {
    try {
        const token = await getCsrfToken();
        const response = await fetch(`http://localhost:8000/api/tournament/delete/${tournamentId}/`, {
            method: "DELETE",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": token,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        console.log(data);
        getListofTournaments(); // Refresh the tournament list after deletion
    } catch (error) {
        console.log(error);
    }
};

getListofTournaments();

form.addEventListener("submit", function (event) {
	console.log("From submitted!");
	event.preventDefault();
	createRequest();
});