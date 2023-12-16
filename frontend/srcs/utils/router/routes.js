const urlPageTitle = "Pixel Pong";
const directory = "./srcs/pages/"


const urlRoutes = {
  404: {
    template: directory + "404/404.html",
    title: urlPageTitle + " - 404",
    description: "Page not found",
  },

  "/": {
    template: directory + "landing/landing.html",
    title: urlPageTitle,
    description: "This is the landing page",
    js: [directory + "landing/landing.js"],
    css: [directory + "landing/landing.css"]
  },

  "/home": {
    template: directory + "home/home.html",
    title: urlPageTitle,
    description: "This is the home page",
    js: [directory + "home/intra-handler.js"],
    css: [directory + "home/home.css"]
  },

  "/signin": {
    template: directory + "signin/signin.html",
    title: urlPageTitle + " - Sing in",
    description: "This is the signin page",
    js: [directory + "signin/signin.js"],
    css: [directory + "signin/signin.css"]
  },

  "/signup": {
    template: directory + "signup/signup.html",
    title: urlPageTitle + " - Sing up",
    description: "This is the signup page",
    js: [directory + "signup/signup-handler.js"],
    css: [directory + "signup/signup.css"]
  },
  
  "/otp": {
    template: directory + "otp/otp.html",
    title: urlPageTitle,
    description: "This is the 2FA page",
    js: [directory + "otp/otp-handler.js", "./srcs/utils/google-auth-utils.js"],
  },

  "/intra": {
    template: directory + "intra/intra.html",
    title: urlPageTitle,
    description: "This is the intra handler page",
    js: [directory + "intra/callback.js"],
  },

  "/play!": {
    template: directory + "play!/play!.html",
    title: urlPageTitle,
    description: "This is the home page",
  },

  "/profile": {
    template: directory + "profile/profile.html",
    title: urlPageTitle + " - Profile",
    description: "This is the user page",
    js: [directory + "profile/profile.js"],
  },

  "/profilesettings": {
    template: directory + "profilesettings/user-settings.html",
    title: urlPageTitle + " - Profile",
    description: "This is the user page",
    js: [directory + "profilesettings/user-settings.js"],
    // js: [directory + "profilesettings/user-settings.js", "./srcs/utils/google-auth-utils.js"],
  },

  "/tournaments": {
    template: directory + "tournaments/create-tournament.html",
    title: urlPageTitle + " - Tournaments",
    description: "This is the create tournament page",
    js: [directory + "tournaments/create-tor.js", directory + "tournaments/join-tor.js"],
    css: [directory + "tournaments/tournaments.css"]
  },

  "/2plygame": {
    template: directory + "2plygame/2plygame.html",
    title: urlPageTitle,
    description: "This is the local pong page",
    // js: ["./srcs/utils/pongJs/environment.js","./srcs/utils/pongJs/MovingRectangle.js",
    // "./srcs/utils/pongJs/Ball.js","./srcs/utils/pongJs/Paddle.js","./srcs/utils/pongJs/Player.js", 
    // "./srcs/utils/pongJs/Game.js","./srcs/utils/pongJs/main.js"],
    js: [directory + "2plygame/game.js"],
    css: [directory + "2plygame/2plygame.css"]
  }
};

const allowedLocations = ["/", "/home", "/login", "/signin", "/signup", "/intra", "/otp"];