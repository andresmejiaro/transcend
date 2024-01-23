const direc = "./srcs/";

document.addEventListener("click", (e) => {
  const { target } = e;
  
  // if (!(target.matches("nav a") || target.matches("nav a *"))) {
  if (!target.matches("nav a")) {
    return;
  }
  e.preventDefault();
  urlRoute();
});

const ifLoggedRedirect = (location) => {
  if (!isLogged()) {
    if (!allowedLocations.includes(window.location.pathname)) {
      console.log("router logout");
      handleLogout();
    }
  } else {
    if (allowedLocations.includes(location)) {
      window.location.pathname = "/play!";
    }
  }
};

const urlRoute = (event) => {
  event = event || window.event;
  event.preventDefault();
  // window.history.pushState(state, unused, target link);
  window.history.pushState({}, "", event.target.href);
  urlLocationHandler();
};

const urlLocationHandler = async () => {
  let location = window.location.pathname;

  if (location.length == 0) {
    location = "/";
  }

  ifLoggedRedirect(location);


  const route = urlRoutes[location] || urlRoutes["404"];
  const html = await fetch(route.template).then((response) => response.text());
  document.getElementById("content").innerHTML = html;
  document.title = route.title;

  // set the description of the document to the description of the route
  document
    .querySelector('meta[name="description"]')
    .setAttribute("content", route.description);

  if (route.css) {
    const head = document.head;

    route.css.forEach((cssFile) => {
      const link = document.createElement("link");

      link.type = "text/css";
      link.rel = "stylesheet";
      link.href = cssFile;

      head.appendChild(link);
    });
  }

  if (isLogged() && route !== urlRoutes["404"])
    loadLobbyScripts();

  if (route.js) {
    route.js.forEach(({file, loadedCallback}) => {
      if (file && !document.querySelector(`script[src="${file}"]`)) {
        const body = document.body;
        const script = document.createElement("script");
        // console.log(file)

        script.type = "text/javascript";
        script.src = file;
        script.async = false;

        body.appendChild(script);
      }
      else {
        loadedCallback?.();
      }
    });
  }

  const navRouter = document.getElementById("nav-router");
  if (navRouter) {
    const existingContent = navRouter.innerHTML.trim();
    if (!existingContent) {
      if (isLogged() && route !== urlRoutes["404"]) {
        navRouter.innerHTML = await fetch(
          direc + "assets/components/navbar/nav-logged.html"
        ).then((response) => response.text());
      }
    }
  } else {
    console.error("Element with id 'nav-router' not found in the DOM");
  }
  if (route !== urlRoutes["404"])
    loadNavScripts();
};

const loadNavScripts = () => {
  const navDirec = `${direc}assets/components/navbar`;
  const scriptPaths = [
    `${navDirec}/nav.js`,
    `${navDirec}/nav-friend-invite-handler.js`,
    `${navDirec}/nav-friend-match-invite-handler.js`,
    `${navDirec}/nav-friend-remove-handler.js`,
    `${navDirec}/nav-friends-modal.js`,
    `${navDirec}/nav-friends.js`,
    `${navDirec}/nav-notification-handler.js`,
    `${navDirec}/nav-notification-modal.js`,
  ];
  const body = document.body;

  scriptPaths.forEach((path) => {
    const scriptSrc = `${path}`;

    if (isLogged() && !document.querySelector(`script[src="${scriptSrc}"]`)) {
      const script = document.createElement("script");
      script.type = "text/javascript";
      script.src = scriptSrc;
      script.async = false;

      body.appendChild(script);
    }
  });
};

const loadLobbyScripts = () => {
  const lobbyDirec = `${direc}utils/lobby/`;
  const scriptPaths = [
    `${lobbyDirec}lobby-connection-handler.js`,
    `${lobbyDirec}lobby-matches-friends-handler.js`,
    `${lobbyDirec}lobby-friends-handler.js`,
    `${lobbyDirec}lobby-message-parser.js`,
    `${lobbyDirec}lobby-notifications-handler.js`,
    `${lobbyDirec}lobby-queue-handler.js`,
  ];
  const body = document.body;

  scriptPaths.forEach((path) => {
    const scriptSrc = `${path}`;

    if (isLogged() && !document.querySelector(`script[src="${scriptSrc}"]`)) {
      const script = document.createElement("script");
      script.type = "text/javascript";
      script.src = scriptSrc;
      script.async = false;

      body.appendChild(script);
    }
  });

}

// add an event listener to the window that watches for url changes
window.onpopstate = urlLocationHandler;
// call the urlLocationHandler function to handle the initial url
window.route = urlRoute;
// call the urlLocationHandler function to handle the initial url
urlLocationHandler();
