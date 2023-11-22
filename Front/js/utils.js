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

async function makeRequest(url, options) {
  const csrfToken = await getCsrfToken();
  if (csrfToken) {
    options.headers = {
      ...options.headers,
      "X-CSRFToken": csrfToken,
    };
  }

  const response = await fetch(url, options);
  

  if (!response.ok) {
    console.log(response)
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return await response.json();
  } else {
    return await response.text(); // Return non-JSON response as text
  }
}
