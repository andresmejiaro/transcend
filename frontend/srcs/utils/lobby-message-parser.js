

const parseAndHandleMessage = async (message) => {
    const data = JSON.parse(message);
    console.log(data)
    if (data.type == "user_joined")
        updateFriendStatus(data);
    else if (data.type == "user_left")
        updateFriendStatus(data);
    else if (data.type == "send_friend_request")
        await updateSendFriendRequests(data);
    else if (data.type == "recieved_friend_request")
        await updateReceiveFriendRequests(data);
    else if (data.type == "list_sent_invites")
        await updateNotifications(data);
    else if (data.type == "list_received_invites")
        await updateNotifications(data);
}