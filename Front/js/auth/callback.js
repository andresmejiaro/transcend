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
	window.location.href = "/home";
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

	if (response.status === "ok") {
	  sessionStorage.setItem("username", username);
	} else {
	  console.error("Error:", response.message);
	}
  } catch (error) {
	console.error("Error:", error.message);
  }
};

const getInfoMe = async (username) => {
  try {
	const url = `${window.DJANGO_API_BASE_URL}/api/get_user_id/${username}`;
	const response = await makeRequest(true, url);

	if (response) {
	  return response.user_id;
	} else {
	  console.error("Error getting user ID:", response.message);
	  return false;
	}
  } catch (error) {
	console.error("Error getting user ID:", error.message);
	return false;
  }
};

const intrahandler = async (userData) => {
  const exists = await getInfoMe(userData.login);
  if (exists) tryLoginFormPostIntra(userData);
  else {
	await tryFormPostIntra(userData);
	await handleUpload(userData.login, userData.image.link);
	window.location.href = "/home";
  }
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
	document.getElementById("user").innerHTML = userData.displayname;
	intrahandler(userData);
  } catch (error) {
	console.error("Error fetching user information:", error.message);
  }
}

async function handleCallback() {
  // Extract the authorization code from the URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const authorizationCode = urlParams.get("code");

  if (authorizationCode) {
	// Replace with your actual client ID, client secret, and redirect URI
	const clientId =
	  "u-s4t2ud-ca3a07a81bac42c6b896a950e6bcce0a4072c14b72a8aea1e48f732b55dd58e2";
	const clientSecret =
	  "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"; // Replace with your actual client secret
	const redirectUri = "http://localhost:3000/callback";

	const tokenUrl = "https://api.intra.42.fr/oauth/token";

	const response = await fetch(tokenUrl, {
	  method: "POST",
	  headers: {
		"Content-Type": "application/x-www-form-urlencoded",
	  },
	  body: `grant_type=authorization_code&client_id=${clientId}&client_secret=${clientSecret}&code=${authorizationCode}&redirect_uri=${encodeURIComponent(
		redirectUri
	  )}`,
	});

	const tokenData = await response.json();

	getUserInfo(tokenData.access_token);
  }
}

handleCallback();
