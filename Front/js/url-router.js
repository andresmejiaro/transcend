
document.addEventListener("click", (e) => {
  const { target } = e;
  if (!target.matches("nav a")) {
    return;
  }
  e.preventDefault();
  urlRoute();
});

const ifLoggedRedirect = (location) => {
  if (isLogged()) {
    if (location == "/login" || location == "/signup")
      window.location.href = "/";
  } else {
    if (location == "/user" || location == "/create-tournaments")
      window.location.href = "/";
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

  console.log("location: ", location);
  const route = urlRoutes[location] || urlRoutes["404"];
  const html = await fetch(route.template).then((response) => response.text());
  document.getElementById("content").innerHTML = html;
  document.title = route.title;

  const navRouter = document.getElementById("nav-router");
  if (navRouter) {
    const existingContent = navRouter.innerHTML.trim();
    if (existingContent.includes("nav-logged")) {
      console.log("Nav logged template is already present");
    } else if (existingContent.includes("nav-anonymous")) {
      console.log("Nav anonymous template is already present");
    } else {
      if (isLogged()) {
        navRouter.innerHTML = await fetch("/templates/nav-logged.html").then(
          (response) => response.text()
        );
      } else {
        navRouter.innerHTML = await fetch("/templates/nav-anonymous.html").then(
          (response) => response.text()
        );
      }
    }
  } else {
    console.error("Element with id 'nav-router' not found in the DOM");
  }

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
  if (route.js) {
    route.js.forEach((jsFile) => {
      if (jsFile && !document.querySelector(`script[src="${jsFile}"]`)) {
        const body = document.body;
        const script = document.createElement("script");

        script.type = "text/javascript";
        script.src = jsFile;
        script.async = false;

        body.appendChild(script);
      }
    });
  }

  if (!document.querySelector(`script[src="./js/nav.js"]`)) {
    const body = document.body;
    const script = document.createElement("script");

    script.type = "text/javascript";
    script.src = "./js/nav.js";
    script.async = false;

    body.appendChild(script);
  }
};

// add an event listener to the window that watches for url changes
window.onpopstate = urlLocationHandler;
// call the urlLocationHandler function to handle the initial url
window.route = urlRoute;
// call the urlLocationHandler function to handle the initial url
urlLocationHandler();
