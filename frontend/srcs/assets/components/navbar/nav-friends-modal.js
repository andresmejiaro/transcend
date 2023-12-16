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
            <div class="text-center">
              <button class="btn" id="back-modal-btn">
              <i class="bi bi-arrow-return-left" style="font-size: 1.5em; color: white;"></i>
              </button>  
            </div>
        `;

    // Remove existing event listeners
    const btn = document.getElementById("back-modal-btn");
    btn.removeEventListener("click", handleBackButtonClick);
    btn.addEventListener("click", handleBackButtonClick);

    const sendInvitationBtn = document.getElementById("sendInvitationBtn");
    sendInvitationBtn.removeEventListener("click", handleSendInvitationClick);
    sendInvitationBtn.addEventListener("click", handleSendInvitationClick);
  }
};

const handleBackButtonClick = (event) => {
  event.preventDefault();
  const modalBody = document.getElementById("modal-body-friends");
  modalBody.innerHTML = initialContent;
};

const handleSendInvitationClick = async (event) => {
  event.preventDefault();
  const clientUsername = document.getElementById("invitationInput").value;
  const inviteId = await getIdFromUsername(clientUsername);
  if (!inviteId) alert("User not found");
  else {
    inviteFriend(inviteId);
    handleCloseModal();
  }
};

const handleCloseModal = () => {
  const closeModalBtn = document.querySelector(".btn-close.btn-close-white");
  closeModalBtn.click();
  showToast("Invite send succesfully")
}

document
  .getElementById("friendsModal")
  .addEventListener("shown.bs.modal", function (event) {
    event.preventDefault();
    const btn = document.getElementById("friendsModalInvite");
    btn.addEventListener("click", function (event) {
      event.preventDefault();
      handleModalForInvite();
    });
  });
