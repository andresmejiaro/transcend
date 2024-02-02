const fadeOutAndNavigate = async (target) => {
  document.body.classList.add('fade-out');

  setTimeout(function () {
    window.location.href = '/home';
  }, 700);
};

document.body.addEventListener('click', function () {
  const targetUrl = "/home";
  fadeOutAndNavigate(targetUrl);
});

window.addEventListener('focus', function() {
  document.body.classList.remove('fade-out');
  window.location.href = '/';
});
