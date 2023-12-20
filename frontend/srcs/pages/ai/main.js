const username_ = sessionStorage.getItem("username");

player1 = new Player(username_, {up:"w", down:"s",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");
player2 = new Player("Marvin", {up:"ArrowUp", down:"ArrowDown",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");

game = new Game(player1, player2, remote = 2);

game.start();