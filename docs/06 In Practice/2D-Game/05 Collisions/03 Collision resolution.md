# 碰撞处理

At the end of the last tutorial we had a working collision detection scheme. However, the ball does not react in any way to the detected collisions; it just moves straight through all the bricks. We want the ball to *bounce* of the collided bricks. This tutorial discusses how we can accomplish this so called collision resolution within the AABB - circle collision detection scheme.

Whenever a collision occurs we want two things to happen: we want to reposition the ball so it is no longer inside the other object and second, we want to change the direction of the ball's velocity so it looks like its bouncing of the object.

### Collision repositioning

To position the ball object outside the collided AABB we have to figure out the distance the ball penetrated the bounding box. For this we'll revisit the diagrams from the previous tutorial:

Here the ball moved slightly into the AABB and a collision was detected. We now want to move the ball out of the shape so that it merely touches the AABB as if no collision occurred. To figure out how much we need to move the ball out of the AABB we need to retrieve the vector R¯R¯ which is the level of penetration into the AABB. To get this vector R¯R¯ we subtract V¯V¯ from the ball's radius. Vector V¯V¯ is the difference between closest point P¯P¯ and the ball's center C¯C¯.

Knowing R¯R¯ we offset the ball's position by R¯R¯ and position the ball directly alongside the AABB; the ball is now properly positioned.

### Collision direction

Next we need to figure out how to update the ball's velocity after a collision. For Breakout we use the following rules to change the ball's velocity:

1. If the ball collides with the right or left side of an AABB, its horizontal velocity (`x`) is reversed.
2. If the ball collides with the bottom or top side of an AABB, its vertical velocity (`y`) is reversed.

But how do we figure out the direction the ball hit the AABB? There are several approaches to this problem and one of them is that instead of 1 AABB we use 4 AABBs for each brick that we position each at one of its edges. This way we can determine which AABB and thus which edge was hit. However, a simpler approach exists with the help of the dot product.

You probably still remember from the [transformations](https://learnopengl.com/#!Getting-started/Transformations) tutorial that the dot product gives us the angle between two normalized vectors. What if we were to define four vectors pointing north, south, west or east and calculate the dot product between them and a given vector? The resulting dot product between these four direction vectors and the given vector that is highest (dot product's maximum value is `1.0f` which represents a `0` degree angle) is then the direction of the vector.

This procedure looks as follows in code:

```
Direction VectorDirection(glm::vec2 target)
{
    glm::vec2 compass[] = {
        glm::vec2(0.0f, 1.0f),	// up
        glm::vec2(1.0f, 0.0f),	// right
        glm::vec2(0.0f, -1.0f),	// down
        glm::vec2(-1.0f, 0.0f)	// left
    };
    GLfloat max = 0.0f;
    GLuint best_match = -1;
    for (GLuint i = 0; i < 4; i++)
    {
        GLfloat dot_product = glm::dot(glm::normalize(target), compass[i]);
        if (dot_product > max)
        {
            max = dot_product;
            best_match = i;
        }
    }
    return (Direction)best_match;
}    
```

The function compares target to each of the direction vectors in the compass array. The compass vector target is closest to in angle, is the direction returned to the function caller. Here Direction is part of an enum defined in the game class's header file:

```
enum Direction {
	UP,
	RIGHT,
	DOWN,
	LEFT
};    
```

Now that we know how to get vector R¯R¯ and how to determine the direction the ball hit the AABB we can start writing the collision resolution code.

### AABB - Circle collision resolution

To calculate the required values for collision resolution we need a bit more information from the collision function(s) than just a `true` or `false` so we're going to return a tuple of information, namely if a collision occurred, what direction it occurred and the difference vector (R¯R¯). You can find the `tuple` container in the `<tuple>` header.

To keep the code slightly more organized we'll typedef the collision relevant data as Collision:

```
typedef std::tuple<GLboolean, Direction, glm::vec2> Collision;    
```

Then we also have to change the code of the CheckCollision function to not only return `true` or `false`, but also the direction and difference vector:

```
Collision CheckCollision(BallObject &one, GameObject &two) // AABB - AABB collision
{
    [...]
    if (glm::length(difference) <= one.Radius)
        return std::make_tuple(GL_TRUE, VectorDirection(difference), difference);
    else
        return std::make_tuple(GL_FALSE, UP, glm::vec2(0, 0));
}
```

The game's DoCollision function now doesn't just check if a collision occurred, but also acts appropriately whenever a collision did occur. The function now calculates the level of penetration (as shown in the diagram at the start of this tutorial) and adds or subtracts it from the ball's position based on the direction of the collision.

```
void Game::DoCollisions()
{
    for (GameObject &box : this->Levels[this->Level].Bricks)
    {
        if (!box.Destroyed)
        {
            Collision collision = CheckCollision(*Ball, box);
            if (std::get<0>(collision)) // If collision is true
            {
                // Destroy block if not solid
                if (!box.IsSolid)
                    box.Destroyed = GL_TRUE;
                // Collision resolution
                Direction dir = std::get<1>(collision);
                glm::vec2 diff_vector = std::get<2>(collision);
                if (dir == LEFT || dir == RIGHT) // Horizontal collision
                {
                    Ball->Velocity.x = -Ball->Velocity.x; // Reverse horizontal velocity
                    // Relocate
                    GLfloat penetration = Ball->Radius - std::abs(diff_vector.x);
                    if (dir == LEFT)
                        Ball->Position.x += penetration; // Move ball to right
                    else
                        Ball->Position.x -= penetration; // Move ball to left;
                }
                else // Vertical collision
                {
                    Ball->Velocity.y = -Ball->Velocity.y; // Reverse vertical velocity
                    // Relocate
                    GLfloat penetration = Ball->Radius - std::abs(diff_vector.y);
                    if (dir == UP)
                        Ball->Position.y -= penetration; // Move ball back up
                    else
                        Ball->Position.y += penetration; // Move ball back down
                }
            }
        }
    }
}    
```

Don't get too scared by the function's complexity since it is basically a direct translation of the concepts introduced so far. First we check for a collision and if so we destroy the block if it is non-solid. Then we obtain the collision direction dir and the vector V¯V¯ as diff_vector from the tuple and finally do the collision resolution.

We first check if the collision direction is either horizontal or vertical and then reverse the velocity accordingly. If horizontal, we calculate the penetration value RR from the diff_vector's x component and either add or subtract this from the ball's position based on its direction. The same applies to the vertical collisions, but this time we operate on the `y` component of all the vectors.

Running your application should now give you a working collision scheme, but it's probably difficult to really see its effect since the ball will bounce towards the bottom edge as soon as you hit a single block and be lost forever. We can fix this by also handling player paddle collisions.

## Player - ball collisions

Collisions between the ball and the player are slightly different than what we've previously discussed since this time the ball's horizontal velocity should be updated based on how far it hit the paddle from its center. The further the ball hits the paddle from its center, the stronger its horizontal velocity should be.

```
void Game::DoCollisions()
{
    [...]
    Collision result = CheckCollision(*Ball, *Player);
    if (!Ball->Stuck && std::get<0>(result))
    {
        // Check where it hit the board, and change velocity based on where it hit the board
        GLfloat centerBoard = Player->Position.x + Player->Size.x / 2;
        GLfloat distance = (Ball->Position.x + Ball->Radius) - centerBoard;
        GLfloat percentage = distance / (Player->Size.x / 2);
        // Then move accordingly
        GLfloat strength = 2.0f;
        glm::vec2 oldVelocity = Ball->Velocity;
        Ball->Velocity.x = INITIAL_BALL_VELOCITY.x * percentage * strength; 
        Ball->Velocity.y = -Ball->Velocity.y;
        Ball->Velocity = glm::normalize(Ball->Velocity) * glm::length(oldVelocity);
    } 
}
  
```

After we checked collisions between the ball and each brick, we'll check if the ball collided with the player paddle. If so (and the ball is not stuck to the paddle) we calculate the percentage of how far the ball's center is removed from the paddle's center compared to the half-extent of the paddle. The horizontal velocity of the ball is then updated based on the distance it hit the paddle from its center. Aside from updating the horizontal velocity we also have to reverse the y velocity.

Note that the old velocity is stored as oldVelocity. The reason for storing the old velocity is that we only update the horizontal velocity of the ball's velocity vector while keeping its `y` velocity constant. This would mean that the length of the vector constantly changes which has the effect that the ball's velocity vector is much larger (and thus stronger) if the ball hit the edge of the paddle compared to if the ball would hit the center of the paddle. For this reason the new velocity vector is normalized and multiplied by the length of the old velocity vector. This way, the strength and thus the velocity of the ball is always consistent, regardless of where it hits the paddle.

### Sticky paddle

You may or may not have noticed it when you ran the code, but there is still a large issue with the player and ball collision resolution. The following video clearly shows what might happen:

This issue is called the sticky paddle issue which happens because the player paddle moves with a high velocity towards the ball that results in the ball's center ending up inside the player paddle. Since we did not account for the case where the ball's center is inside an AABB the game tries to continuously react to all the collisions and once it finally breaks free it will have reversed its `y` velocity so much that it's unsure whether it goes up or down after breaking free.

We can easily fix this behavior by introducing a small hack which is possible due to the fact that the we can assume we always have a collision at the top of the paddle. Instead of reversing the `y` velocity we simply always return a positive `y` direction so whenever it does get stuck, it will immediately break free.

```
 //Ball->Velocity.y = -Ball->Velocity.y;
Ball->Velocity.y = -1 * abs(Ball->Velocity.y);  
```

If you try hard enough the effect is still noticeable, but I personally find it an acceptable trade-off.

### The bottom edge

The only thing that is still missing from the classic Breakout recipe is some loss condition that resets the level and the player. Within the game class's Update function we want to check if the ball reached the bottom edge, and if so, reset the game.

```
void Game::Update(GLfloat dt)
{
    [...]
    if (Ball->Position.y >= this->Height) // Did ball reach bottom edge?
    {
        this->ResetLevel();
        this->ResetPlayer();
    }
}  
```

The ResetLevel and ResetPlayer functions simply re-load the level and reset the objects' values to their original starting values. The game should now look a bit like this:

And there you have it, we just finished creating a clone of the classical Breakout game with similar mechanics. You can find the game class' source code here: [header](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_collisions.h), [code](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_collisions).

## A few notes

Collision detection is a difficult topic of video game development and possibly its most challenging. Most collision detection and resolution schemes are combined with physics engines as found in most modern-day games. The collision scheme we used for the Breakout game is a very simple scheme and one specialized specifically for this type of game.

It should be stressed that this type of collision detection and resolution is not perfect. It calculates possible collisions only per frame and only for the positions exactly as they are at that timestep; this means that if an object would have such a velocity that it would pass over another object within a single frame, it would look like it never collided with this object. So if there are framedrops or you reach high enough velocities, this collision detection scheme will not hold.

Several of the issues that can still occur:

- If the ball goes too fast, it might skip over an object entirely within a single frame, not detecting any collisions.
- If the ball hits more than one object within a single frame, it will have detected two collisions and reverse its velocity twice; not affecting its original velocity.
- Hitting a corner of a brick could reverse the ball's velocity in the wrong direction since the distance it travels in a single frame could make the difference between VectorDirection returning a vertical or horizontal direction.

These tutorials are however aimed to teach the readers the basics of several aspects of graphics and game-development. For this reason, this collision scheme serves its purpose; its understandable and works quite well in normal scenarios. Just keep in mind that there exist better (more complicated) collision schemes that work quite well in almost all scenarios (including movable objects) like the separating axis theorem.

Thankfully, there exist large, practical and often quite efficient physics engines (with timestep-independent collision schemes) for use in your own games. If you wish to delve further into such systems or need more advanced physics and have trouble figuring out the mathematics, [Box2D](http://box2d.org/about/) is a perfect 2D physics library for implementing physics and collision detection in your applications.