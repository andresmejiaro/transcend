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
    #remoteCanvas
    #ai
    #marvin
    #defLocalBinds
    #defRemoteBinds
    #frame
    #endGame
    #connStatus
    #endState

    constructor(leftPlayer, rightPlayer, remote = 0) {
        this.#leftPlayer = leftPlayer;
        this.#rightPlayer = rightPlayer;
        this.#scoreLimit = 11;
        this.#background = new Image();
        this.#marvin = new Image();
        this.#background.src = './srcs/assets/game/table.svg';
        this.#marvin.src = './srcs/assets/imgs/marvin.png';
        this.#backgroundLoaded = false;
        this.#background.onload = () => { this.#backgroundLoaded = true; };
        this.#remote = remote; 
        this.#defLocalBinds = {up : "w", down : "s",
            left : "UNUSED_DEFAULT_KEY", right : "UNUSED_DEFAULT_KEY"};
        this.#defRemoteBinds = {up : "ru", down : "rd",
            left : "UNUSED_DEFAULT_KEY", right : "UNUSED_DEFAULT_KEY"};
        this.#frame = -5;
        this.#endGame = 0;
        this.#connStatus = "Waiting for Match ..."; 
        this.#endState = {};
    }
    
    startScreen() {
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (this.#backgroundLoaded) {
            this.statusToText()
            if (this.#remote == "ai")
                this.setupAI();
            if (this.#remote == 0 || this.#remote == 2)
                requestAnimationFrame(() => this.gameSetup());
            else {
                //handleMatchmaking(this);
                requestAnimationFrame(() => this.conectingScreen());
            }
        }
        else {
            ctx.fillText(`Loading ...`, 50, 30);
            //console.log(this.#backgroundLoaded);
            requestAnimationFrame(() => this.startScreen());
        }

    }

    conectingScreen(){
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillText(`${this.#connStatus} ... `, 50, 30);
        if (this.#connStatus != 'Game Ready'){
            requestAnimationFrame(() => this.conectingScreen());
        }
        else{ 
            //console.log("going to setup");
            requestAnimationFrame(() => this.gameSetup());
            activateGame();
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
        if (this.statusToText() != "remote"){
            if (this.#leftPlayer.score > this.#rightPlayer.score) {
                ctx.font = '80pt VT323';
                ctx.fillText(`Winner`, 310, 60);
                ctx.font = '30pt VT323';
                ctx.fillText(`${this.#leftPlayer.name}`, 380, 340, 200);
            } else {
                ctx.font = '80pt VT323';
                ctx.fillText(`Winner`, 310, 60);
                ctx.font = '30pt VT323';
                if (this.#rightPlayer.name == "Marvin") {
                    ctx.drawImage(this.#marvin, 360, 130, 140, 140);
                }
                ctx.fillText(`${this.#rightPlayer.name}`, 380, 340, 200);
            }
        } else {
            ctx.font = '80pt VT323';
            ctx.fillText(`Winner`, 310, 60);
            ctx.font = '30pt VT323';
            ctx.fillText(`${this.#endState["winner_username"]}`, 380, 340, 200);
            //ctx.drawImage(`${this.#endState["winner_avatar"]}`, 200, 200, canvas.width / 2, canvas.height /2);
        }
        //ctx.drawImage("/", 200, 200, canvas.width / 2, canvas.height /2);
        ctx.font = '26pt VT323';
        ctx.fillText(`Thanks for playing!`, 305, 470);
        
        if (keysPressed["Enter"])
            //requestAnimationFrame(() => this.gameSetup());
            // Using location.assign()
            // window.location.href='/play!';
            ;
         else
            requestAnimationFrame(() => this.endScreen());
    }


    checkStopCondition(){
        if(this.statusToText() != "remote"){
            console.log("thsn");
            if(this.#leftPlayer.score >= this.#scoreLimit
                || this.#rightPlayer.score >= this.#scoreLimit)
                return true;
            return false
        }   
        else{
            if(this.#endGame == 1)
                return true;
            return false;
        } 
    }

    // game loop
    pointLoop() {
        this.drawNonInteractive();
        if (this.statusToText() == "remote"){
            this.remoteGameLogic();
        }
        else 
            this.localGameLogic();
        this.drawInteractive();
        this.drawScore();
        if (this.checkStopCondition())
            requestAnimationFrame(() => this.endScreen());
        else
            requestAnimationFrame(() => this.pointLoop());
		this.#frame += 1;
    }
 
    
    remoteGameLogic() {
       // this.updateRemoteCanvas();
       let canvas = this.#remoteCanvas;
       //console.log("remote game logic", canvas)
        
        if (canvas === undefined){
            // console.log("undefined canvas");
            return;
        }
        this.#ball.setPosition(canvas["ball"]["position"]);
        this.#ball.setSpeed(canvas["ball"]["speed"]);
        this.#ball.setSize(canvas["ball"]["size"]);
        this.#leftPaddle.setPosition(canvas["leftPaddle"]["position"]);
        this.#leftPaddle.setSize(canvas["leftPaddle"]["size"]);
        this.#rightPaddle.setPosition(canvas["rightPaddle"]["position"]);
        this.#rightPaddle.setSize(canvas["rightPaddle"]["size"]);
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
        } 
       //console.log(keysPressed);
		this.#leftPaddle.updatePosition();
        this.#rightPaddle.updatePosition();
    }

    drawNonInteractive() {
        ctx.font = '20pt VT323';
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
        //ctx.fillText(this.#remoteIAM, canvas.width / 2, 40);
        
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

    async gameSetup() {
          this.#ball = new Ball({ x: canvas.width / 2, y: canvas.height / 2 },
            { x: 4, y: 3 }, { x: 10, y: 10 });
            this.resetPosition();
            this.#leftPaddle = new Paddle({ x: 30, y: 0 }, { x: 0, y: 10 },
            { x: 10, y: 100 }, "white",
            this.#leftPlayer.binds);
            this.#rightPaddle = new Paddle({ x: canvas.width - 30, y: 0 }, { x: 0, y: 10 },
            { x: 10, y: 100 }, "white",
            this.#rightPlayer.binds);
            if (this.#remote == 1)
                this.remoteGameSetup();
			if(this.#remote == 2){
				this.setupAI();
			}
            this.#rightPlayer.resetScore();
            this.#leftPlayer.resetScore();
            this.#ball.addColider(this.#leftPaddle);
            this.#ball.addColider(this.#rightPaddle);
            requestAnimationFrame(() => this.pointLoop());
        }
        
    async remoteGameSetup(){
        try{
            const url = `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/`;
            const options = {
                method: "GET",
                mode: "cors",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                  }};
                //console.log(url)
            const response = await makeRequest(true,url, options,"");
            this.#leftPlayer.name = response.player1.username;
            this.#rightPlayer.name = response.player2.username;
            //console.log(response);
        }
        catch (error)
        {
            console.error(error);
        }
        document.addEventListener('keydown', (event) => {
            // Handle arrow key presses and send messages to the server
            handleArrowKeyPress(event.key);
        });

        document.addEventListener('keyup', (event) => {
            // Handle arrow key releases and send messages to the server
            handleArrowKeyRelease(event.key);
        });
    }

    conexionSetup() {
        handleMatchmaking(this);
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
   
    receiveRemoteCanvas(data){
        //console.log("recieving", data.data.game_update)
        this.#remoteCanvas = data.data.game_update; 
        this.#leftPlayer.score = data.data.left_score;
        this.#rightPlayer.score = data.data.right_score;
        
    }

    scoreUpdate(data){
        //console.log(data)
        this.#leftPlayer.score = data["left"];
        this.#rightPlayer.score = data["right"];
    }

   
    remoteGameEnd(data){
        this.#endGame = 1;
        this.#endState = data.data;
    }
    
    set connStatus (data){
        this.#connStatus = data;
    }

	get frame(){
		return this.#frame;
	}

}