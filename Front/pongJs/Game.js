class Game {
    #leftPlayer
    #rightPlayer
    #scoreLimit
    #ball
    #leftPaddle
    #rightPaddle
    #background
    #backgroundLoaded
    #remote
    #justpressed
    #remoteCanvas
    #ai

    constructor(leftPlayer, rightPlayer) {
        this.#leftPlayer = leftPlayer;
        this.#rightPlayer = rightPlayer;
        this.#scoreLimit = 11;
        this.#background = new Image();
        this.#background.src = './assets/game/table.png';
        this.#backgroundLoaded = false;
        this.#background.onload = () => { this.#backgroundLoaded = true; };
        this.#remote = 0;
        this.#justpressed = false;
        
    }
    
    startScreen() {
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (this.#backgroundLoaded) {
            ctx.fillText("Current Mode is " + this.statusToText(), 50, 20);
            ctx.fillText(`Press Enter to Start`, 50, 40);
            ctx.fillText(`Press w to Change Mode`, 50, 60);
            if (keysPressed["Enter"]){
                if (this.statusToText() == "ai")
                    this.setupAI();
                requestAnimationFrame(() => this.gameSetup());
            }
            else if (!(keysPressed["w"] || keysPressed["W"]) && this.#justpressed) {
                this.#justpressed = 0;
                requestAnimationFrame(() => this.startScreen());
            }
            else if ((keysPressed["w"] || keysPressed["W"]) && !this.#justpressed) {
                this.#remote = (this.#remote + 1) % 3;
                this.#justpressed = 1;
                requestAnimationFrame(() => this.startScreen());
            }
            else
                requestAnimationFrame(() => this.startScreen());
        }
        else {
            ctx.fillText(`Loading ...`, 50, 30);
            console.log(this.#backgroundLoaded);
            requestAnimationFrame(() => this.startScreen());
        }

    }

    statusToText() {
        if (this.#remote == 0)
            return "local";
        if (this.#remote == 1)
            return "remote";
        if (this.#remote == 2)
            return "ai";
    }

    endScreen() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (this.#leftPlayer.score > this.#rightPlayer.score)
            ctx.fillText(`Winner: ${this.#leftPlayer.name}`, 100, 100);
        else
            ctx.fillText(`Winner: ${this.#rightPlayer.name}`, 100, 100);
        ctx.fillText(`Thanks for playing to play again press Enter`, 50, 30);
        if (keysPressed["Enter"])
            requestAnimationFrame(() => this.gameSetup());
        else
            requestAnimationFrame(() => this.endScreen());
    }


    // game loop

    pointLoop() {
        this.drawNonInteractive();
        if (this.statusToText() == "remote")
            this.remoteGameLogic();
        else 
            this.localGameLogic();
        this.drawInteractive();
        this.drawScore();
        if (this.#leftPlayer.score >= this.#scoreLimit
            || this.#rightPlayer.score >= this.#scoreLimit)
            requestAnimationFrame(() => this.endScreen());
        else
            requestAnimationFrame(() => this.pointLoop());
    }
    
    receiveRemoteCanvas() {
        let data = { ... this.#remoteCanvas };
        keysSend = {}
        keysSend["up"] = keysPressed[this.player1.binds["up"]];
        keysSend["down"] = keysPressed[this.player1.binds["down"]];
        //se deja para futura expansion enviar las teclas de los dos jugadores
        //keysSend["up2"] = keysPressed[this.player1.binds["up2"]];
        //keysSend["down2"] = keysPressed[this.player1.binds["down2"]];
        sendWebSocketGameMessage("keyboard_update", keysSend);
        return data["canvas"];
    }

    remoteGameLogic() {
        let canvas = this.receiveRemoteCanvas();
        this.#ball.setPosition(canvas["ball"]["position"]);
        this.#ball.setSize(canvas["ball"]["size"]);
        this.#leftPaddle.setPosition(canvas["leftPaddle"]["position"]);
        this.#leftPaddle.setSize(canvas["leftPaddle"]["size"]);
        this.#rightPaddle.setPosition(canvas["rightPaddle"]["position"]);
        this.#rightPaddle.setSize(canvas["rightPaddle"]["size"]);
        //if (this.newScore()){
        //    this.#leftPlayer.score = score["p1"];
        //    this.#rightPlayer.score = score["p2"];
        //}
    }


    localGameLogic() {
        if (this.statusToText() == "ai"){
            this.#ai.keyboardUpdate();
        }
        let ballState = this.#ball.updatePosition();
        if (ballState == 1) {
            this.#leftPlayer.goal();
            this.resetPosition();
        }
        else if (ballState == -1) {
            this.#rightPlayer.goal();
            this.resetPosition();
        } else {
            this.#leftPaddle.updatePosition();
            this.#rightPaddle.updatePosition();
        }
    }

    drawNonInteractive() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(this.#background, 0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "white";
    }

    drawInteractive() {
        this.#ball.draw();
        this.#leftPaddle.draw();
        this.#rightPaddle.draw();
    }

    drawScore() {
        const text1 = `${this.#leftPlayer.name}: ${this.#leftPlayer.score}`;
        const text2 = `${this.#rightPlayer.name}: ${this.#rightPlayer.score}`;
        const p1metrics = ctx.measureText(text1);
        const p2metrics = ctx.measureText(text2);
        ctx.fillText(text1, canvas.width / 4 - p1metrics.width / 2, 40);
        ctx.fillText(text2, canvas.width * 3 / 4 - p2metrics.width / 2, 40);
    }

    resetPosition() {
        this.#ball.setPosition({ x: canvas.width / 2, y: canvas.height / 2 });
        let ran = Math.random();
        if (ran < 0.25)
            this.#ball.setSpeed({ x: 4, y: 1 });
        else if (ran < 0.5)
            this.#ball.setSpeed({ x: -4, y: 1 });
        else if (ran < 0.75)
            this.#ball.setSpeed({ x: 4, y: -1 });
        else
            this.#ball.setSpeed({ x: -4, y: -1 });


    }

    gameSetup() {
        this.#ball = new Ball({ x: canvas.width / 2, y: canvas.height / 2 },
            { x: 4, y: 3 }, { x: 10, y: 10 });
        this.resetPosition();
        this.#leftPaddle = new Paddle({ x: 30, y: 0 }, { x: 10, y: 10 },
            { x: 10, y: 100 }, "white",
            this.#leftPlayer.binds);
        this.#rightPaddle = new Paddle({ x: canvas.width - 30, y: 0 }, { x: 10, y: 10 },
            { x: 10, y: 100 }, "white",
            this.#rightPlayer.binds);
        this.#rightPlayer.resetScore();
        this.#leftPlayer.resetScore();

        this.#ball.addColider(this.#leftPaddle);
        this.#ball.addColider(this.#rightPaddle);
        requestAnimationFrame(() => this.pointLoop());
    }

    conexionSetup(matchId) {
        this.#remoteCanvas = {}
        connectGameWebSocket(matchId, player1, player2, this.#remoteCanvas)
    }


    start() {
        requestAnimationFrame(() => this.startScreen());
    }

    setupAI(){
        if (!this.#rightPlayer.ai)
            this.#rightPlayer.toggleAI();
        this.#rightPlayer.binds = {up : "AI_UP", down : "AI_DOWN", 
            left: "AI_LEFT", right: "AI_RIGHT"}
        this.#ai = new PongAI(this.#rightPlayer, this);
    
    }

    getCanvas(){
        let lcanvas = {};
        lcanvas["ball"] = {}
        lcanvas["ball"]["position"] = this.#ball.getPosition;
        lcanvas["ball"]["size"] = this.#ball.getSize;
        lcanvas["leftPaddle"] = {}
        lcanvas["leftPaddle"]["position"] = this.#leftPaddle.getPosition;
        lcanvas["leftPaddle"]["size"] = this.#leftPaddle.getSize;
        lcanvas["rightPaddle"] = {}
        lcanvas["rightPaddle"]["position"] = this.#rightPaddle.getPosition;
        lcanvas["rightPaddle"]["size"] = this.#rightPaddle.getSize;
        return lcanvas;
    }
}
