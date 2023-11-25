const tournamentsContainer = document.getElementById("tournaments");
const matchesContainer = document.getElementById("matches");
const usersContainer = document.getElementById('user');


const form = document.getElementById("createTornForm");

const createRequest = async () => {
    console.log("Creating tournament");
    const name = document.getElementById("nameTournament").value;
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

        const url = "http://localhost:8000/api/tournament/create/" + "?token=" + token + "&username=" + username;
        const options = {
            method: "POST",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name
            }),
        };

        await makeRequest(url, options);

        // Refresh the list of tournaments after creating a new one
        getListofTournaments();
    } catch (error) {
        console.log(error);
    }
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

        const url = "http://localhost:8000/api/tournament/" + "?token=" + token + "&username=" + username;
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        // Update the content of the 'tournaments' div with the list of tournaments
        tournamentsContainer.innerHTML = "";
        data.data.forEach(tournament => {
            const tournamentElement = document.createElement("div");
            tournamentElement.innerHTML = `
                <p>Tournament ID: ${tournament.id}, Name: ${tournament.name}</p>
                <button class="delete-button" data-tournament-id="${tournament.id}">Delete Tournament</button>
            `;
            tournamentsContainer.appendChild(tournamentElement);
        });

        attachDeleteEventListeners(); // Attach event listeners for delete buttons
    } catch (error) {
        console.log(error);
    }
};

const getListofMatches = async () => {
    console.log("Getting list of matches");
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

        const url = "http://localhost:8000/api/match/" + "?token=" + token + "&username=" + username;
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        // Update the content of the 'matches' div with the list of matches
        matchesContainer.innerHTML = "";
        data.data.forEach(match => {
            const matchElement = document.createElement("div");
            matchElement.innerHTML = `
                <p>Match ID: ${match.id}</p>
                <p>Player 1: ${match.player1.username}</p>
                <p>Player 2: ${match.player2.username}</p>
                <p>Scores: ${match.player1_score} - ${match.player2_score}</p>
                <p>Active: ${match.active ? 'Yes' : 'No'}</p>
                <button class="delete-button" data-match-id="${match.id}">Delete Match</button>
            `;
            matchesContainer.appendChild(matchElement);
        });

        attachDeleteEventListeners(); // Attach event listeners for delete buttons
    } catch (error) {
        console.log(error);
    }
};

const getListofUsers = async () => {
    console.log("Getting list of users");
    try {
        const token = sessionStorage.getItem("jwt");
        if (!token) {
            console.log("JWT token not found");
            return;
        }

        const url = "http://localhost:8000/api/user/" + "?token=" + token + "&username=" + username;
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        // Update the content of the 'users' div with the list of users
        usersContainer.innerHTML = "";
        data.data.forEach(user => {
            const userElement = document.createElement("div");
            userElement.innerHTML = `
                <p>User ID: ${user.id}</p>
                <p>Username: ${user.username}</p>
                <p>Email: ${user.email}</p>
                <p>First Name: ${user.first_name}</p>
                <p>Last Name: ${user.last_name}</p>
                <button class="delete-button" data-user-id="${user.id}">Delete User</button>
            `;
            usersContainer.appendChild(userElement);
        });

        attachDeleteEventListeners(); // Attach event listeners for delete buttons
    } catch (error) {
        console.log("Error:", error);
    }
};

const attachDeleteEventListeners = () => {
    const deleteButtons = document.querySelectorAll(".delete-button");
    deleteButtons.forEach(deleteButton => {
        deleteButton.addEventListener("click", function () {
            if (this.dataset.tournamentId) {
                const tournamentId = this.dataset.tournamentId;
                deleteTournament(tournamentId);
            } else if (this.dataset.matchId) {
                const matchId = this.dataset.matchId;
                deleteMatch(matchId);
            }
            else if (this.dataset.userId) {
                const userId = this.dataset.userId;
                deleteUser(userId);
            }
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

        const url = `http://localhost:8000/api/tournament/${tournamentId}/` + "?token=" + token + "&username=" + username;
        const options = {
            method: "DELETE",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        getListofTournaments();
    }
    catch (error) {
        console.log(error);
    };
};

const deleteMatch = async (matchId) => {
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

        const url = `http://localhost:8000/api/match/${matchId}/` + "?token=" + token + "&username=" + username;
        const options = {
            method: "DELETE",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        getListofMatches();
    }
    catch (error) {
        console.log(error);
    };
}

const deleteUser = async (userId) => {
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

        const url = `http://localhost:8000/api/user/${userId}/` + "?token=" + token + "&username=" + username;
        const options = {
            method: "DELETE",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const data = await makeRequest(url, options);

        getListofUsers();
    }
    catch (error) {
        console.log(error);
    };
}

getListofUsers();
getListofMatches();
getListofTournaments();

form.addEventListener("submit", function (event) {
	console.log("From submitted!");
	event.preventDefault();
	createRequest();
});