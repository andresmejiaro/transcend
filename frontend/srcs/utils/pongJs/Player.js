class Player {
    #name
    #binds
    #score

    constructor(name = "Player", binds = {up:"UNUSED_DEFAULT_KEY", 
    down:"UNUSED_DEFAULT_KEY", left:"UNUSED_DEFAULT_KEY", 
    right:"UNUSED_DEFAULT_KEY"}){
        this.#name = name;
        this.#binds = binds;
        this.#score = 0;
    }

    get score(){
        return this.#score;
    }

    set score(value){
        this.#score = value;
    }
    
    get name(){
        return this.#name;
    }

    get binds(){
        return this.#binds;
    }

    set name(value){
        this.#name = value;
    }
    
    goal(){
        this.#score += 1;
    }
    
    resetScore(){
        this.#score = 0;
    }

}   