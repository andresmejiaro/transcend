const infoToNavHome = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/info-me/`;
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
			const usernameH2 = document.getElementById("usernameNav2");
			const avatarImage2 = document.getElementById("avatarImageNav2");

			usernameH.innerHTML = data.user.username;
			usernameH2.innerHTML = data.user.username;

			if (data.user.avatar_url) {
				const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
				avatarImage.src = completeAvatarUrl;
				avatarImage2.src = completeAvatarUrl;
			}
		}
	} catch (error) {
		console.log(error);
	}
};

infoToNavHome();

document.getElementById("logoutButton").addEventListener("click", function (e) {
	e.preventDefault();
	handleLogout();
});

const navbar = document.getElementById("navbarSupportedContent");
const menuButton = document.querySelector(".navbar-toggler");
const navLinks = document.querySelectorAll(".nav-link");

navbar.addEventListener("show.bs.collapse", function () {
	// Navbar is about to collapse
	document.getElementById("navContentClass").classList.remove("mx-auto", "d-flex", "align-items-center");
	document.getElementById("navContentClass").classList.add("text-center");
	document.getElementById("logoutButton").style.margin = "auto";
	document.getElementById("rightNavBall").style.display = "none";
	navbar.style.maxHeight = null;
});


navbar.addEventListener("hidden.bs.collapse", function () {
	// Navbar is about to expand
	document.getElementById("navContentClass").classList.remove("text-center");
	document.getElementById("navContentClass").classList.add("mx-auto", "d-flex", "align-items-center");
	document.getElementById("logoutButton").style.margin = "0";
	document.getElementById("rightNavBall").style.display = "block";
	navbar.style.maxHeight = "100%";

});

function navigateToProfile() {
	window.location.pathname = '/profile';
}

function closeNavbar() {
	if (window.innerWidth > 0 && !navbar.classList.contains("collapsing") && navbar.classList.contains("show")) {
		menuButton.click();
	}
}
window.addEventListener("resize", closeNavbar);

navLinks.forEach((link) => {
	link.addEventListener("click", closeNavbar);
  });