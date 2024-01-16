class Paddle extends MovingRectangle{
    #binds;
    #maxSpeed;
    

    constructor(position = {x : 30, y : 0}, speed = {x : 0, y : 10},
        size = {x : 10, y : 30}, color = "white",
        binds ={up : "UNUSED_DEFAULT_KEY", down : "UNUSED_DEFAULT_KEY",
        left : "UNUSED_DEFAULT_KEY", right : "UNUSED_DEFAULT_KEY"}){
        super();
        super.initialize(position, speed, size, color);
        this.#binds = binds;
        this.#maxSpeed = speed;
        this.setSpeed= {x:0,y:0};
        this.initializePaddleKeys();
    }

    set binds(data){
        this.#binds =data;
    }

    get getMaxSpeed(){
        return this.#maxSpeed;
    }

     updatePosition() {
        let xSpeed = 0;
        let ySpeed = 0;
		
    
        xSpeed = (keysPressed[this.#binds.right]
            - keysPressed[this.#binds.left])*this.getMaxSpeed.x;
        ySpeed = (keysPressed[this.#binds.down]
            - keysPressed[this.#binds.up])*this.getMaxSpeed.y;
		
		//console.log(this.#binds.down,keysPressed, "1");
        if (Number.isNaN(xSpeed)){
			xSpeed = 0;
		}
		if (Number.isNaN(ySpeed)){
			ySpeed = 0;
		}
		if (xSpeed < 0 && this.getPosition.x <= 0){
			xSpeed = 0;
		}
		if (ySpeed < 0 && this.getPosition.y <= 0){
			ySpeed = 0;
		}
		if (xSpeed > 0 && this.getPosition.x + this.getSize.x >= canvas.width){
			xSpeed = 0;
		}
		if (ySpeed > 0 && this.getPosition.y + this.getSize.y >= canvas.height){
			ySpeed = 0;
		}
		let xNewPos = super.getPosition.x + xSpeed;
		if (xNewPos < 0)
            xNewPos = 0;
        if (xNewPos + this.getSize.x > canvas.width)
            xNewPos = canvas.width - this.getSize.x;
		let yNewPos = super.getPosition.y + ySpeed;
		if (yNewPos < 0)
            yNewPos = 0;
        if (yNewPos + this.getSize.y > canvas.height)
            yNewPos = canvas.height - this.getSize.y;
		super.setPosition({x: xNewPos, 
                    y : yNewPos});
    }

    initializePaddleKeys(){
        Object.values(this.#binds).forEach( bind => 
            {keysPressed[bind] = false;});
    }

    draw() {
        ctx.fillStyle = "gray";
        ctx.fillRect(this.getPosition.x - 1, this.getPosition.y - 1, 
            this.getSize.x + 2, this.getSize.y + 2);
        ctx.fillStyle = "white";
        ctx.fillRect(this.getPosition.x, this.getPosition.y, 
            this.getSize.x, this.getSize.y);
        ctx.fillStyle = "orange";
        ctx.fillRect(this.getPosition.x, this.getPosition.y, 5, 5);
        ctx.fillRect(this.getPosition.x + this.getSize.x - 5,
            this.getPosition.y + this.getSize.y - 5, 5, 5);
        ctx.fillRect(this.getPosition.x, 
            this.getPosition.y + this.getSize.y - 5, 5, 5);
        ctx.fillRect(this.getPosition.x + this.getSize.x - 5,
            this.getPosition.y, 5, 5);
        ctx.fillStyle = "white";
        }
    }