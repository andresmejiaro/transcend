let initialContent; // Variable to store the initial content

const handleInvite = async () => {
  const modalBody = document.getElementById("modal-body-friends");

  if (!initialContent) {
    initialContent = modalBody.innerHTML;
  }

  const isInputVisible = modalBody.querySelector("#invitationInput") !== null;
  if (isInputVisible) {
    modalBody.innerHTML = initialContent;
  } else {
    modalBody.innerHTML = `
            <input type="text" id="invitationInput" placeholder="Enter friend's name">
            <button id="sendInvitationBtn" class="btn btn-success">Send Invitation</button>
        `;

    const sendInvitationBtn = document.getElementById("sendInvitationBtn");
    sendInvitationBtn.addEventListener(
      "click",
      (function () {
        return async function (event) {
          event.preventDefault();
          const clientUsername =
            document.getElementById("invitationInput").value;
          const inviteId = await getIdFromUsername(clientUsername);
          if (!inviteId) alert("User not found");
          else inviteFriend(inviteId);
        };
      })()
    );
  }
};

document
  .getElementById("friendsModal")
  .addEventListener("shown.bs.modal", function (event) {
    event.preventDefault();
    const btn = document.getElementById("friendsModalInvite");
    btn.addEventListener("click", function (event) {
      event.preventDefault();
      handleInvite();
    });
  });

const listInvitationFriends = () => {
  const invitationListContainer = document.getElementById("friends-invitation-list");
  invitationListContainer.innerHTML = "";
  let invitationListFriends = []
  invitationListFriends.forEach((friend) => {
    const friendElement = document.createElement("div");
    friendElement.classList.add("d-flex", "align-items-center");

    const mxElement = document.createElement("div");
    mxElement.classList.add("mx-1");

    const pElement = document.createElement("p");
    pElement.classList.add("pm0");
    pElement.textContent = friend.username;

    friendElement.appendChild(circleElement);
    friendElement.appendChild(mxElement);
    friendElement.appendChild(pElement);

    friendsListContainer.appendChild(friendElement);
  });
}

const handleInviteSent = () => {
  const modalBody = document.getElementById("modal-body-friends");
  const isInputVisible = modalBody.querySelector("#invitationInput") !== null;
  if (isInputVisible) {
    modalBody.innerHTML = initialContent;
  }
  listInvitationFriends();
};

const inviteFriend = async (inviteId) => {
  console.log("inviting: ", inviteId);
  sendWebSocketMessage("command", {
    command: "send_friend_request",
    data: {
      client_id: inviteId,
    },
  });
  handleInviteSent();
};

const listFriends = async () => {
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

    friendElement.appendChild(circleElement);
    friendElement.appendChild(mxElement);
    friendElement.appendChild(pElement);

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
