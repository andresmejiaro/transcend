player1 = new Player("Left player", {up:"w", down:"s",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");
player2 = new Player("Right player", {up:"ArrowUp", down:"ArrowDown",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");

game = new Game(player1, player2, remote = 0);

game.start();