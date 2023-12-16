let initialContent; // Variable to store the initial content

const handleModalForInvite = async () => {
  const modalBody = document.getElementById("modal-body-friends");

  if (!initialContent) {
    initialContent = modalBody.innerHTML;
  }

  const isInputVisible = modalBody.querySelector("#invitationInput") !== null;
  if (isInputVisible) {
    modalBody.innerHTML = initialContent;
  } else {
    modalBody.innerHTML = `
            <div class="text-center">
            <div class="mt-2"><input type="text" id="invitationInput" placeholder="Enter friend's name"></div>
            <div class="mt-3"><button id="sendInvitationBtn" class="btn btn-success">Send Invitation</button></div>
            </div>
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
    handleModalForInvite();
  });
});