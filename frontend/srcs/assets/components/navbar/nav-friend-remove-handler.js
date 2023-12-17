const removeFriendRequest = async (friend) => {
  sendWebSocketMessage("command", {
    command: "cancel_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
};

