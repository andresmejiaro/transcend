const urlPageTitle = "Pixel Pong";

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
    css: ["./css/landing.css"]
  },
  "/home": {
    template: "/templates/home.html",
    title: "Home | " + urlPageTitle,
    description: "This is the home page",
    js: ["./js/home.js", "./js/auth/intra-handler.js"],
    css: ["./css/home.css"]
  },
  "/login": {
    template: "/templates/login.html",
    title: "Login | " + urlPageTitle,
    description: "This is the login page",
    js: ["./js/auth/login-handler.js"],
    css: ["./css/signup.css", "./css/inputs.css"]
  },
  "/signup": {
    template: "/templates/signup.html",
    title: "Signup | " + urlPageTitle,
    description: "This is the login page",
    js: ["./js/auth/signup-handler.js"],
    css: ["./css/signup.css", "./css/inputs.css"]
  },
  "/otp": {
    template: "/templates/otp.html",
    title: "OTP | " + urlPageTitle,
    description: "This is the 2FA page",
    js: ["./js/auth/otp-handler.js"],
  },
  "/callback": {
    template: "/templates/callback.html",
    title: "callback | " + urlPageTitle,
    description: "This is the callback page",
    js: ["./js/auth/callback.js"],
  },
  "/home-logged": {
    template: "/templates/home-logged.html",
    title: "Home | " + urlPageTitle,
    description: "This is the home page",
    js: ["./js/home-loggedin.js"],
  },
  "/user": {
    template: "/templates/user.html",
    title: "user | " + urlPageTitle,
    description: "This is the user page",
    js: ["./js/user/user.js"],
  },
  "/user-settings": {
    template: "/templates/user-settings.html",
    title: "user | " + urlPageTitle,
    description: "This is the user page",
    js: ["./js/user/user-settings.js"],
    css: ["./css/inputs.css"]
  },
  "/create-tournaments": {
    template: "/templates/create-tournament.html",
    title: "create tournament | " + urlPageTitle,
    description: "This is the create tournament page",
    js: ["./js/create-tor.js"],
    css: ["./css/tournaments.css"]
  },
  "/leaderboards": {
    template: "/templates/leaderboards.html",
    title: "Leaderboards | " + urlPageTitle,
    description: "This is the leaderboards tournament page",
    // js: ["./js/create-tor.js"],
    // css: ["./css/tournaments.css"]
  },
};