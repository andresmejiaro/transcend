class PongAI {
    #binds
    #lastCanvas
    #canvas
    #game
    #ballspeed
    #collisionPoint
    #difficulty

    constructor(player, game){
        this.#binds =  player.binds;
        this.#game = game;
        this.#ballspeed = {x: 3, y: 1}  
        this.#collisionPoint = canvas.height / 2;  
        this.#difficulty = 9;
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
            this.#canvas['rightPaddle']['size']['y'] / 2 ; 
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
            this.#collisionPoint += canvas.height/4 * (10 - this.#difficulty) * Math.sin(game.frame / 17);
            return;
        }
        this.#collisionPoint = canvas.height / 2 + (10 - this.#difficulty)*canvas.height/4 * Math.sin(game.frame / 17 );
        
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