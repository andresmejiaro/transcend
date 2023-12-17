const infoToNavHome = async () => {
  const username = sessionStorage.getItem("username");
  if (!username) {
    return;
  }

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/info-me/${username}/`;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options, "");
    if (data.status === "ok") {
      const usernameH = document.getElementById("usernameNav");
      const avatarImage = document.getElementById("avatarImageNav");

      usernameH.innerHTML = data.user.username;

      if (data.user.avatar_url) {
        const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
        avatarImage.src = completeAvatarUrl;
      } else {
        avatarImage.src = "../assets/imgs/default-avatar.jpeg";
      }
    }

  } catch (error) {
    console.log(error);
  }
};

infoToNavHome();

document.getElementById("logoutButton").addEventListener("click", function(e) {
  e.preventDefault();
  handleLogout();
});


const handleCloseModalMsg = (msg) => {
  const closeModalBtn = document.querySelector(".btn-close.btn-close-white");
  closeModalBtn.click();
  showToast(msg)
}

const handleCloseModal = () => {
  const closeModalBtn = document.querySelector(".btn-close.btn-close-white");
  closeModalBtn.click();
}