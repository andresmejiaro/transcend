const loadNavScripts = () => {
	const navDirec = `${direc}assets/components/navbar`;
	const scriptPaths = [`${navDirec}/nav.js`, `${navDirec}/nav-friend-invite-handler.js`, `${navDirec}/nav-friend-match-invite-handler.js`, `${navDirec}/nav-friend-remove-handler.js`, `${navDirec}/nav-friends-modal.js`, `${navDirec}/nav-friends.js`, `${navDirec}/nav-notification-handler.js`, `${navDirec}/nav-notification-modal.js`];
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
	const scriptPaths = [`${lobbyDirec}lobby-connection-handler.js`, `${lobbyDirec}lobby-matches-friends-handler.js`, `${lobbyDirec}lobby-friends-handler.js`, `${lobbyDirec}lobby-message-parser.js`, `${lobbyDirec}lobby-notifications-handler.js`, `${lobbyDirec}lobby-queue-handler.js`];
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
