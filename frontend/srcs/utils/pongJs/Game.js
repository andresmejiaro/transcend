class Game {
    #leftPlayer
    #rightPlayer
    #scoreLimit
    #ball
    #leftPaddle
    #rightPaddle
    #background
    #backgroundLoaded
    
    constructor(leftPlayer, rightPlayer){
        this.#leftPlayer = leftPlayer;
        this.#rightPlayer = rightPlayer;
        this.#scoreLimit  = 11;
        this.#background = new Image();
        this.#background.src = './assets/game/table.svg';
        this.#backgroundLoaded = false;
        this.#background.onload = () => {this.#backgroundLoaded = true ;};
    }
    
    startScreen(){
        
        ctx.clearRect(0,0, canvas.width, canvas.height);
        if (this.#backgroundLoaded){
            ctx.fillText(`Press Enter to Start`, 50, 30);
            if (keysPressed["Enter"])
                requestAnimationFrame(() => this.gameSetup());
            else
               requestAnimationFrame(() => this.startScreen());
        }
        else {
            ctx.fillText(`Loading ...`, 50, 30);
            console.log(this.#backgroundLoaded);
            requestAnimationFrame(() => this.startScreen());
        }

    }

    endScreen(){
        ctx.clearRect(0,0, canvas.width, canvas.height);
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

pointLoop(){
    ctx.clearRect(0,0, canvas.width, canvas.height);
    ctx.drawImage(this.#background, 0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    this.#ball.draw()
    let ballState = this.#ball.updatePosition();
    if (ballState == 1){
        this.#leftPlayer.goal();
        this.resetPosition();
    }
    else if (ballState == -1){
        this.#rightPlayer.goal();
        this.resetPosition();
    } else {
        this.#leftPaddle.draw();
        this.#leftPaddle.updatePosition();
	    this.#rightPaddle.draw();
	    this.#rightPaddle.updatePosition();
    }
    const text1 = `${this.#leftPlayer.name}: ${this.#leftPlayer.score}`;
    const text2 = `${this.#rightPlayer.name}: ${this.#rightPlayer.score}`;
    const p1metrics = ctx.measureText(text1);
    const p2metrics = ctx.measureText(text2);
    ctx.fillText(text1, canvas.width/4 - p1metrics.width/2, 40);
    ctx.fillText(text2, canvas.width*3/4 - p2metrics.width/2, 40);
    if (this.#leftPlayer.score >= this.#scoreLimit 
        || this.#rightPlayer.score >= this.#scoreLimit)
        requestAnimationFrame(() => this.endScreen());
    else 
        requestAnimationFrame(() => this.pointLoop());
}

resetPosition(){
    this.#ball.setPosition({x:canvas.width/2,y:canvas.height/2});
    let ran = Math.random();
    if (ran < 0.25)
        this.#ball.setSpeed({x:4, y:1});
    else if(ran < 0.5)
        this.#ball.setSpeed({x:-4, y:1});
    else if(ran < 0.75)
        this.#ball.setSpeed({x:4, y:-1});
    else 
        this.#ball.setSpeed({x:-4, y:-1});

        
}

gameSetup(){
    this.#ball = new Ball({x:canvas.width/2,y:canvas.height/2},
                        {x:4, y:3},{x:10,y:10});
    this.resetPosition(); 
    this.#leftPaddle = new Paddle ({x:30,y:0},{x:10,y:10},
	    {x:10,y:100}, "white",
	    this.#leftPlayer.binds);
    this.#rightPaddle = new Paddle ({x:canvas.width-30,y:0},{x:10,y:10},
		{x:10,y:100}, "white",
		this.#rightPlayer.binds);
    this.#rightPlayer.resetScore();
    this.#leftPlayer.resetScore();

    this.#ball.addColider(this.#leftPaddle);
    this.#ball.addColider(this.#rightPaddle);
   
    requestAnimationFrame(() => this.pointLoop());        
        
}

    start(){
        requestAnimationFrame(() => this.startScreen());
    }
}
