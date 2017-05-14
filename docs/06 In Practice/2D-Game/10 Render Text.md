# 渲染文字

原文    | [Particles](https://learnopengl.com/#!In-Practice/2D-Game/Render-text)
-----   |  ----
作者    | JoeydeVries
翻译    | [aillieo](https://github.com/aillieo)
校对    | 暂无

In this tutorial we're adding the final enhancements to the game by adding a life system, a win condition and feedback in the form of rendered text. This tutorial heavily builds upon the earlier introduced [Text Rendering](https://learnopengl.com/#!In-Practice/Text-Rendering) tutorial so it is highly advised to first work your way through that tutorial if you haven't already.
本教程中将通过增加生命值系统、获胜条件和渲染文字形式的反馈来对游戏做最后的改进。本教程很大程度上是建立在之前的教程xx基础之上，因此如果没有看过的话，强烈建议您先一步一步学习之前的教程。



In Breakout all text rendering code is encapsulated within a class called TextRenderer that features the initialization of the FreeType library, render configuration and the actual render code. You can find the code of the TextRenderer class below:
在Breakout中，所有的文字渲染代码都封装在一个名为TextRenderer的类中，TextRenderer类中有FreeType库的初始化、渲染配置和实际渲染代码等重要组成部分。以下是TextRenderer类的代码：


- **TextRenderer**: [header](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/text_renderer.h), [code](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/text_renderer).
- **Text shaders**: [vertex](https://learnopengl.com/code_viewer.php?code=in-practice/text_rendering&type=vertex), [fragment](https://learnopengl.com/code_viewer.php?code=in-practice/text_rendering&type=fragment).

The content of the text renderer's functions is almost exactly the same as the code from the text rendering tutorial. However, the code for rendering glyphs onto the screen is slightly different:
文字渲染器中函数的内容几乎与文字渲染教程中的代码完全一样。但用于向屏幕渲染字形（glyphs）的代码稍有不同：

```
void TextRenderer::RenderText(std::string text, GLfloat x, GLfloat y, GLfloat scale,glm::vec3 color)
{
    [...]
    for (c = text.begin(); c != text.end(); c++)
    {
        GLfloat xpos = x + ch.Bearing.x * scale;
        GLfloat ypos = y + (this->Characters['H'].Bearing.y - ch.Bearing.y) * scale;

        GLfloat w = ch.Size.x * scale;
        GLfloat h = ch.Size.y * scale;
        // Update VBO for each character
        GLfloat vertices[6][4] = {
            { xpos,     ypos + h,   0.0, 1.0 },
            { xpos + w, ypos,       1.0, 0.0 },
            { xpos,     ypos,       0.0, 0.0 },

            { xpos,     ypos + h,   0.0, 1.0 },
            { xpos + w, ypos + h,   1.0, 1.0 },
            { xpos + w, ypos,       1.0, 0.0 }
        };
        [...]
    }
}

```

The reason for it being slightly different is that we use a different orthographic projection matrix than the one we've used in the text rendering tutorial. In the text rendering tutorial, all `y` values ranged from bottom to top while in the Breakout game all `y` values range from top to bottom with a `y` coordinate of `0.0` corresponding to the top edge of the screen. This means we have to slightly modify how we calculate the vertical offset.
之所以会稍有不同，是因为相比于文字渲染教程我们此处使用了一个不同的正交投影矩阵。在文字渲染教程中，所有的y值取值从底部向顶部递增，但在Breakout游戏中，y值取值从顶部到底部递增，值为0.0的y值对应屏幕顶端。这意味着我们需要稍微改变计算垂直方向偏移的方法。


Since we now render downwards from RenderText's y parameter we calculate the vertical offset as the distance a glyph is pushed downwards from the top of the glyph space. Looking back at the glyph metrics image from FreeType this is indicated by the red arrow:
由于现在我们将渲染文字y坐标参数从上向下渲染，我们将垂直偏移计算为一个字形距离字形空间顶部的距离（下推）。回顾FreeType的字形矩阵图片，此垂直偏移用红色箭头标记。


![img](https://learnopengl.com/img/in-practice/breakout/glyph_offset.png)

To calculate this vertical offset we need to get the top of the glyph space (basically the length of the black vertical arrow from the origin). Unfortunately, FreeType has no such metric for us. What we do know is that that some glyphs always touch this top edge; characters like 'H', 'T' or 'X'. So what if we calculate the length of this red vector by subtracting `bearingY` from any of these *top-reaching* glyphs by `bearingY` of the glyph in question. This way, we push the glyph down based on how far its top point differs from the top edge.
为计算垂直偏移，我们需要获取字形空间的顶部（基本上是原点发出的黑色垂直箭头的长度）。不幸的是，FreeType并不向我们提供这样的metric。我们已知的是有一些字形直接与顶部接触，如字符'H'、'T'或'X'。那么我们通过到达顶部（top-reaching）的字形的bearingY减去顶部不确定字形的bearingY来计算红色矢量的长度。使用这种方法，我们依据字形顶部的点与顶部边差异的距离来下推字形。


```
GLfloat ypos = y + (this->Characters['H'].Bearing.y - ch.Bearing.y) * scale;

```

Aside from updating the `ypos` calculation we also switched the order of the vertices a bit around to make sure all the vertices are still front facing when multiplied with the current orthographic projection matrix (as discussed in the [face culling](https://learnopengl.com/#!Advanced-OpenGL/Face-culling)tutorial).
除了更新`ypos`的计算之外，我们还调换了一些顶点的顺序，用以确保所有的顶点在与现在的正交投影矩阵相乘后仍为正方向（详见教程面剔除）。


Adding the TextRenderer to the game is easy:
向游戏中加入文字渲染器并不难：

```
TextRenderer  *Text;

void Game::Init()
{
    [...]
    Text = new TextRenderer(this->Width, this->Height);
    Text->Load("fonts/ocraext.TTF", 24);
}

```

The text renderer is initialized with a font called OCR A Extended that you can download from [here](http://fontzone.net/font-details/ocr-a-extended). If the font is not to your liking feel free to use a different font.
使用一个名为OCR A Extended的字体来初始化文字渲染器，改字体可以从[这里](http://fontzone.net/font-details/ocr-a-extended)下载。您可以使用任意不同的字体，如果不很喜欢这个字体。

Now that we have a text renderer, let's finish the gameplay mechanics.
现在我们已经有了一个文字渲染器，接下来我们来完成游戏机制。

## Player lives

Instead of immediately resetting the game as soon as the ball reaches the bottom edge, we'd like to give the player a few extra chances. We do this in the form of player lives, where the player begins with an initial number of lives (say `3`) and each time the ball touches the bottom edge the player's life total is decreased by 1. Only when the player's life total becomes `0` we reset the game. This makes it easier for the player to finish a level while also building tension.

当球碰到底部边界时，我们会给玩家额外的几次机会，而不是立即重置游戏。我们使用玩家生命值的形式来实现，玩家开始时会有初始数量的生命值（比如3），每当球碰到底部边界，玩家的生命值总数会减1。只有当玩家生命值变为`0`时才会重置游戏。这样对玩家来说完成关卡会稍容易一点，同时也会感受到难度。


We keep count of the lives of a player by adding it to the game class (initialized within the constructor to a value of `3`):
我们向game类中增加玩家的生命值以记录它（在构造函数中将其初始化为3）。


```
class Game
{
    [...]
    public:
        GLuint Lives;
}

```

We then modify the game's Update function to, instead of resetting the game, decrease the player's life total and only reset the game once the life total reached `0`:
接下来我们修改game类的update函数，不再重置游戏，而是减少玩家生命值，只有当生命值为0时重置游戏。


```
void Game::Update(GLfloat dt)
{
    [...]
    if (Ball->Position.y >= this->Height) // Did ball reach bottom edge?
    {
        --this->Lives;
        // Did the player lose all his lives? : Game over
        if (this->Lives == 0)
        {
            this->ResetLevel();
            this->State = GAME_MENU;
        }
        this->ResetPlayer();
    }
}

```

As soon as the player is game over (lives equal to `0`) we reset the level and change the game state to GAME_MENU which we'll get to later.
一旦玩家游戏结束（生命值等于0），我们会重置关卡，并将游戏状态（game state）改变为GAME_MENU，稍后会详细讲。

Don't forget to reset the player's life total as soon as we reset the game/level:
注意不要忘了在重置游戏/关卡时重置玩家生命值：

```
void Game::ResetLevel()
{
    [...]
    this->Lives = 3;
}

```

The player now has a working life total, but has no way of seeing how many lives he currently has while playing the game. That's where the text renderer comes in.
此时玩家生命值已可以运作，但玩家在游戏时却无法看到自己当前有多少生命值。这时就需要加入文字渲染器。


```
void Game::Render()
{
    if (this->State == GAME_ACTIVE)
    {
        [...]
        std::stringstream ss; ss << this->Lives;
        Text->RenderText("Lives:" + ss.str(), 5.0f, 5.0f, 1.0f);
    }
}

```

Here we convert the number of lives to a string and display it at the top-left of the screen. It'll now look a bit like this:
这里我们将生命值数量转化为一个字符串，并将其显示在屏幕左上角。看起来将会是像这样：

![img](https://learnopengl.com/img/in-practice/breakout/render_text_lives.png)

As soon as the ball touches the bottom edge, the player's life total is decreased which is instantly visible at the top-left of the screen.
一旦球接触到底部边界，玩家的生命值会减少，这会在屏幕左上角直接可见。


## Level selection

Whenever the user is in the game state GAME_MENU we'd like to give the player the control to select the level he'd like to play in. With either the 'w' or 's' key the player should be able to scroll through any of the levels we loaded. Whenever the player feels like the chosen level is indeed the level he'd like to play in he can press the enter key to switch from the game's GAME_MENU state to the GAME_ACTIVE state.
当玩家所处游戏状态为GAME_MENU时，我们希望玩家可以控制选择他想玩的关卡。玩家应该可以使用'w'或's'键在我们加载的所有关卡中滚动选择。当玩家感觉选中的是他想玩的关卡时，他可以按回车键将游戏状态从GAME_MENU切换到GAME_ACTIVE。


Allowing the player to choose a level is not too difficult. All we have to do is increase or decrease the game class's Levelvariable based on whether he pressed 'w' or 's' respectively:
允许玩家选择关卡并不难。我们要做的就是当玩家按下'w'或's'键时分别增加或减小game类中的Levelvariable值：


```
if (this->State == GAME_MENU)
{
    if (this->Keys[GLFW_KEY_ENTER])
        this->State = GAME_ACTIVE;
    if (this->Keys[GLFW_KEY_W])
        this->Level = (this->Level + 1) % 4;
    if (this->Keys[GLFW_KEY_S])
    {
        if (this->Level > 0)
            --this->Level;
        else
            this->Level = 3;
    }
}

```

We use the modulus operator (`%`) to make sure the Level variable remains within the acceptable level range (between `0` and `3`). Aside from switching levels we also want to define what we want to render when we're in the menu state. We'd like to give the player some instructions in the form of text and also display the selected level in the background.
我们使用取模运算以保证变量Level在可接受的关卡值范围内（0和3之间）。除了变换关卡之外，在菜单状态时我们还需要将其渲染出来。我们要给玩家一些文字形式的指示，并在背景中展示出选中的关卡。



```
void Game::Render()
{
    if (this->State == GAME_ACTIVE || this->State == GAME_MENU)
    {
        [...] // Game state's rendering code
    }
    if (this->State == GAME_MENU)
    {
        Text->RenderText("Press ENTER to start", 250.0f, Height / 2, 1.0f);
        Text->RenderText("Press W or S to select level", 245.0f, Height / 2 + 20.0f, 0.75f);
    }
}

```

Here we render the game whenever we're in either the GAME_ACTIVE state or the GAME_MENU state and whenever we're in the GAME_MENU state we also render two lines of text to inform the player to select a level and/or accept his choice. Note that for this to work when launching the game you do have to set the game's state as GAME_MENU by default.
这里无论游戏处在GAME_ACTIVE状态还是GAME_MENU状态，都会渲染游戏，当游戏处在GAME_MENU状态需要渲染两行文字用于告知玩家选择一个关卡或确认确认选择。注意，为此必须在启动游戏时将游戏状态默认设置为GAME_MENU。

![img](https://learnopengl.com/img/in-practice/breakout/render_text_select.png)

It looks great, but once you try to run the code you'll probably notice that as soon as you press either the 'w' or the 's' key the game rapidly scrolls through the levels making it difficult to select the level you want to play in. This happens because the game records the key press for multiple frames until we release the key. This causes the ProcessInput function to process the pressed key more than once.
看起来很棒，但当你试图运行代码你很可能会注意到，当按下'w'或's'键时，游戏会在关卡之前快速滚动，很难选中你想玩的关卡。这是因为game会在多帧记录按键直到按键松开。这将导致ProcessInput函数处理按下的键不止一次。

We can solve this issue with a little trick commonly found within GUI systems. The trick is to not only record the keys currently pressed, but also storing the keys that have been processed once, until released again. We then check (before processing) whether the key has not yet been processed, and if so, process this key after which we store this key as being processed. Once we want to process the same key again without the key having been released, we do not process the key. This probably sounds slightly confusing, but as soon as you see it in practice it (probably) starts to make sense.
我们可以使用GUI系统中常见的一个小技巧来解决这一问题。这一小技巧就是：不仅记录当前按下的键，并且存储已经被按下的键，直到再次松开。然后我们会检查（在处理之前）是否还没有被处理，如果没有被处理的话，处理该按键并将其存储为正在被处理。一旦我们要在未松开时再次处理相同的按键，我们将不会处理该按键。这听起来让人稍微迷惑，但当你在实际应用中见到它，（很可能）就会明白它的意义。

First we have to create another array of bool values to indicate which keys have been processed. We define this within the game class:
首先我们需要创建另一个布尔数组用来表示处理过的按键。我们在game类定义如下：


```
class Game
{
    [...]
    public:
        GLboolean KeysProcessed[1024];
}

```

We then set the relevant key(s) to `true` as soon as they're processed and make sure to only process the key if it wasn't processed before (until released):
当相对应的按键被处理时，我们将其设置为true，以确保按键只在之前没有被处理过（直到松开）时将其处理。

```
void Game::ProcessInput(GLfloat dt)
{
    if (this->State == GAME_MENU)
    {
        if (this->Keys[GLFW_KEY_ENTER] && !this->KeysProcessed[GLFW_KEY_ENTER])
        {
            this->State = GAME_ACTIVE;
            this->KeysProcessed[GLFW_KEY_ENTER] = GL_TRUE;
        }
        if (this->Keys[GLFW_KEY_W] && !this->KeysProcessed[GLFW_KEY_W])
        {
            this->Level = (this->Level + 1) % 4;
            this->KeysProcessed[GLFW_KEY_W] = GL_TRUE;
        }
        if (this->Keys[GLFW_KEY_S] && !this->KeysProcessed[GLFW_KEY_S])
        {
            if (this->Level > 0)
                --this->Level;
            else
                this->Level = 3;
            this->KeysProcessed[GLFW_KEY_S] = GL_TRUE;
        }
    }
    [...]
}

```

Now as soon as the key's value in the KeysProcessed array has not yet been set, we process the key and set its value to `true`. Next time we reach the `if` condition of the same key, it will have been processed so we'll pretend we never pressed the button until it's released again.
现在，当KeysProcessed数组中按键的值未被设置时，我们会处理按键并将其值设为true。下一次当到达同一按键的if条件时，它已经被处理过了所以我们会假装并没有按下此键，直到它被松开。

Within GLFW's key callback function we then need to reset the key's processed value as soon as its released so we can process it again the next time it's pressed:
之后，我们需要在松开按键时通过GLFW的按键回调函数，重置按键处理后的值，以便于下次再处理：

```
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode)
{
    [...]
    if (key >= 0 && key < 1024)
    {
        if (action == GLFW_PRESS)
            Breakout.Keys[key] = GL_TRUE;
        else if (action == GLFW_RELEASE)
        {
            Breakout.Keys[key] = GL_FALSE;
            Breakout.KeysProcessed[key] = GL_FALSE;
        }
    }
}

```

Launching the game gives us a neat level select screen that now precisely selects a single level per key press no matter how long we press he key.

启动游戏会展示一个整洁的关卡选择界面，现在可以每次按键清晰地选择一个关卡，无论按键被按下多久。


## Winning

Currently the player is able to select levels, play the game and fail in doing so to lose. It is kind of unfortunate if the player finds out after destroying all the bricks he cannot in any way win the game. So let's fix that.
现在玩家可以选择关卡、玩游戏和游戏失败。有些不幸的是玩家在消除了所有的砖块之后会发现无法获得游戏胜利。现在来修复此问题。


The player wins when all of the non-solid blocks have been destroyed. We already created a function to check for this condition with the GameLevel class:
在所有实体砖块被消除之后玩家会取得胜利。我们已经在GameLevel类创建了一个函数用于检查这一条件：


```
GLboolean GameLevel::IsCompleted()
{
    for (GameObject &tile : this->Bricks)
        if (!tile.IsSolid && !tile.Destroyed)
            return GL_FALSE;
    return GL_TRUE;
}

```

We check all bricks in the game level and if a single non-solid brick is not destroyed we return `false`. All we have to do is check for this condition in the game's Update function and as soon as it returns `true` we change the game state to GAME_WIN:
我们会检查游戏关卡所有的砖块，如果有一个非实体砖块未被消除则返回false。我们所要做的就是在Update函数中检查此条件，一旦返回true，我们就将游戏状态改变为GAME_WIN：


```
void Game::Update(GLfloat dt)
{
    [...]
    if (this->State == GAME_ACTIVE && this->Levels[this->Level].IsCompleted())
    {
        this->ResetLevel();
        this->ResetPlayer();
        Effects->Chaos = GL_TRUE;
        this->State = GAME_WIN;
    }
}

```

Whenever the level is completed while the game is active we reset the game and display a small victory message in the GAME_WIN state. For fun we'll enable the chaos effect while in the GAME_WIN screen. In the Render function we'll congratulate the player and ask him to either restart or quit the game:

在游戏激活状态，当关卡完成时，我们会重置游戏并且在GAME_WIN状态展示一条小的胜利的消息。为了增加趣味性我们会在GAME_WIN界面启用混沌效果（chaos effect）。在渲染函数中我们会祝贺玩家并询问其重新开始还是退出游戏。



```
void Game::Render()
{
    [...]
    if (this->State == GAME_WIN)
    {
        Text->RenderText(
            "You WON!!!", 320.0, Height / 2 - 20.0, 1.0, glm::vec3(0.0, 1.0, 0.0)
        );
        Text->RenderText(
            "Press ENTER to retry or ESC to quit", 130.0, Height / 2, 1.0, glm::vec3(1.0, 1.0, 0.0)
        );
    }
}

```

Then we of course have to actually catch the mentioned keys:
之后我们当然也要处理之前提到的按键：

```
void Game::ProcessInput(GLfloat dt)
{
    [...]
    if (this->State == GAME_WIN)
    {
        if (this->Keys[GLFW_KEY_ENTER])
        {
            this->KeysProcessed[GLFW_KEY_ENTER] = GL_TRUE;
            Effects->Chaos = GL_FALSE;
            this->State = GAME_MENU;
        }
    }
}

```

If you can then actually manage to win the game you'd get the following image:
之后如果你真的可以赢得游戏，你将会看到以下图片：

![img](https://learnopengl.com/img/in-practice/breakout/render_text_win.png)

And that is it! The final piece of the puzzle of the Breakout game we've been working on. Try it out, customize it to your liking and show it to all your family and friends!
就是这样！这是游戏Breakout我们要处理的最后一块拼图。尝试按照自己的意愿自定义并把它展示给你的家人和朋友！


You can find the final version of the game's code below:
以下是最终版的游戏代码：

- **Game**: [header](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/game.h), [code](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/game).

## Want to help?

Enjoyed the tutorial? Consider becoming a [patron](https://www.patreon.com/learnopengl) of LearnOpenGL.
喜欢这个教程吗？来[赞助](https://www.patreon.com/learnopengl)LearnOpenGL吧。

Your support helps me create new and better tutorials, improve existing content and enables me to improve the website wherever I can.
您的支持会帮助我创作新的更好的教程，改进现有内容，帮助我改进网站的任何地方。


