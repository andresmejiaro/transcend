let notificationInfoSent = [];
let notificationInfoReceived = [];
let invitationListFriendsData = [];
let receivedFriendsNotifications = [];

const updateNotifications = async (data) => {
	const bellSpan = document.getElementById("nav-notification-bell-span");
    if (data && data.length)
        bellSpan.innerHTML = data.length;
    else
        bellSpan.innerHTML = "";
};

const handleListSentInvites = async (data) => {
    if (data.data)
        notificationInfoSent = data.data;
    else
        notificationInfoSent = data;

    const updatedInfo = await Promise.all(notificationInfoSent.map(async (user) => {
        const userInfo = await getPlayerInfo(user.invite_id);
        return {
            ...userInfo,
            id: user.invite_id,
            invite_type: user.invite_type,
        };
    }));
    invitationListFriendsData = updatedInfo;
	await listInvitationFriendsNav();
};

const handleListReceivedInvites = async (data) => {
    if (data.data)
        notificationInfoReceived = data.data;
    else
        notificationInfoReceived = data;
	updateNotifications(notificationInfoReceived);

	const updatedInfo = await Promise.all(notificationInfoReceived.map(async (user) => {
        console.log(user)
        const userInfo = await getPlayerInfo(user.invite_id);
        return {
            ...userInfo,
            id: user.invite_id,
            invite_type: user.invite_type,
        };
    }));
    receivedFriendsNotifications = updatedInfo;
};

const handleCancelFriendRequest = async (data) => {
    const clientIdToRemove = data.data.client_id;
    const newData = invitationListFriendsData.filter(user => user.id !== clientIdToRemove);
    await handleListSentInvites(newData);
    showToast("Invite canceled succesfully")
};


const handleCanceledAFriendRequest = async (data) => {
    const clientIdToRemove = data.data.client_id;
    const canceledUser = receivedFriendsNotifications.find(user => user.id === clientIdToRemove);
    const newData = receivedFriendsNotifications.filter(user => user.id !== clientIdToRemove);
    await handleListReceivedInvites(newData);
    if (canceledUser) {
        const toastMessage = `${canceledUser.username} canceled the friend request`;
        showToast(toastMessage);
    }
};

