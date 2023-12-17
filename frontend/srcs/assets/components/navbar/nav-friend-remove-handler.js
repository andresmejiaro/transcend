const removeFriendRequest = async (friend) => {
  console.log(friend)
  console.log(`Removing invitation for ${friend.username}`);
  sendWebSocketMessage("command", {
    command: "cancel_friend_request",
    data: {
      client_id: `${friend.id}`,
    },
  });
};

