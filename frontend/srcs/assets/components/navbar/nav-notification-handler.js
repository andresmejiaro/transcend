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
  handleCloseNotificationModalMsg("Invitation Accepted Succesfully");
};

const rejectFriendRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "reject_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
  handleCloseNotificationModalMsg("Invitation Rejected Succesfully");
};