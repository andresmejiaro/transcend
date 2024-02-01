window.DJANGO_API_BASE_URL = "https://localhost:3000";
window.DAPHNE_BASE_URL = "wss://localhost:3000";

function getCSRFCookie() {
	let name = "csrftoken" + "=";
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(";");
	for (let i = 0; i < ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == " ") {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}

const isLogged = () => {
	jwt = sessionStorage.getItem("jwt");

	if (!jwt) return false;
	else return true;
};

function handleLogout() {
	sessionStorage.clear();
	window.location.href = "/";
}

async function makeRequest(useCsrf, url, options, queries) {
	//console.log(useCsrf, url, options, queries);
	if (useCsrf) {
		const csrfToken = getCSRFCookie();
		if (csrfToken) {
			options.headers = {
				...options.headers,
				"X-CSRFToken": csrfToken,
			};
		} else {
			console.log("LADRON ! Cross Site Request Forgery Detected");
			return;
		}

		const JWTToken = sessionStorage.getItem("jwt");
		if (JWTToken) {
			options.headers = {
				...options.headers,
				Authorization: `Bearer ${JWTToken}`,
			};
		} else {
			console.log("LADRON ! JWT not correct");
			return;
		}
	}

	if (queries) {
		url = `${url}?${queries}`;
	}

	const response = await fetch(url, options);

	// COMMENT IN PRODUCTION ONLY "!!!!!!!!!!!!!"
	// if (!response.ok) {
	//   if (!allowedLocations.includes(window.location.pathname)) {
	//     handleLogout();
	//   }
	// }

	const contentType = response.headers.get("content-type");
	if (contentType && contentType.includes("application/json")) {
		return await response.json();
	} else {
		return await response.text(); // Return non-JSON response as text
	}
}

const getUserUsername = () => {
	const jwtToken = sessionStorage.getItem('jwt');
	const [header, payload] = jwtToken.split('.').slice(0, 2);
	const decodedPayload = JSON.parse(atob(payload));
	const username = decodedPayload.username;

	return username
}

const getUserId = async () => {
	try {
		const username = getUserUsername();
		const url = `${window.DJANGO_API_BASE_URL}/api/get_user_id/${username}`;
		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const response = await makeRequest(true, url, options);

		if (response) {
			return response.user_id;
		} else {
			console.error("Error getting user ID:", response.message);
			return null;
		}
	} catch (error) {
		console.error("Error getting user ID:", error.message);
		return null;
	}
};

const getIdFromUsername = async (clientUsername) => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/get_user_id/${clientUsername}`;
		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const response = await makeRequest(true, url, options);

		if (response) {
			return response.user_id;
		} else {
			console.error("Error getting user ID:", response.message);
			return null;
		}
	} catch (error) {
		console.error("Error getting user ID:", error.message);
		return null;
	}
};

const showToast = (title, image, body) => {
	const toastElement = document.getElementById("liveToast");

	const toastTitle = document.getElementById("toast-title-top");
	toastTitle.textContent = title;
	
	const toastBody = document.getElementById("toast-body-index");
	toastBody.textContent = body;

	if (image) {
		const toastImage = document.getElementById("toast-image-top");
		image = `${window.DJANGO_API_BASE_URL}${image}`;
		toastImage.src = image;
	}

	const bsToast = new bootstrap.Toast(toastElement);
	bsToast.show();
};

const showSimpleToast = (body) => {
	const toastElement = document.getElementById("liveSimpleToast");
	
	const toastBody = document.getElementById("toast-simple-body-index");
	toastBody.textContent = body;

	const bsToast = new bootstrap.Toast(toastElement);
	bsToast.show();
};

const getPlayerInfo = async (playerId) => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/info-me-id/${playerId}/`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const data = await makeRequest(true, url, options);

		return data.user;
	} catch (error) {
		console.error(error);
	}
};

const showAlertSuccess = (message) => {
	const alertContainer = document.getElementById("alert-container-success");

	const alertElement = document.createElement("div");
	alertElement.classList.add("alert", "alert-success", "fade", "show");
	alertElement.setAttribute("role", "alert");
	alertElement.innerHTML = `
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    ${message}
  `;

	alertContainer.appendChild(alertElement);

	setTimeout(() => {
		alertElement.classList.remove("show");
	}, 5000);

	alertElement.addEventListener("transitionend", () => {
		alertContainer.removeChild(alertElement);
	});
};

const showAlertDanger = (message) => {
	const alertContainer = document.getElementById("alert-container-danger");

	const alertElement = document.createElement("div");
	alertElement.classList.add("alert", "alert-danger", "fade", "show");
	alertElement.setAttribute("role", "alert");
	alertElement.innerHTML = `
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    ${message}
  `;

	alertContainer.appendChild(alertElement);

	setTimeout(() => {
		alertElement.classList.remove("show");
	}, 5000);

	alertElement.addEventListener("transitionend", () => {
		alertContainer.removeChild(alertElement);
	});
};
