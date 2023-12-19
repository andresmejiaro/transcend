document.body.addEventListener('click', function () {
  // Apply the fade-out effect
  document.body.classList.add('fade-out');

  setTimeout(function () {
    window.location.href = '/home';
  }, 700);
});
