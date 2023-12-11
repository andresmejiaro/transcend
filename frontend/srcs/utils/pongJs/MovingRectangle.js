class MovingRectangle {
    #position
    #speed
    #size
    #color;
    #corners;
    
    constructor() {
        if (new.target === MovingRectangle){
            throw new Error('MovingRectangle is an abstract class.')
        }
    }
    
    initialize(position ={x:0,y:0}, speed ={x:0,y:0}, size ={x:0,y:0},
         color = "white") {
        this.#position = position;
        this.#speed = speed;
        this.#size = size;
        this.#color = color;
        ctx.fillStyle = this.#color;
        this.updateCorners();
        
    }

    get getPosition(){
        return this.#position;
    }
    get getSpeed(){
        return this.#speed;
    }
    get getSize(){
        return this.#size;
    }

    get getColor(){
        return this.#color;
    }

    get getCorners(){
        return this.#corners;
    }

    updateCorners(){
        //first 2 components x, second two components y
        this.#corners = {xl:this.getPosition.x, 
            xh:this.getPosition.x + this.getSize.x,
                yl:this.getPosition.y, yh:this.getPosition.y + this.getSize.y};
    }
    
    setPosition({x = this.#position[x], y = this.#position[y]}){
        this.#position = {x,y};
        this.updateCorners();
    }

    setSpeed({x = this.#speed.x, y = this.#speed.y}){
        this.#speed = {x,y};
    }

    setSize({x = this.#size.x, y = this.#size.y}){
        this.#size = {x,y};
    }

    setColor(color){
        this.#color = color;
    }

    draw() {

        ctx.fillRect(this.#position.x, this.#position.y, 
            this.#size.x, this.#size.y);
    }

    updatePosition(){
        throw new Error('MovingRectangle is an abstract class.')
    }
  
}

