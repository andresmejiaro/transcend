const handleMessage = async (message) => {
    const data = JSON.parse(message);
    //console.log(data);

    switch (data.type) {
        case "list_of_users":
            break;

        case "user_joined":
        case "user_left":
            updateFriendStatus(data);
            break;

        case "list_sent_invites":
            await handleListSentInvites(data);
            break;

        case "list_received_invites":
            await handleListReceivedInvites(data);
            break;


        // FRIENDS REQUESTS
        case "sent_friend_request":
            await handleSendFriendRequest(data);
            break;

        case "recieved_friend_request":
            await handleReceivedFriendRequest(data);
            break;

        case "cancel_friend_request":
            await handleCancelFriendRequest(data);
            break;

        case "friend_request_cancelled":
            await handleCanceledAFriendRequest(data);
            break;

        case "accept_friend_request":
            await handleMeAcceptedFriendRequest(data);
            break;

        case "friend_request_accepted":
            await handleAcceptedFriendRequest(data);
            break;

        case "reject_friend_request":
            await handleMeRejectedFriendRequest(data);
            break;
        
        case "friend_request_rejected":
            await handleRejectedFriendRequest(data);
            break;


        // MATCH REQUESTS
        case "sent_match_invite":
            await handleSentFriendMatchRequest(data);
            break;

        case "recieved_match_invite":
            await handleRecievedFriendMatchRequest(data);
            break;

        // QUEUE && MATCH REQUESTS        
        case "joined_queue":
            await handleJoinedQueue(data);
            break;

        case "left_queue":
            await handleLeftQueue(data);
            break;

        case "found_opponent":
            await handleFoundOpponent(data);
            break;

        case "match_results":
            await handleMatchResults(data);
            break;

        // TOURNAMENT REQUESTS

        default:
            console.warn(`Unhandled message type: ${data.type}`);
    }
};
