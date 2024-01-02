class Player {
    #name
    #binds
    #score
    #ai

    constructor(name = "Player", binds = {up:"UNUSED_DEFAULT_KEY", 
    down:"UNUSED_DEFAULT_KEY", left:"UNUSED_DEFAULT_KEY", 
    right:"UNUSED_DEFAULT_KEY"}){
        this.#name = name;
        this.#binds = binds;
        this.#score = 0;
        this.#ai = false;
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

    set name(data){
        this.#name = data;
    }

    get binds(){
        return this.#binds;
    }

    get ai(){
        return this.#ai;
    }
    
    set binds(data){
        this.#binds = data;
    }

    goal(){
        this.#score += 1;
    }
    
    resetScore(){
        this.#score = 0;
    }

    toggleAI(){
        this.#ai = 1 - this.#ai;
    }

    
}   