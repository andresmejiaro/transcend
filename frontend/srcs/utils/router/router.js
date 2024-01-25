const direc = "./srcs/";


document.addEventListener("click", (e) => {
  const { target } = e;
  
  if (target.matches("a")) {
    handleRouting(e);
  }
});

const navigateTo = async (target) => {
  window.history.pushState({}, "", target);
  await urlLocationHandler();
};

const handleRouting = async (event) => {
  event.preventDefault();
  const target = event.target.href;
  await navigateTo(target);
};


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


// Common function to load scripts
const loadScripts = async (scripts) => {
  const body = document.body;

  await Promise.all(
    scripts.map(async (script) => {
      const { file, loadedCallback } = script;

      if (file && !document.querySelector(`script[src="${file}"]`)) {
        return new Promise((resolve, reject) => {
          const scriptElement = document.createElement("script");

          scriptElement.type = "text/javascript";
          scriptElement.src = file;
          scriptElement.async = false;

          scriptElement.onload = () => {
            loadedCallback?.();
            resolve();
          };
          scriptElement.onerror = reject;

          body.appendChild(scriptElement);
        });
      } else {
        loadedCallback?.();
        return Promise.resolve();
      }
    })
  );
};

// Common function to load styles
const loadStyles = (styles) => {
  const head = document.head;

  styles.forEach((styleFile) => {
    const link = document.createElement("link");

    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = styleFile;

    head.appendChild(link);
  });
};



const urlLocationHandler = async () => {
  const location = window.location.pathname || "/";

  ifLoggedRedirect(location);

  const route = urlRoutes[location] || urlRoutes["404"];

  try {
    const [html, styles] = await Promise.all([
      fetch(route.template).then((response) => response.text()),
      Promise.resolve(route.css || []),
    ]);

    document.getElementById("content").innerHTML = html;
    document.title = route.title;

    document.querySelector('meta[name="description"]').setAttribute("content", route.description);

    loadStyles(styles);

    if (isLogged() && route !== urlRoutes["404"]) {
      loadLobbyScripts();
    }

    if (route.js) {
      await loadScripts(route.js);
    }

    const navRouter = document.getElementById("nav-router");

    if (navRouter && navRouter.innerHTML.trim() === "" && isLogged() && route !== urlRoutes["404"]) {
      navRouter.innerHTML = await fetch(direc + "assets/components/navbar/nav-logged.html").then((response) => response.text());
    }
  } catch (error) {
    console.error("Error loading content:", error);
  }

  if (route !== urlRoutes["404"]) {
    loadNavScripts();
  }
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