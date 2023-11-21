const urlPageTitle = "JS Single Page Application Router";

const urlRoutes = {
  404: {
    template: "/templates/404.html",
    title: "404 | " + urlPageTitle,
    description: "Page not found",
  },
  "/": {
    template: "/templates/index.html",
    title: "Landing | " + urlPageTitle,
    description: "This is the landing page",
    js: ["./js/index.js"],
  },
  "/home": {
    template: "/templates/home.html",
    title: "Home | " + urlPageTitle,
    description: "This is the home page",
    js: ["./js/home.js"],
  },
  "/user": {
    template: "/templates/user.html",
    title: "user | " + urlPageTitle,
    description: "This is the user page",
  },
  "/login": {
    template: "/templates/login.html",
    title: "Login | " + urlPageTitle,
    description: "This is the login page",
    js: ["./js/auth/login-handler.js", "./js/auth/intra-handler.js"],
  },
  "/signup": {
    template: "/templates/signup.html",
    title: "Login | " + urlPageTitle,
    description: "This is the login page",
    js: ["./js/auth/signup-handler.js"],
  },
  "/callback": {
    template: "/templates/callback.html",
    title: "callback | " + urlPageTitle,
    description: "This is the callback page",
    js: ["./js/auth/callback.js"],
  },
  "/create-tournaments": {
    template: "/templates/create-tournament.html",
    title: "create tournament | " + urlPageTitle,
    description: "This is the create tournament page",
    js: ["./js/create-tor.js"],
  },
};