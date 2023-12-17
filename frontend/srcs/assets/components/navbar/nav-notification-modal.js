const handleModalForNotifications = async () => {
  function createNotificationElement(data) {
    const notificationContainer = document.getElementById('notifications-list');

    const notificationDiv = document.createElement('div');
    notificationDiv.classList.add('d-flex');
    notificationDiv.classList.add('justify-content-between');

    const descriptionDiv = document.createElement('div');
    const descriptionParagraph = document.createElement('p');
    descriptionParagraph.textContent = `${data.invite_type}: ${data.username}`;
    descriptionDiv.appendChild(descriptionParagraph);

    const actionsDiv = document.createElement('div');
    
    const acceptButton = document.createElement('button');
    acceptButton.type = 'button';
    acceptButton.classList.add('accept-btn');
    acceptButton.innerHTML = '<i class="bi bi-check"></i>';
    acceptButton.addEventListener("click", async () => {
      (async () => {
        await acceptFriendRequest(data);
      })();
    });
    
    const rejectButton = document.createElement('button');
    rejectButton.type = 'button';
    rejectButton.classList.add('reject-btn');
    rejectButton.innerHTML = '<i class="bi bi-x"></i>';
    rejectButton.addEventListener("click", async () => {
      (async () => {
        await rejectFriendRequest(data);
      })();
    });

    actionsDiv.appendChild(acceptButton);
    actionsDiv.appendChild(rejectButton);

    notificationDiv.appendChild(descriptionDiv);
    notificationDiv.appendChild(actionsDiv);

    notificationContainer.appendChild(notificationDiv);
  }

  // Iterate over the sample data and create notification elements
  receivedFriendsNotifications.forEach(createNotificationElement);
}

// const btn = document.getElementById("notificationsModalInvite");
document.getElementById("notificationsModal").addEventListener("shown.bs.modal", function (event) {
    event.preventDefault();
	handleModalForNotifications();
});

// if (notificationInfo.length) {
//   updateNavNotification(notificationInfo.length)
// }
