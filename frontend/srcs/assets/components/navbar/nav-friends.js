const listInvitationFriendsNav = async () => {
  const invitationListContainer = document.getElementById("friends-invitation-list");
  
  invitationListContainer.innerHTML = "";
  await Promise.all(invitationListFriendsData.map( async (friend) => {
    const friendElement = document.createElement("div");
    friendElement.classList.add("d-flex", "align-items-center");

    const mxElement = document.createElement("div");
    mxElement.classList.add("mx-1");

    const pElement = document.createElement("p");
    pElement.classList.add("pm0");
    pElement.textContent = friend.username;

    const removeButton = document.createElement("button");
    removeButton.classList.add("btn", "btn-danger", "ms-2");
    removeButton.innerHTML = '<i class="bi bi-x"></i> Remove Invitation';
    removeButton.addEventListener("click", async () => {
      (async () => {
        await removeFriendRequest(friend);
      })();
    });

    friendElement.appendChild(mxElement);
    friendElement.appendChild(pElement);
    friendElement.appendChild(removeButton);

    invitationListContainer.appendChild(friendElement);
  }));
};

const handleInviteFriend = async (friend) => {
  console.log("invite to a match", friend);
}


const listFriendsNav = async () => {
  if (nowOnlineFriends) toggleFriendNav(nowOnlineFriends);
  else removeToggleFriendNav();

  const friendsListContainer = document.getElementById("friends-list");
  friendsListContainer.innerHTML = "";

  const sortedFriendList = friendList.sort((a, b) => (b.online ? 1 : -1));
  sortedFriendList.forEach((friend) => {
    const friendElement = document.createElement("div");
    friendElement.classList.add("d-flex", "align-items-center");

    const circleElement = document.createElement("div");
    circleElement.classList.add("rounded-circle", "p-2");
    circleElement.style.width = "15px";
    circleElement.style.height = "15px";
    circleElement.style.background = friend.online ? "#94ba85" : "#fffeee";

    const mxElement = document.createElement("div");
    mxElement.classList.add("mx-1");

    const pElement = document.createElement("p");
    pElement.classList.add("pm0");
    pElement.textContent = friend.username;

    const inviteButton = document.createElement("button");
    inviteButton.type = "button";
    inviteButton.classList.add("btn", "ms-5");
    inviteButton.style = "background: #fffeee; color: #4CA2BB";
    inviteButton.textContent = "Friendly Battle";
  
    inviteButton.addEventListener("click", () => {
      handleInviteFriend(friend);
    });

    friendElement.appendChild(circleElement);
    friendElement.appendChild(mxElement);
    friendElement.appendChild(pElement);
    friendElement.appendChild(inviteButton);

    friendsListContainer.appendChild(friendElement);
  });

  document.getElementById("friendsModalLabel").innerHTML =
    "Online: " + nowOnlineFriends;
};

const friendsIconNav = document.getElementById("nav-friends-icon");
const toggleFriendNav = async (nbrFriendsOnline) => {
  friendsIconNav.src = "./srcs/assets/imgs/friends-online-icon.svg";
};
const removeToggleFriendNav = () => {
  friendsIconNav.src = "./srcs/assets/imgs/friends-icon.svg";
};


const handleCloseFriendsModalMsg = (msg) => {
  const closeModalBtn = document.querySelector(".btn-close.btn-close-white.btn-friends-close");
  closeModalBtn.click();
  showToast(msg)
}

const handleCloseFriendsModal = () => {
  const closeModalBtn = document.querySelector(".btn-close.btn-close-white.btn-friends-close");
  closeModalBtn.click();
}