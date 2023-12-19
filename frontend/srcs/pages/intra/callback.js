const tryLoginFormPostIntra = async (data) => {
  const username = data.login;
  const password = "AUTH0_USER_NO_PASSWORD";

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/login/`;

    const response = await makeRequest(false, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    sessionStorage.setItem("username", username);
    sessionStorage.setItem("jwt", response.token);
  } catch (error) {
    console.error("Error:", error.message);
    displayError("Invalid credentials. Please try again.");
  }
};

async function handleUpload(username, avatarUrl) {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/update-avatar/${username}/`;

    const response = await makeRequest(true, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ avatar_url: avatarUrl }),
    });

    // Optionally log or handle the response data if needed
    // console.log(response);
  } catch (error) {
    console.error("Error:", error.message);
    alert("An error occurred while uploading the avatar.");
  }
}

const tryFormPostIntra = async (data) => {
  const username = data.login;
  const fullname = data.displayname;
  const placeholderPassword = "AUTH0_USER_NO_PASSWORD";
  const email = data.email;

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/signup/`;

    const response = await makeRequest(false, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        fullname: fullname,
        email: email,
        password: placeholderPassword,
      }),
    });

    if (response.status == "ok") {
      sessionStorage.setItem("username", username);
      sessionStorage.setItem("jwt", response.token);
    } else {
      console.error("Error:", response.message);
    }
  } catch (error) {
    console.error("Error:", error.message);
  }
};

const getInfoMe = async (username) => {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/exists/${username}`;
    const response = await makeRequest(false, url);

    return response;
  } catch (error) {
    console.error("Error getting user ID:", error.message);
    return false;
  }
};

const getInfoUsernameFullname = async (userData) => {
  try {
    const username = userData.login;
    const fullname = userData.displayname;
    const url = `${window.DJANGO_API_BASE_URL}/api/user/exists/${username}/${fullname}/`;
    const response = await makeRequest(false, url);
    return response;
  } catch (error) {
    console.error("Error getting user ID:", error.message);
    return false;
  }
};

const intrahandler = async (userData) => {
  const usernameExists = await getInfoMe(userData.login);
  if (!usernameExists.error) {
    const usernameTakenNotIntra = await getInfoUsernameFullname(userData);
    if (usernameTakenNotIntra.error) {
      showAlertDanger("Username taken, create a user")
      setTimeout(function () {
        window.location.href = '/home';
      }, 1000);
      return;
    }
    await tryLoginFormPostIntra(userData);
  }
  else {
    await tryFormPostIntra(userData);
    await handleUpload(userData.login, userData.image.link);
  }
  window.location.href = "/play!";
};

async function getUserInfo(accessToken) {
  const apiUrl = "https://api.intra.42.fr/v2/me";
  let userData = "";
  try {
    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    userData = await response.json();
    intrahandler(userData);
  } catch (error) {
    console.error("Error fetching user information:", error.message);
  }
}

async function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const authorizationCode = urlParams.get("code");

  if (authorizationCode) {
    const clientId ="u-s4t2ud-8a3d7b6ac3c28259758ac83a1d842d4a448f4bc3d0afadbc90eb50f6c29083c7";
    const clientSecret ="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";
    const redirectUri = "http://localhost:3000/intra";

    const tokenUrl = "https://api.intra.42.fr/oauth/token";
	try {
		const response = await fetch(tokenUrl, {
		  method: "POST",
		  mode: "cors",
		  credentials: "include",
		  headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		  },
		  body: `grant_type=authorization_code&client_id=${clientId}&client_secret=${clientSecret}&code=${authorizationCode}&redirect_uri=${encodeURIComponent(redirectUri)}`,
		});
	  
		if (!response.ok) {
		  throw new Error(`HTTP error! Status: ${response.status}`);
		}
	  
		const tokenData = await response.json();
		getUserInfo(tokenData.access_token);
	  } catch (error) {
		console.error("Error during token exchange:", error);
	  }
  }
}

handleCallback();
