// const handleClick = async (event, targetUrl) => {
// 	event.preventDefault();
// 	await navigateTo(targetUrl);
// };

// // Function to add click event listener
// const addClickListener = (buttonId, targetUrl) => {
// 	const button = document.getElementById(buttonId);

// 	if (button) {
// 		button.addEventListener("click", async (event) => {
// 			await handleClick(event, targetUrl);
// 		});
// 	}
// };

// // Example usage
// addClickListener("signupButton", "/signup");
// addClickListener("signinButton", "/signin");

window.addEventListener('focus', function() {
    window.location.href = '/home';
  });
  