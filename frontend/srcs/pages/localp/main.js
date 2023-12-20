player1 = new Player("player1", {up:"w", down:"s",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");
player2 = new Player("player2", {up:"ArrowUp", down:"ArrowDown",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");

game = new Game(player1, player2, remote = 0);

game.start();