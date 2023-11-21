export const urlRoutes = {
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
  };