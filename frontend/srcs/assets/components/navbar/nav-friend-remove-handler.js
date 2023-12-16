const removeFriendRequest = async (friend) => {
  console.log(`Removing invitation for ${friend.username}`);
  console.log(friend)
  sendWebSocketMessage("command", {
    command: "cancel_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
};

