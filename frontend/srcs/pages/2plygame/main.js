player1 = new Player("adrgonza", {up:"w", down:"s",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");
player2 = new Player("ai", {up:"ArrowUp", down:"ArrowDown",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");

game = new Game(player1, player2, remote = 1);

game.start();