const urlPageTitle = "Pixel Pong";

const urlRoutes = {

  404: {
    template: "/templates/404.html",
    title: "404 | " + urlPageTitle,
    description: "Page not found",
  },

  "/": {
    template: "/templates/landing.html",
    title: urlPageTitle,
    description: "This is the landing page",
    js: ["./js/index.js"],
    css: ["./css/landing.css"]
  },

  "/home": {
    template: "/templates/home.html",
    title: urlPageTitle,
    description: "This is the home page",
    js: ["./js/home.js", "./js/auth/intra-handler.js"],
    css: ["./css/home.css"]
  },

  "/login": {
    template: "/templates/login.html",
    title: urlPageTitle + " - Sing in",
    description: "This is the login page",
    js: ["./js/auth/login-handler.js"],
    css: ["./css/signup.css", "./css/inputs.css"]
  },

  "/signup": {
    template: "/templates/signup.html",
    title: urlPageTitle + " - Sing up",
    description: "This is the login page",
    js: ["./js/auth/signup-handler.js"],
    css: ["./css/signup.css", "./css/inputs.css"]
  },
  
  "/otp": {
    template: "/templates/otp.html",
    title: urlPageTitle,
    description: "This is the 2FA page",
    js: ["./js/auth/otp-handler.js"],
  },

  "/callback": {
    template: "/templates/callback.html",
    title: urlPageTitle,
    description: "This is the callback page",
    js: ["./js/auth/callback.js"],
  },

  "/home-logged": {
    template: "/templates/home-logged.html",
    title: urlPageTitle,
    description: "This is the home page",
    js: ["./js/home-loggedin.js"],
  },

  "/user": {
    template: "/templates/user.html",
    title: urlPageTitle + " - Profile",
    description: "This is the user page",
    js: ["./js/user/user.js"],
  },

  "/user-settings": {
    template: "/templates/user-settings.html",
    title: urlPageTitle + " - Profile",
    description: "This is the user page",
    js: ["./js/user/user-settings.js"],
    css: ["./css/inputs.css"]
  },

  "/create-tournaments": {
    template: "/templates/create-tournament.html",
    title: urlPageTitle + "Tournaments",
    description: "This is the create tournament page",
    js: ["./js/create-tor.js"],
    css: ["./css/tournaments.css"]
  },

  "/leaderboards": {
    template: "/templates/leaderboards.html",
    title: urlPageTitle + " - Leaderboard",
    description: "This is the leaderboards tournament page",
    // js: ["./js/create-tor.js"],
    // css: ["./css/tournaments.css"]
  },

  "/local-game": {
    template: "/templates/local-game.html",
    title: urlPageTitle,
    description: "This is the local pong page",
    js: ["./pongJs/environment.js","./pongJs/MovingRectangle.js",
    "./pongJs/Ball.js","./pongJs/Paddle.js","./pongJs/Player.js", 
    "./pongJs/Game.js","./pongJs/main.js"],
    css: ["./css/local-game.css"]
  }
};