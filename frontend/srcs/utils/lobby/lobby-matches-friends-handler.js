const handleSentFriendMatchRequest = async (data) => {
  
};

const acceptMatchInvite = async (friendId, matchId) => {
  try {
    const playerId = await getUserId();
    await updateMatchInDb(matchId, playerId);
    console.log(`Accepted match invite from friend with ID: ${friendId}`);
    await new Promise((resolve) => setTimeout(resolve, 500));
    window.location = `/2plygame?matchid=${matchId}`;
  } catch (error) {
    console.error("Error accepting match invite:", error.message);
  }
};

// Function to handle rejecting a match invite
const rejectMatchInvite = async (friendId) => {
  try {
    console.log(`Rejected match invite from friend with ID: ${friendId}`);
  } catch (error) {
    console.error("Error rejecting match invite:", error.message);
  }
};

const showAlertMatchInvite = async (data) => {
  const friendId = data.client_id;
  const matchId = data.match_id;
  const friend = await getPlayerInfo(friendId);

  const alertContainer = document.getElementById("alert-container-success");

  const alertElement = document.createElement("div");
  alertElement.classList.add("alert", "alert-success", "fade", "show");
  alertElement.setAttribute("role", "alert");
  alertElement.innerHTML = `
	  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
	  <p>${friend.username} has invited you to a match!</p>
	  <button class="btn btn-success accept-btn" data-invite-id="${friendId}">Accept</button>
	  <button class="btn btn-danger reject-btn" data-invite-id="${friendId}">Reject</button>
	`;

  alertContainer.appendChild(alertElement);

  const acceptBtn = alertElement.querySelector(".accept-btn");
  acceptBtn.addEventListener("click", async () => {
    const inviteId = acceptBtn.getAttribute("data-invite-id");
    await acceptMatchInvite(inviteId, matchId);
    alertContainer.removeChild(alertElement);
  });

  // Handle reject button click
  const rejectBtn = alertElement.querySelector(".reject-btn");
  rejectBtn.addEventListener("click", async () => {
    const inviteId = rejectBtn.getAttribute("data-invite-id");
    await rejectMatchInvite(inviteId, matchId);
    alertContainer.removeChild(alertElement);
  });

  setTimeout(() => {
    alertElement.classList.remove("show");
    if (alertContainer.contains(alertElement)) {
      alertContainer.removeChild(alertElement);
    }
  }, 15000);

};

const handleRecievedFriendMatchRequest = async (data) => {

  await new Promise(resolve => setTimeout(resolve, 0));
  console.log(data);
  await showAlertMatchInvite(data.data);
};
