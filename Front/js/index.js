const useSessionStorageEffect = (key, callback) => {
  const initialValue = sessionStorage.getItem(key);

  callback(initialValue);

  window.addEventListener("storage", (event) => {
    if (event.key === key) {
      callback(event.newValue);
    }
  });

  return () => {
    window.removeEventListener("storage", callback);
  };
};

const handleChange = (newValue) => {
  const usernameElement = document.getElementById("username-nav");
  const loggedElement = document.getElementById("logged");

  if (newValue) {
    usernameElement.innerHTML = newValue;

    loggedElement.innerHTML = `<p>Welcome, ${newValue}!</p><button id="submitButton" class="btn btn-primary">Submit</button>`;

    const submitButton = document.getElementById("submitButton");
    if (submitButton) {
      submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        handleLogout();
      });
    }
  } else {
    loggedElement.innerHTML = "Not logged in";
  }
};

const cleanup = useSessionStorageEffect("username", handleChange);

const cleanupFunction = () => {
	window.removeEventListener("storage", handleChange);
};

cleanupFunction();
