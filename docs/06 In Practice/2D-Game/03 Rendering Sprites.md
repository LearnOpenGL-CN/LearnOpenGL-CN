# 渲染精灵

原文   | [Rendering Sprites](http://learnopengl.com/#!In-Practice/2D-Game/Rendering-Sprites)
   ---|---
作者   | JoeyDeVires
翻译   | [ZMANT](https://github.com/Itanq)
校队   | 暂无

## 渲染精灵

为了给我们当前这个黑漆漆的游戏世界带来一点生机，我们将会渲染一些精灵(Sprite)来填补一些空虚。精灵有很多种定义，但主要是指一个2D图片，它通常是和一些属性数据一起使用，比如用一些数据来表示它在世界坐标下的位置，一个旋转的角度以及一个表示二维空间的大小的变量。在2D游戏中，我们主要使用精灵来渲染图片/纹理对象。

就像前面那些教程里做的那样，我们可以把顶点数据传到GPU并且手动的通过一些操作来创建一些2D形状。然而，在一个大型应用中，就像我们正在做的这个，我们还是宁愿在渲染2D形状上做一些抽象。如果我们手动的去定义并转换每一个对象，那就相当的凌乱了。

在这里，我们将会定义一个用最少的代码去渲染大量的精灵的渲染类。这样，我们就可以从像散沙一样的OpenGL渲染代码中摘要出游戏代码，这是在一个大型应用中常用的做法。尽管我们首先要做的是设置一个合适的投影矩阵。

## 2D投影矩阵

从这个[坐标系统](../../01 Getting started/08 Coordinate Systems.md)教程我们明白了投影矩阵的作用是把视图空间坐标转化为标准化设备坐标。通过生成合适的投影矩阵，我们就可以在不同的坐标系下计算，这可能比把所有的坐标指定为标准化设备坐标（再计算）要更容易处理。

我们并不需要在坐标系执行任何的透视应用，因为这个游戏完全是在二维平面，所以一个正交投影矩阵就可以很好的工作了。因为正交投影矩阵几乎是直接把整个坐标变换到裁切空间，我们可以定义如下的矩阵来把世界坐标指定为屏幕坐标：

```c++
glm::mat4 projection = glm::ortho(0.0f,800.0f,600.0f,0.0f,-1.0f,1.0f);
```

前面的四个参数依次指定了投影椎体左、右、下、上边界。这个投影矩阵把所有在`0`到`800`之间的`x`坐标变换到`-1`到`1`之间以及把所有在`0`到`600`之间的`y`坐标变换到`-1`到`1`之间。这里我们指定了视椎体上部的`y`坐标值为`0`，同时其下部的`y`坐标值为`600`。结果就是这个场景的左上角坐标为`(0,0)`，右下角坐标为`(800,600)`，就像屏幕坐标那样。视图空间坐标直接对应像素坐标。

![](../../img/06/Breakout/03/projection.png)

这允许我们指定每个坐标都等于它们在屏幕上最终的像素坐标，这在2D游戏里相当直观。

## 渲染精灵

渲染一个实际的精灵不因太复杂化。我们创建一个纹理四边形，并且在使用了前面预先定义的正交投影矩阵（变换到标准化设备坐标）之后我们可以使用模型矩阵来变换它。

!!! important

	由于`Breakout`游戏是一个静态游戏，这里不需要视图/摄像机矩阵，我们可以直接使用投影矩阵把世界空间坐标变换到裁切空间坐标

为了变换精灵我们使用了下面的顶点着色器：

```c++
#version 330 core
layout (location = 0) in vec4 vertex; // <vec2 position, vec2 texCoords>

out vec2 TexCoords;

uniform mat4 model;
uniform mat4 projection;

void main()
{
    TexCoords = vertex.zw;
    gl_Position = projection * model * vec4(vertex.xy, 0.0, 1.0);
}
```

注意，我们使用了一个单一的`vec4`变量来存储了位置和纹理坐标数据。因为位置和纹理坐标数据都只包含了两个浮点型数据，所以我们可以把他们组合在一起作为一个单一的顶点属性。

像素着色器相对比较简单。我们设置了一个纹理和颜色向量，她们两个都会对像素最后的颜色产生影响。同样也设置了一个`uniform`颜色向量，我们就可以很容易的在游戏代码里面改变精灵的颜色。

```c++
#version 330 core
in vec2 TexCoords;
out vec4 color;

uniform sampler2D image;
uniform vec3 spriteColor;

void main()
{    
    color = vec4(spriteColor, 1.0) * texture(image, TexCoords);
}
```

为了让渲染精灵的代码更加有条理，我们定义了一个`SpriteRenderer`类，只需要一个单一的函数就可以渲染精灵，它的定义如下：

```c++
class SpriteRenderer
{
    public:
        SpriteRenderer(Shader &shader);
        ~SpriteRenderer();

        void DrawSprite(Texture2D &texture, glm::vec2 position, 
            glm::vec2 size = glm::vec2(10, 10), GLfloat rotate = 0.0f, 
            glm::vec3 color = glm::vec3(1.0f));
    private:
        Shader shader; 
        GLuint quadVAO;

        void initRenderData();
};
```

`SpriteRenderer`类封装了一个着色器对象，一个顶点数组对象以及一个渲染和初始化函数。它的构造函数接受一个着色器对象用于后面的渲染。

### 初始化

首先，让我们探究一下负责配置`quadVAO`的`initRenderData`h函数：

```c++
void SpriteRenderer::initRenderData()
{
    // Configure VAO/VBO
    GLuint VBO;
    GLfloat vertices[] = { 
        // Pos      // Tex
        0.0f, 1.0f, 0.0f, 1.0f,
        1.0f, 0.0f, 1.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 0.0f, 
    
        0.0f, 1.0f, 0.0f, 1.0f,
        1.0f, 1.0f, 1.0f, 1.0f,
        1.0f, 0.0f, 1.0f, 0.0f
    };

    glGenVertexArrays(1, &this->quadVAO);
    glGenBuffers(1, &VBO);
    
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    glBindVertexArray(this->quadVAO);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), (GLvoid*)0);
    glBindBuffer(GL_ARRAY_BUFFER, 0);  
    glBindVertexArray(0);
}
```

在这我们首先定义了一组以四边形的左上角为`(0,0)`的顶点坐标。这意味着当我们在四边形上申请一个移动或伸缩变换的时候，四边形的左上角会被变换。这在2D图形或GUI这类元素的位置是相对于元素左上角的系统而言很常见。

下面我们简单的向`GPU`传递了顶点数据并且配置了顶点属性，这里的情况是只有一个单一的顶点属性。我们仅仅需要为每一个精灵渲染器定义一个单一的`VAO`，因为他们的顶点数据都是一样的。

### 渲染

渲染精灵并不是太难；我们使用精灵渲染器的着色器对象，配置一个模型矩阵并且设置相关的`uniform`变量。这里最重要的就是变换的顺序：

```c++
void SpriteRenderer::DrawSprite(Texture2D &texture, glm::vec2 position, 
  glm::vec2 size, GLfloat rotate, glm::vec3 color)
{
    // Prepare transformations
    this->shader.Use();
    glm::mat4 model;
    model = glm::translate(model, glm::vec3(position, 0.0f));  

    model = glm::translate(model, glm::vec3(0.5f * size.x, 0.5f * size.y, 0.0f)); 
    model = glm::rotate(model, rotate, glm::vec3(0.0f, 0.0f, 1.0f)); 
    model = glm::translate(model, glm::vec3(-0.5f * size.x, -0.5f * size.y, 0.0f));

    model = glm::scale(model, glm::vec3(size, 1.0f)); 
  
    this->shader.SetMatrix4("model", model);
    this->shader.SetVector3f("spriteColor", color);
  
    glActiveTexture(GL_TEXTURE0);
    texture.Bind();

    glBindVertexArray(this->quadVAO);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glBindVertexArray(0);
}
```

当试图在一个场景中用旋转矩阵和伸缩矩阵放置一个对象的时候，建议首先做伸缩变换，然后旋转最后是移动变换。因为矩阵乘法是从右向左执行的，所以我们变换的矩阵顺序是相反的：移动，旋转，缩放。

旋转变换可能看起来稍微有点让人望而却步。我们从[变换](../../01 Getting started/07 Transformations/)教程里面知道旋转总是围绕原点`(0,0)`转动的。因为我们指定了四边形的左上角为`(0,0)`，所有的旋转都是围绕`(0,0)`的。主要是这个旋转的原点是四边形的左上角，这样就会造成不太友好的旋转效果。我们想要做的就是把旋转的点移到四边形的中心，这样旋转就是围绕四边形中心而不是左上角了。我们通过在旋转之前把旋转点移动到四边形中心解决了这个问题。

![](../../img/06/Breakout/03/rotation-origin.png)

因为我们首先缩放了这个四边形，我们不得不在把原点变换到精灵中心的时候输入一个`size`变量(这就是我们乘了精灵的`size`向量)。一旦应用了旋转变换之后，我们就需要做上一次变换的逆变换。

把所有变换组合起来我们就可以以我们喜欢的方式移动、缩放并且旋转每一个精灵了。在下面你可以找到完整的精灵渲染器的源代码：

>* SpriteRenderer: [header](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/sprite_renderer.h),[code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/sprite_renderer)

## 你好，精灵

使用`SpriteRenderer`类我们有了把实际图片渲染到屏幕的能力！让我们来在游戏代码里面初始化一个精灵并且加载一个我们最喜爱的[纹理](../../img/06/Breakout/03/awesomeface.png)：

```c++
SpriteRenderer  *Renderer;
  
void Game::Init()
{
    // Load shaders
    ResourceManager::LoadShader("shaders/sprite.vs", "shaders/sprite.frag", nullptr, "sprite");
    // Configure shaders
    glm::mat4 projection = glm::ortho(0.0f, static_cast<GLfloat>(this->Width), 
        static_cast<GLfloat>(this->Height), 0.0f, -1.0f, 1.0f);
    ResourceManager::GetShader("sprite").Use().SetInteger("image", 0);
    ResourceManager::GetShader("sprite").SetMatrix4("projection", projection);
    // Set render-specific controls
    Renderer = new SpriteRenderer(ResourceManager::GetShader("sprite"));
    // Load textures
    ResourceManager::LoadTexture("textures/awesomeface.png", GL_TRUE, "face");
}
```

然后在渲染函数里面我们渲染一下我们的吉祥物来看看是否一切都按正确的方式工作了：

```c++
void Game::Render()
{
    Renderer->DrawSprite(ResourceManager::GetTexture("face"), 
        glm::vec2(200, 200), glm::vec2(300, 400), 45.0f, glm::vec3(0.0f, 1.0f, 0.0f));
}
```

这里我们把精灵放置在靠近屏幕中心的位置，它的高度稍微有点大于宽度。我们同样也把它旋转了`45.0f`度并且给了一个绿色。注意，我们设定的精灵的位置是精灵四边形左上角的位置。

如果你一切都做对了你应该可以看到下面的输出：

![](../../img/06/Breakout/03/rendering-sprites.png)

你可以在[这里](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_rendering-sprites)找到更新后的游戏源代码。

目前我们的渲染系统正确工作了，我们在下一个教程里设置了游戏的等级，它在那里将会有更好的用处。