const urlPageTitle = "Pixel Pong";
const directory = "./srcs/pages/";

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
		js: [{ file: directory + "landing/landing.js" }],
		css: [directory + "landing/landing.css"],
	},

	"/home": {
		template: directory + "home/home.html",
		title: urlPageTitle,
		description: "This is the home page",
		js: [{ file: directory + "home/intra-handler.js" }, { file: directory + "home/home.js" }],
		css: [directory + "home/home.css"],
	},

	"/signin": {
		template: directory + "signin/signin.html",
		title: urlPageTitle + " - Sing in",
		description: "This is the signin page",
		js: [{ file: directory + "signin/signin.js" }],
		css: [directory + "signin/signin.css"],
	},

	"/signup": {
		template: directory + "signup/signup.html",
		title: urlPageTitle + " - Sing up",
		description: "This is the signup page",
		js: [{ file: directory + "signup/signup-handler.js" }],
		css: [directory + "signup/signup.css"],
	},

	"/otp": {
		template: directory + "otp/otp.html",
		title: urlPageTitle,
		description: "This is the 2FA page",
		js: [{ file: directory + "otp/otp-handler.js" }, { file: "./srcs/utils/google-auth-utils.js" }],
		css: [directory + "otp/otp.css"],
	},

	"/intra": {
		template: directory + "intra/intra.html",
		title: urlPageTitle,
		description: "This is the intra handler page",
		js: [{ file: directory + "intra/callback.js" }],
	},

	"/play!": {
		template: directory + "play!/play!.html",
		title: urlPageTitle,
		description: "This is the home page",
		css: [directory + "play!/play!.css"],
	},

	"/profile": {
		template: directory + "profile/profile.html",
		title: urlPageTitle + " - Profile",
		description: "This is the user page",
		js: [{ file: directory + "profile/profile.js", loadedCallback: () => getMeSettingsInfoProfile() }],
	},

	"/profilesettings": {
		template: directory + "profilesettings/user-settings.html",
		title: urlPageTitle + " - Profile",
		description: "This is the user page",
		js: [{ file: directory + "profilesettings/user-settings.js", loadedCallback: () => getMeSettingsInfo() }, { file: directory + "profilesettings/edit-user-info.js" }, { file: directory + "profilesettings/change-avatar.js" }, { file: directory + "profilesettings/profile-settings-ga.js" }, { file: "./srcs/utils/google-auth-utils.js" }],
		css: [directory + "profilesettings/user-settings.css"],
	},

	"/tournaments": {
		template: directory + "tournaments/create-tournament.html",
		title: urlPageTitle + " - Tournaments",
		description: "This is the create tournament page",
		js: [{ file: directory + "tournaments/tournaments.js" }, { file: directory + "tournaments/tournament-creation-handler.js" }, { file: directory + "tournaments/tournament-join-handler.js" },],
		css: [directory + "tournaments/tournaments.css"],
	},

	"/tournament": {
		template: directory + "tournament/tournament.html",
		title: urlPageTitle + " - Tournament",
		description: "This is the tournament page",
		js: [{ file: directory + "tournament/tournament-lobby.js" }, { file: directory + "tournament/utils.js" }, { file: directory + "tournament/tournament.js" }, { file: directory + "tournament/tournament-admin.js" }, { file: directory + "tournament/tournament-matchmaking-handler.js" }, { file: directory + "tournament/tournament-match-handler.js" },
		{ file: directory + "0nlinegame/enviroment.js" }, { file: "./srcs/utils/pongJs/MovingRectangle.js" }, { file: "./srcs/utils/pongJs/Ball.js" }, { file: "./srcs/utils/pongJs/Paddle.js" }, { file: "./srcs/utils/pongJs/Player.js" }, { file: "./srcs/utils/pongJs/Game.js" }, { file: directory + "0nlinegame/helper.js" }, { file: directory + "0nlinegame/finish-helper.js" }],
		css: [directory + "tournament/tournament.css"],
	},

	"/2plygame": {
		template: directory + "2plygame/2plygame.html",
		title: urlPageTitle,
		description: "This is the local pong page",
		js: [{ file: directory + "2plygame/enviroment.js" }, { file: "./srcs/utils/pongJs/MovingRectangle.js" }, { file: "./srcs/utils/pongJs/Ball.js" }, { file: "./srcs/utils/pongJs/Paddle.js" }, { file: "./srcs/utils/pongJs/Player.js" }, { file: "./srcs/utils/pongJs/Game.js" }, { file: directory + "2plygame/main.js" }],
		css: [directory + "2plygame/2plygame.css"],
	},

	"/1plygame": {
		template: directory + "1plygame/1plygame.html",
		title: urlPageTitle,
		description: "This is the local pong page",
		js: [{ file: directory + "1plygame/enviroment.js" }, { file: "./srcs/utils/pongJs/MovingRectangle.js" }, { file: "./srcs/utils/pongJs/Ball.js" }, { file: "./srcs/utils/pongJs/Paddle.js" }, { file: "./srcs/utils/pongJs/Player.js" }, { file: "./srcs/utils/pongJs/Game.js" }, { file: "./srcs/utils/pongJs/PongAI.js" }, { file: directory + "1plygame/main.js" }],
		css: [directory + "1plygame/1plygame.css"],
	},

	"/onlinegame": {
		template: directory + "0nlinegame/onlinegame.html",
		title: urlPageTitle,
		description: "This is the local pong page",
		js: [{ file: directory + "0nlinegame/enviroment.js" }, { file: "./srcs/utils/pongJs/MovingRectangle.js" }, { file: "./srcs/utils/pongJs/Ball.js" }, { file: "./srcs/utils/pongJs/Paddle.js" }, { file: "./srcs/utils/pongJs/Player.js" }, { file: "./srcs/utils/pongJs/Game.js" }, { file: directory + "0nlinegame/helper.js" }, { file: directory + "0nlinegame/finish-helper.js" }, { file: directory + "0nlinegame/main.js" }],
		css: [directory + "0nlinegame/onlinegame.css"],
	},

	"/localp": {
		template: directory + "localp/localp.html",
		title: urlPageTitle,
		description: "This is the local pong page",
		js: [{ file: directory + "localp/enviroment.js" }, { file: "./srcs/utils/pongJs/MovingRectangle.js" }, { file: "./srcs/utils/pongJs/Ball.js" }, { file: "./srcs/utils/pongJs/Paddle.js" }, { file: "./srcs/utils/pongJs/Player.js" }, { file: "./srcs/utils/pongJs/Game.js" }, { file: directory + "localp/main.js" }],
		css: [directory + "localPlay/localp.css"],
	},
};

const allowedLocations = ["/", "/home", "/login", "/signin", "/signup", "/intra"];
