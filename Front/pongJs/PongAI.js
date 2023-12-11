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
        this.internalKeyUpdate();       
    }
    
    internalKeyUpdate(){
        let ycenter = this.#canvas['rightPaddle']['position']['y'] + 
            this.#canvas['rightPaddle']['size']['y'] /2 ; 
        if (this.#collisionPoint > ycenter){
            this.pressDown();             
        } else
            this.pressUp();
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
                this.#collisionPoint = canvas.height - collisionPoint % canvas.height;
            else 
                this.#collisionPoint = collisionPoint % canvas.height;
            return;
        }
        this.#collisionPoint = canvas.height / 2;        
    }

    pressUp(){
        keysPressed[this.#binds["up"]] = true;           
        keysPressed[this.#binds["down"]] = false;     
    }
    
    pressDown(){
        keysPressed[this.#binds["up"]] = false;           
        keysPressed[this.#binds["down"]] = true;     
    }
}