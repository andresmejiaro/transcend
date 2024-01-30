
const fadeOutAndNavigate = async (target) => {
  document.body.classList.add('fade-out');

  await new Promise((resolve) => setTimeout(resolve, 700));

  await navigateTo(target);

  document.body.classList.remove('fade-out');

  document.body.removeEventListener('click', clickHandler);
};

const clickHandler = async function () {
  const targetUrl = "/home";
  await fadeOutAndNavigate(targetUrl);
};

document.body.addEventListener('click', clickHandler);