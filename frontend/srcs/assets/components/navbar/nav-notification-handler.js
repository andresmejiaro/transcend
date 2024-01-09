const updateNavNotification = (nbr) => {
  const bellSpan = document.getElementById("nav-notification-bell-span");
  if (!nbr || nbr == 0)
    bellSpan.innerHTML = "";
  else
    bellSpan.innerHTML = nbr;

};

const acceptFriendRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "accept_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
  // handleCloseNotificationModalMsg("Invitation Accepted Succesfully");
  handleCloseNotificationModal();
};

const rejectFriendRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "reject_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
  // handleCloseNotificationModalMsg("Invitation Rejected Succesfully");
  handleCloseNotificationModal();
};

const acceptMatchRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "accept_match",
    data: {
      client_id: `${friend.id}`,
      match_id: `99`,
    },
  });
  // handleCloseNotificationModalMsg("Invitation Accepted Succesfully");
  handleCloseNotificationModal();
};

const rejectMatchRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "reject_match",
    data: {
      client_id: `${friend.id}`,
      match_id: `99`,
    },
  });
  // handleCloseNotificationModalMsg("Invitation Rejected Succesfully");
  handleCloseNotificationModal();
};