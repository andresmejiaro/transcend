const getMeSettingsInfo = async () => {
  const username = sessionStorage.getItem("username");

  if (!username) {
    console.log("username not found");
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

    const data = await makeRequest(true, url, options);

    if (data.status === "ok") {
      const usernameElement = document.getElementById("user-username");
      const avatarImage = document.getElementById("avatarImageUser");
      
      usernameElement.innerHTML = data.user.username;
      if (data.user.avatar_url) {
        const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
        avatarImage.src = completeAvatarUrl;
      }
    }
  } catch (error) {
    console.error("Error:", error.message);
  }
};

getMeSettingsInfo();
