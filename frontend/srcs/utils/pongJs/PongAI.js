class PongAI {
    #side
    #binds
    #lastCanvas
    #canvas
    #game
    #ballspeed
    #collisionPoint
 
    constructor(player, game, side = 1){
        this.#side = side;
        this.#binds =  player.binds;
        this.#side = side;
        this.#game = game;
        this.#ballspeed = {x: 3, y: 1}  
        this.#collisionPoint = canvas.height / 2;  
		this.#game = game;
    }

    keyboardUpdate(){
        if (this.#lastCanvas === undefined){
            this.#lastCanvas = this.#game.getCanvas();
            return;
        }
        if (this.#canvas !== undefined){
            this.#lastCanvas = this.#canvas;
        }
        this.#canvas = game.getCanvas();
        this.updateBallSpeed();
        this.calculateCollisionPoint()
        this.deadCenterMethod();
    }
    

    keyUpdater(target){
        let ycenter = this.#canvas['rightPaddle']['position']['y'] + 
            this.#canvas['rightPaddle']['size']['y'] /2 ; 
        if (target > ycenter + this.#canvas['rightPaddle']['size']['y'] / 5){
            this.pressDown();             
        } else if (target < ycenter - this.#canvas['rightPaddle']['size']['y'] / 5)
            this.pressUp();
        else
            this.pressNone();
    }

    deadCenterMethod(){
        this.keyUpdater(this.#collisionPoint);
    }

 

 
    updateBallSpeed(){
        if (this.#canvas !== undefined && this.#lastCanvas !== undefined){
            this.#ballspeed["x"] = this.#canvas["ball"]["position"]["x"] - 
                this.#lastCanvas["ball"]["position"]["x"];
            this.#ballspeed["y"] = this.#canvas["ball"]["position"]["y"] - 
                this.#lastCanvas["ball"]["position"]["y"];
        }
    }

    calculateCollisionPoint(){
        let offset = 90 * Math.sin(this.#game.frame/10);
        //let offset = Math.sin(this.#game.frame/17);
		//console.log(offset);
		if (this.#ballspeed["x"] > 0){
            let remainingX = this.#canvas["rightPaddle"]["position"]["x"] -
                + this.#canvas["ball"]["position"]["x"];
            let collisionPoint = this.#canvas["ball"]["position"]["y"] +
                this.#ballspeed["y"] * remainingX /this.#ballspeed["x"];
            if (collisionPoint < 0){
                collisionPoint = -collisionPoint;
            }
            let nScreens = Math.floor(collisionPoint/canvas.height);
            collisionPoint = collisionPoint % canvas.height;
            if (nScreens % 2 == 1)
                this.#collisionPoint = canvas.height - collisionPoint % canvas.height + offset;
            else 
                this.#collisionPoint = collisionPoint % canvas.height + offset;
            return;
        }
        this.#collisionPoint = canvas.height / 2 + offset;        
    }
    
    
    pressUp(){
        keysPressed[this.#binds["up"]] = true;           
        keysPressed[this.#binds["down"]] = false;     
    }
    
    pressDown(){    
        keysPressed[this.#binds["up"]] = false;           
        keysPressed[this.#binds["down"]] = true;     
    }
    
    pressNone(){
        keysPressed[this.#binds["up"]] = false;           
        keysPressed[this.#binds["down"]] = false;     
    }
}