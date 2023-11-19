const getCsrfToken = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/user/csrftoken/", {
      method: "GET",
      credentials: "include",
    });
    const data = await response.json();
    if (data.token) {
      return data.token;
    } else {
      console.error("Error:", data.message);
      return null;
    }
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
};

// CLARAMENTE MEJORAR ESTO!!!!!!!!!
const isLogged = () => {
  username = sessionStorage.getItem("username");
  token = sessionStorage.getItem("jwt");
  if (!username || !token) return false;
  else return true;
};

function handleLogout() {
	sessionStorage.clear();
	window.location.href = "/";
}

// Pendiente a mejorar
// async function makeRequest(url, options) {
//     const csrfToken = await getCsrfToken();
// 	console.log(csrfToken)
//     if (csrfToken) {
//         options.headers = {
//             ...options.headers,
//             'X-CSRFToken': csrfToken,
//         };
//     }

//     const response = await fetch(url, options);
//     const data = await response.json();

//     console.log(data);

//     return data;
// }
