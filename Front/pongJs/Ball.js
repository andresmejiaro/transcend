class Ball extends MovingRectangle {
    #collide

    constructor(position = { x: 0, y: 0 }, speed = { x: 0, y: 0 }, 
        size = { x: 0, y: 0 }, color = "white") {
        super();
        super.initialize(position, speed, size, color);
        this.#collide = [];
    }

    checkCollision(collider) {
        // Check if upper right corner is touching the collider
        if (collider.getCorners.xl <= this.getCorners.xl &&
            this.getCorners.xl <= collider.getCorners.xh &&
            collider.getCorners.yl <= this.getCorners.yl &&
            this.getCorners.yl <= collider.getCorners.yh) {
            return true;
        }
        // Check if upper left corner is touching the collider
        if (collider.getCorners.xl <= this.getCorners.xh &&
            this.getCorners.xh <= collider.getCorners.xh &&
            collider.getCorners.yl <= this.getCorners.yl &&
            this.getCorners.yl <= collider.getCorners.yh) {
            return true;
        }
        // Check if lower right corner is touching the collider
        if (collider.getCorners.xl <= this.getCorners.xl &&
            this.getCorners.xl <= collider.getCorners.xh &&
            collider.getCorners.yl <= this.getCorners.yh &&
            this.getCorners.yh <= collider.getCorners.yh) {
            return true;
        }
        // Check if lower left corner is touching the collider
        if (collider.getCorners.xl <= this.getCorners.xh &&
            this.getCorners.xh <= collider.getCorners.xh &&
            collider.getCorners.yl <= this.getCorners.yh &&
            this.getCorners.yh <= collider.getCorners.yh) {
            return true;
        }
        return false;
    }

    collisionHandler(colider) {
        if (this.checkCollision(colider)) {
            //Calculate the left and right side of the "inscribed square of the intersection"
            const leftInter = Math.max(this.getCorners.xl, colider.getCorners.xl);
            const rightInter = Math.min(this.getCorners.xh, colider.getCorners.xh);
            // const topInter = Math.max(this.getCorners.yl, colider.getCorners.yl);
            //const bottomInter = Math.min(this.getCorners.yh, colider.getCorners.yh);
            // calculate the proportion of the movement that overlaps
            const adj = Math.abs(leftInter - rightInter) / Math.abs(this.getSpeed.x);
            // undo overlaping
            this.setPosition({
                x: this.getPosition.x - adj * this.getSpeed.x,
                y: this.getPosition.y - adj * this.getSpeed.y
            });
            // This calculates the "nearest side and considers that collition as such"
            const x1 = Math.abs(this.getCorners.xl - colider.getCorners.xh);
            const x2 = Math.abs(this.getCorners.xh - colider.getCorners.xl);
            const y1 = Math.abs(this.getCorners.yl - colider.getCorners.yh);
            const y2 = Math.abs(this.getCorners.yh, colider.getCorners.yh);
            // Set speed and friction effect
            if (Math.min(x1, x2) < Math.min(y1, y2)) {
                super.setSpeed({ x: -super.getSpeed.x , y: this.getSpeed.y 
                                                    + 0.5 * colider.getSpeed.y});
            } else {
                super.setSpeed({ y: -super.getSpeed.y });
            }
        }

    }

    updatePosition() {
        if (super.getPosition.x + super.getSize.x >= canvas.width) {
            super.setSpeed({x: -super.getSpeed.x});
            return 1;
        }
        if (super.getPosition.x < 0) {
            super.setSpeed({x: -super.getSpeed.x});
            return -1;
        }
        if (super.getPosition.y + super.getSize.y >= canvas.height
            || super.getPosition.y < 0) {
            super.setSpeed({y: -super.getSpeed.y});
        }
        Object.values(this.#collide).forEach(ele => this.collisionHandler(ele));
        super.setPosition({
            x: super.getPosition.x + super.getSpeed.x,
            y: super.getPosition.y + super.getSpeed.y
        })
        return 0;
    }

    addColider(colider) {
        this.#collide.push(colider);
    }

}
