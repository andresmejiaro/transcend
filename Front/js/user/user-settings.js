document.getElementById('updateAvatarForm').addEventListener('submit', function (e) {
    e.preventDefault();
    changeAvatar();
}, false);

const changeAvatar = async () => {
    const avatarInput = document.getElementById('avatar');
    const token = sessionStorage.getItem("jwt");

    if (!token) {
        console.log("JWT token not found");
        return;
    }

    const username = sessionStorage.getItem("username");

    if (!username) {
        console.log("username not found");
        return;
    }

    const url = `http://localhost:8000/api/user/update-avatar/${username}/?token=${token}`;

    const formData = new FormData();
    formData.append('avatar', avatarInput.files[0]);

    const options = {
        method: "POST",
        mode: "cors",
        credentials: "include",
        body: formData,
    };

    try {
        const response = await makeRequest(url, options);

        console.log(response)
        const msg = document.getElementById('avatarMsg')

        if (response.status === 'ok') {
            msg.innerText = response.message;
            msg.classList.add('text-success');
        } else {
            msg.innerText = response.error;
            msg.classList.add('text-error');
        }
    } catch (error) {
        console.error("Error:", error);
    }
};


const getMeSettingsInfo = async () => {
    const token = sessionStorage.getItem("jwt");
    if (!token) {
      console.log("JWT token not found");
      return;
    }
    const username = sessionStorage.getItem("username");
    if (!username) {
      console.log("username not found");
      return;
    }
    const url = "http://localhost:8000/api/user/info-me-jwt/" + "?token=" + token + "&username=" + username;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const data = await makeRequest(url, options);
    if (data.status == "ok") {
      const username = document.getElementById("userSettingsUsername");
	  const fullname = document.getElementById("userSettingsFullname");
	  const email = document.getElementById("userSettingsEmail");
      const avatarImage = document.getElementById("avatarImageUserSettings");
      username.placeholder =  data.user.username;
	  fullname.placeholder = data.user.fullname;
	  email.placeholder = data.user.email;
      if (data.user.avatar_url) {
        const completeAvatarUrl = `http://localhost:8000${data.user.avatar_url}`;
        avatarImage.src = completeAvatarUrl;
    }
      
    }
  };
  
getMeSettingsInfo();