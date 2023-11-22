const tournamentsContainer = document.getElementById("tournaments");

const form = document.getElementById("createTornForm")

const createRequest = async () => {
    console.log("Creating tournament");
    const name = document.getElementById("nameTournament").value;
    const theDate = document.getElementById("dateTournament").value;
    const theEndDate = document.getElementById("endTournament").value;

    const token = sessionStorage.getItem("jwt");
    if (!token) {
        console.log("JWT token not found");
        return;
    }
    const username = sessionStorage.getItem("username");
    if (!username) {
        console.log("username not found");
        return;
    }

    csrfToken = await getCsrfToken();
    const response = await fetch("http://localhost:8000/api/tournament/create/" + "?token=" + token + "&username=" + username, {
        method: "POST",
        mode: "cors",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
            name: name,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.status === "ok") {
            sessionStorage.setItem("name", name);
            sessionStorage.setItem("date", theDate);
            sessionStorage.setItem("endDate", theEndDate);
            window.location.href = "/create-tournaments";
        } else {
            console.error("Error:", data.message);
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
};


const getListofTournaments = async () => {
    console.log("Getting list of tournaments");
    try {
        const token = sessionStorage.getItem("jwt");
        if (!token) {
            console.log("JWT token not found");
            return;
        }
        const username = sessionStorage.getItem("username");
        if (!username) {
            console.log("username not found");
            return;
        }

        const url = "http://localhost:8000/api/tournament/list/" + "?token=" + token + "&username=" + username;
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };
        console.log(token)
        console.log(username)
        
        const data = await makeRequest(url, options);

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
        const token = sessionStorage.getItem("jwt");
        if (!token) {
            console.log("JWT token not found");
            return;
        };
        const username = sessionStorage.getItem("username");
        if (!username) {
            console.log("username not found");
            return;
        };

        const url = `http://localhost:8000/api/tournament/delete/${tournamentId}/` + "?token=" + token + "&username=" + username;
        const options = {
            method: "DELETE",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };
        console.log(token)
        console.log(username)

        const data = await makeRequest(url, options);

        getListofTournaments();
    }
    catch (error) {
        console.log(error);
    };
};

getListofTournaments();

form.addEventListener("submit", function (event) {
	console.log("From submitted!");
	event.preventDefault();
	createRequest();
});