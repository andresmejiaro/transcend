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


var navbar = document.getElementById('navbarSupportedContent');

    navbar.addEventListener('show.bs.collapse', function () {
      // Navbar is about to collapse
      document.getElementById('navContentClass').classList.remove('mx-auto', 'd-flex', 'align-items-center');
      document.getElementById('navContentClass').classList.add('text-center');
      document.getElementById('logoutButton').style.margin = "auto";
      document.getElementById('rightNavBall').style.display = "none";
      document
    });

    navbar.addEventListener('hidden.bs.collapse', function () {
      // Navbar is about to expand
      document.getElementById('navContentClass').classList.remove('text-center');
      document.getElementById('navContentClass').classList.add('mx-auto', 'd-flex', 'align-items-center');
      document.getElementById('logoutButton').style.margin = "0";
      document.getElementById('rightNavBall').style.display = "block";
    });