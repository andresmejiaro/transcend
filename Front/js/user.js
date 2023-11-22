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





// document.getElementById('updateAvatarForm').addEventListener('submit', function (e) {
//     e.preventDefault();
//     changeAvatar();
// }, false);

// const changeAvatar = async () => {
//     console.log("HELO")
//     const avatarInput = document.getElementById('avatar');
//     const token = sessionStorage.getItem("jwt");

//     if (!token) {
//         console.log("JWT token not found");
//         return;
//     }

//     const username = sessionStorage.getItem("username");

//     if (!username) {
//         console.log("username not found");
//         return;
//     }

//     const url = `http://localhost:8000/api/user/update-avatar/${username}/?token=${token}`;

//     const formData = new FormData();
//     formData.append('avatar', avatarInput.files[0]);

//     const options = {
//         method: "POST",
//         mode: "cors",
//         credentials: "include",
//         body: formData,
//     };

//     try {
//         const response = await makeRequest(url, options);

//         console.log(response)
//         const msg = document.getElementById('avatarMsg')

//         if (response.status === 'ok') {
//             msg.innerText = response.message;
//             msg.classList.add('text-success');
//         } else {
//             msg.innerText = response.error;
//             msg.classList.add('text-error');
//         }
//     } catch (error) {
//         console.error("Error:", error);
//     }
// };