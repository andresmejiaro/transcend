let initialContent; // Variable to store the initial content

const handleInvite = async () => {
    const modalBody = document.getElementById('modal-body-friends');

    // Check if the initial content is already stored
    if (!initialContent) {
        initialContent = modalBody.innerHTML; // Store the initial content
    }

    // Check if the input field is already present
    const isInputVisible = modalBody.querySelector('#invitationInput') !== null;
    if (isInputVisible) {
        // If input is visible, switch back to the initial content
        modalBody.innerHTML = initialContent;
    } else {
        // If input is not visible, show the input and button
        modalBody.innerHTML = `
            <input type="text" id="invitationInput" placeholder="Enter friend's name">
            <button id="sendInvitationBtn" class="btn btn-success">Submit</button>
        `;

        // Add event listener for the new button
        const sendInvitationBtn = document.getElementById('sendInvitationBtn');
        sendInvitationBtn.addEventListener('click', function (event) {
            event.preventDefault();
            // Handle the logic for sending the invitation
            console.log('Invitation sent to:', document.getElementById('invitationInput').value);
        });
    }
};

document.getElementById('friendsModal').addEventListener('shown.bs.modal', function (event) {
    event.preventDefault();
    const btn = document.getElementById("friendsModalInvite");
    btn.addEventListener("click", function (event) {
        event.preventDefault();
        handleInvite();
    });
});
