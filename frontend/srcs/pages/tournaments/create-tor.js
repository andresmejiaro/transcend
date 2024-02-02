// const tournamentsContainer = document.getElementById("tournaments");
// const matchesContainer = document.getElementById("matches");
// const usersContainer = document.getElementById("user");

// const form = document.getElementById("createTornForm");


const createRequest = async () => {
  const userId = await getUserId();
  const name = document.getElementById("nameTournament").value;
  try {
    
    const url =
    `${window.DJANGO_API_BASE_URL}/api/tournament/create/` +
    "?username=" + username
    const options = {
      method: "POST",
      mode: "cors",
      credentials: "include",
      body: JSON.stringify({
        name: name,
        "players": [userId],
        "tournament_admin": userId,
      }),
    };
    
    const data = await makeRequest(true, url, options, "");
    if (data.status == "ok") {
      // window.location = `/tournament?id=${tournamentId}`
      getListofTournaments();
      addEventListenerButtons();
    }
  } catch (error) {
    console.log(error);
  }
};

const getListofTournaments = async () => {
  // console.log("Getting list of tournaments");
  try {
    const token = sessionStorage.getItem("jwt");
    if (!token) {
      console.log("JWT token not found");
      return;
    }
    const username = getUserUsername();
    if (!username) {
      console.log("username not found");
      return;
    }

    const url =
      `${window.DJANGO_API_BASE_URL}/api/tournament/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    if (data.data.length === 0) {
      tournamentsContainer.appendChild(tournamentElement);
    } else {
      // Update the content of the 'tournaments' div with the list of tournaments
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
                  <img src="./srcs/assets/buttons/join-tournament.svg" alt="" class="img-fluid">
                </button> 
              </div>        
            </div>
          `;
          tournamentsContainer.appendChild(tournamentElement);
        }
      });
    }
    attachDeleteEventListeners(); // Attach event listeners for delete buttons
    addEventListenerButtons();
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
    const username = getUserUsername();
    if (!username) {
      console.log("username not found");
      return;
    }

    const url =
      `${window.DJANGO_API_BASE_URL}/api/match/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    // Update the content of the 'matches' div with the list of matches
    matchesContainer.innerHTML = "";
    data.data.forEach((match) => {
      const matchElement = document.createElement("div");
      matchElement.innerHTML = `
                <p>Match ID: ${match.id}</p>
                <p>Player 1: ${match.player1.username}</p>
                <p>Player 2: ${match.player2.username}</p>
                <p>Scores: ${match.player1_score} - ${match.player2_score}</p>
                <p>Active: ${match.active ? "Yes" : "No"}</p>
                <button class="delete-button" data-match-id="${
                  match.id
                }">Delete Match</button>
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

    const url =
      `${window.DJANGO_API_BASE_URL}/api/user/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    // Update the content of the 'users' div with the list of users
    usersContainer.innerHTML = "";
    data.data.forEach((user) => {
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

const attachDeleteEventListeners = () => {
  const deleteButtons = document.querySelectorAll(".delete-button");
  deleteButtons.forEach((deleteButton) => {
    deleteButton.addEventListener("click", function () {
      if (this.dataset.tournamentId) {
        const tournamentId = this.dataset.tournamentId;
        deleteTournament(tournamentId);
      } else if (this.dataset.matchId) {
        const matchId = this.dataset.matchId;
        deleteMatch(matchId);
      } else if (this.dataset.userId) {
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
    }
    const username = getUserUsername();
    if (!username) {
      console.log("username not found");
      return;
    }

    const url =
      `${window.DJANGO_API_BASE_URL}/api/tournament/${tournamentId}/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "DELETE",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    getListofTournaments();
  } catch (error) {
    console.log(error);
  }
};

const deleteMatch = async (matchId) => {
  try {
    const token = sessionStorage.getItem("jwt");
    if (!token) {
      console.log("JWT token not found");
      return;
    }
    const username = getUserUsername();
    if (!username) {
      console.log("username not found");
      return;
    }

    const url =
      `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "DELETE",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    getListofMatches();
  } catch (error) {
    console.log(error);
  }
};

const deleteUser = async (userId) => {
  try {
    const token = sessionStorage.getItem("jwt");
    if (!token) {
      console.log("JWT token not found");
      return;
    }
    const username = getUserUsername();
    if (!username) {
      console.log("username not found");
      return;
    }

    const url =
      `${window.DJANGO_API_BASE_URL}/api/user/${userId}/` +
      "?token=" +
      token +
      "&username=" +
      username;
    const options = {
      method: "DELETE",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");

    getListofUsers();
  } catch (error) {
    console.log(error);
  }
};

// getListofUsers();
// getListofMatches();
// getListofTournaments();

// form.addEventListener("submit", function (event) {
//   event.preventDefault();
//   console.log("From submitted!");
//   let closeButton = document.querySelector("#exampleModal .btn-close");
//   closeButton.click();
//   createRequest();
// });
