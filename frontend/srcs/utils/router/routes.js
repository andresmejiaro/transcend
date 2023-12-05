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
    template: directory + "/signin/signin.html",
    title: urlPageTitle + " - Sing in",
    description: "This is the signin page",
    js: [directory + "sigin/sigin.js"],
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
    js: [directory + "opt/otp-handler.js"],
  },

  "/callback": {
    template: directory + "callback/callback.html",
    title: urlPageTitle,
    description: "This is the callback page",
    js: [directory + "callback/callback.js"],
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
  },

  "/tournaments": {
    template: directory + "tournaments/create-tournament.html",
    title: urlPageTitle + " - Tournaments",
    description: "This is the create tournament page",
    js: [directory + "tournaments/create-tor.js"],
    css: [directory + "tournaments/tournaments.css"]
  },

  "/leaderboards": {
    template: directory +  "leaderboard/leaderboards.html",
    title: urlPageTitle + " - Leaderboard",
    description: "This is the leaderboards tournament page"
  },

  "/2plygame": {
    template: directory + "2plygame/2plygame.html",
    title: urlPageTitle,
    description: "This is the local pong page",
    js: ["./srcs/utils/pongJs/environment.js","./pongJs/MovingRectangle.js",
    "./pongJs/Ball.js","./pongJs/Paddle.js","./pongJs/Player.js", 
    "./pongJs/Game.js","./pongJs/main.js"],
    css: [directory + "2plygame/2plygame.css"]
  }
};