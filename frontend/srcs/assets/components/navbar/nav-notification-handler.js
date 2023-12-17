const updateNavNotification = (nbr) => {
  const bellSpan = document.getElementById("nav-notification-bell-span");
  bellSpan.innerHTML = nbr;
};

const acceptFriendRequest = async (friend) => {
  console.log(friend)
  console.log(`Accepting invitation for ${friend.username}`);
  sendWebSocketMessage("command", {
    command: "accept_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
  handleCloseModalMsg("Invitation Accepted Succesfully");
};

const rejectFriendRequest = async (friend) => {
  console.log(friend)
  console.log(`Rejecting invitation for ${friend.username}`);
  sendWebSocketMessage("command", {
    command: "reject_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
  handleCloseModalMsg("Invitation Rejected Succesfully");
};