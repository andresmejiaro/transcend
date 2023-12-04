document.body.addEventListener('click', function () {
  // Apply the fade-out effect
  document.body.classList.add('fade-out');

  // Change location after the transition ends
  setTimeout(function () {
    window.location.href = '/home';
  }, 700); // Match this time with your CSS transition time
});
