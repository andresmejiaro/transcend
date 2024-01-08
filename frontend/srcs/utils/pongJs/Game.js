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
    #playersConnected
    #remoteIAM
    #defLocalBinds
    #defRemoteBinds
    #frame
    #remoteCanvasQ
    #delay
    #endGame
    #actualframe;
    #connStatus;

    constructor(leftPlayer, rightPlayer, remote = 0) {
        this.#leftPlayer = leftPlayer;
        this.#rightPlayer = rightPlayer;
        this.#scoreLimit = 11;
        this.#background = new Image();
        this.#background.src = './srcs/assets/game/table.svg';
        this.#backgroundLoaded = false;
        this.#background.onload = () => { this.#backgroundLoaded = true; };
        this.#remote = remote; 
        this.#playersConnected = 0;
        this.#remoteIAM = "none";
        this.#defLocalBinds = {up : "w", down : "s",
            left : "UNUSED_DEFAULT_KEY", right : "UNUSED_DEFAULT_KEY"};
        this.#defRemoteBinds = {up : "ru", down : "rd",
            left : "UNUSED_DEFAULT_KEY", right : "UNUSED_DEFAULT_KEY"};
        this.#frame = -5;
        this.#remoteCanvasQ = {};
        this.#delay = 0;
        this.#endGame = 0;
        this.#actualframe = 0;
        this.#connStatus = "Waiting for Match ..."; 
    }
    
    startScreen() {
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (this.#backgroundLoaded) {
            if (this.statusToText() == "ai")
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
            console.log("going to setup");
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
        if (this.#leftPlayer.score > this.#rightPlayer.score)
            ctx.fillText(`Winner: ${this.#leftPlayer.name}`, 100, 100);
        else
            ctx.fillText(`Winner: ${this.#rightPlayer.name}`, 100, 100);
        ctx.fillText(`Thanks for playing to play again press Enter`, 50, 30);
        if (keysPressed["Enter"])
            //requestAnimationFrame(() => this.gameSetup());
            // Using location.assign()
            window.location.href('/play');
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
            || this.#rightPlayer.score >= this.#scoreLimit || 
                this.#endGame == 1)
            requestAnimationFrame(() => this.endScreen());
        else
            requestAnimationFrame(() => this.pointLoop());
    }
    
    updateRemoteCanvas(){
        //try to print from memory
        if (this.#remoteCanvasQ[this.#actualframe]){
            this.#remoteCanvas= this.#remoteCanvasQ[this.#actualframe];
            this.#actualframe += 1;
            this.#delay = 0;
            // console.log("printing from memory");
            return;
        } else{
            // try to find if skipped
            let lowestHigherNumber = Math.min(...Object.keys(this.#remoteCanvasQ).
            map(Number).filter(key => key > this.#actualframe));
            if (isFinite(lowestHigherNumber)){
                this.#actualframe = lowestHigherNumber;
                this.#remoteCanvas= this.#remoteCanvasQ[this.#actualframe];
                return;
            }
        
        }
        if (!this.#remoteCanvasQ[this.#actualframe + this.#delay]){
            this.#delay = Math.max(...Object.keys(this.#remoteCanvasQ).map(Number)) - this.#actualframe;
            // console.log(this.#delay);
        }
        if (isFinite(this.#delay)){
            this.#remoteCanvas = this.#remoteCanvasQ[this.#frame + this.#delay]
        }
    }
    
    async remoteGameLogic() {
        this.updateRemoteCanvas();
        let canvas = this.#remoteCanvas;
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
        if (isFinite(this.#delay) && this.#delay < 0){
                for (let i = 0; i < Math.max(0, -this.#delay); i++){
                this.localGameLogic2();
            }
        }
        
        
        this.#frame += 1;
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

    localGameLogic2() {
        this.#ball.updatePosition();
        this.#leftPaddle.updatePosition();
        this.#rightPaddle.updatePosition();
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
            this.#rightPlayer.resetScore();
            this.#leftPlayer.resetScore();
            this.#ball.addColider(this.#leftPaddle);
            this.#ball.addColider(this.#rightPaddle);
            requestAnimationFrame(() => this.pointLoop());
        }
        
    remoteGameSetup(){
        if (this.#remote == 1 && this.#remoteIAM == "right"){
            this.#rightPaddle.binds = this.#defLocalBinds;
            this.#leftPaddle.binds = this.#defRemoteBinds;
        }
        if (this.#remote == 1 && this.#remoteIAM == "left"){
            this.#leftPaddle.binds = this.#defLocalBinds;
            this.#rightPaddle.binds = this.#defRemoteBinds;
        }
        this.#leftPaddle.initializePaddleKeys();
        this.#rightPaddle.initializePaddleKeys();
        if(this.#remote == 1){
            document.addEventListener('keydown', (event) => {
                handleArrowKeyPress(event.key);
            });
            document.addEventListener('keyup', (event) => {
                handleArrowKeyRelease(event.key);
            });
            // document.addEventListener('keydown', (event) => {
            //     if (event.key == "w")
            //         sendKeyPress("up",this.#remoteIAM, this.#frame);
            //     if(event.key == "s")
            //         sendKeyPress("down",this.#remoteIAM, this.#frame);
            // });
            // document.addEventListener('keyup', (event) => {
            //     if (event.key == "w")
            //         sendRelease("up", this.#remoteIAM, this.#frame);
            //     if(event.key == "s")
            //         sendRelease("down",  this.#remoteIAM, this.#frame);
            // });
        }
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

    async updatePlayerNames(data){
        let names = Object.keys(data.data);
        let name1 = await getPlayerInfo(names[0]);
        let name2;
        this.#leftPlayer.name = name1.username;
        if (names.length > 1){
            
            try{
                name2 = await getPlayerInfo(names[1]);
                this.#rightPlayer.name = name2.username;
            }
            catch(error){
                console.error(error);
                console.error(names, names.length,data)
            }
        }
        this.#playersConnected = names.length; 

       
        if (name1.username == sessionStorage.getItem("username")){
            this.#remoteIAM = "left";
        }
        if (name2 && name2.username == sessionStorage.getItem("username")){
            this.#remoteIAM = "right";
        }
    }

    receiveRemoteCanvas(data){

        data.data.forEach(item => {
            let frame = item.frame;
            let gameUpdate = item.game_update;
            this.#remoteCanvasQ[frame] = gameUpdate; 
        });
    }

    scoreUpdate(data){
        //console.log(data)
        this.#leftPlayer.score = data["left"];
        this.#rightPlayer.score = data["right"];
    }

    remoteKeyUpHandling(data){
        if (["left", "right"].includes(data.data.side)){
            if (data.data.side != this.#remoteIAM){
                // console.log(data);
                let keyToPress;
                if (data.data.key == "down"){
                    keyToPress = this.#defRemoteBinds["down"];
                    
                }
                if (data.data.key == "up"){
                    keyToPress = this.#defRemoteBinds["up"];
                    
                }
                let status;
                if (data.data.key_status == "on_press")
                    status = true;
                if (data.data.key_status == "on_release")
                    status = false;
                keysPressed[keyToPress] = status;
               // console.log(keyToPress,data.data.key,keysPressed[keyToPress], data.data.key_status);
            }
        }
    }

    remoteGameEnd(){
        this.#endGame = 1;
    }
    
    set connStatus (data){
        this.#connStatus = data;
    }

}



