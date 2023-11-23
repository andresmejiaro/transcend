const getMeInfo = async () => {
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
      const usernameH = document.getElementById("user-username");
      const avatarImage = document.getElementById("avatarImage");
  
      usernameH.innerHTML =  data.user.username;
  
      if (data.user.avatar_url) {
        const completeAvatarUrl = `http://localhost:8000${data.user.avatar_url}`;
        avatarImage.src = completeAvatarUrl;
    }
      
    }
  };
  
getMeInfo();

