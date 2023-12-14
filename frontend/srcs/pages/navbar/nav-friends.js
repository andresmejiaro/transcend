let initialContent; // Variable to store the initial content

const handleInvite = async () => {
  const modalBody = document.getElementById("modal-body-friends");

  // Check if the initial content is already stored
  if (!initialContent) {
    initialContent = modalBody.innerHTML; // Store the initial content
  }

  // Check if the input field is already present
  const isInputVisible = modalBody.querySelector("#invitationInput") !== null;
  if (isInputVisible) {
    // If input is visible, switch back to the initial content
    modalBody.innerHTML = initialContent;
  } else {
    // If input is not visible, show the input and button
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

document.getElementById("friendsModal").addEventListener("shown.bs.modal", function (event) {
    event.preventDefault();
    const btn = document.getElementById("friendsModalInvite");
    btn.addEventListener("click", function (event) {
      event.preventDefault();
      handleInvite();
    });
  });

const inviteFriend = async (inviteId) => {
  const userId = await getUserId();

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/${userId}/addfriend/`;

    const options = {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        friend_id: inviteId,
      }),
    };

    const data = await makeRequest(true, url, options);

    if (data.status === "ok") {
      window.location.href = "/play!";
    }
  } catch (error) {
    console.error("Error:", error.message);
  }
};


const listFriends = async () => {
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

  document.getElementById("friendsModalLabel").innerHTML = "Online: " + nowOnlineFriends;
};
