# 混合

原文     | [Blending](http://learnopengl.com/#!Advanced-OpenGL/Blending)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)


在OpenGL中，物体透明技术通常被叫做**混合(Blending)**。透明是物体（或物体的一部分）非纯色而是混合色，这种颜色来自于不同浓度的自身颜色和它后面的物体颜色。一个有色玻璃窗就是一种透明物体，玻璃有自身的颜色，但是最终的颜色包含了所有玻璃后面的颜色。这也正是混合这名称的出处，因为我们将多种（来自于不同物体）颜色混合为一个颜色，透明使得我们可以看穿物体。

![](http://learnopengl.com/img/advanced/blending_transparency.png)

透明物体可以是完全透明（它使颜色完全穿透）或者半透明的（它使颜色穿透的同时也显示自身颜色）。一个物体的透明度，被定义为它的颜色的alpha值。alpha颜色值是一个颜色向量的第四个元素，你可能已经看到很多了。在这个教程前，我们一直把这个元素设置为1.0，这样物体的透明度就是0.0，同样的，当alpha值是0.0时就表示物体是完全透明的，alpha值为0.5时表示物体的颜色由50%的自身的颜色和50%的后面的颜色组成。

我们之前所使用的纹理都是由3个颜色元素组成的：红、绿、蓝，但是有些纹理同样有一个内嵌的aloha通道，它为每个纹理像素(Texel)包含着一个alpha值。这个alpha值告诉我们纹理的哪个部分有透明度，以及这个透明度有多少。例如，下面的窗子纹理的玻璃部分的alpha值为0.25(它的颜色是完全红色，但是由于它有75的透明度，它会很大程度上反映出网站的背景色，看起来就不那么红了)，角落部分alpha是0.0。

![](http://learnopengl.com/img/advanced/blending_transparent_window.png)

我们很快就会把这个窗子纹理加到场景中，但是首先，我们将讨论一点简单的技术来实现纹理的半透明，也就是完全透明和完全不透明。

## 忽略片段

有些图像并不关心半透明度，但也想基于纹理的颜色值显示一部分。例如，创建像草这种物体你不需要花费很大力气，通常把一个草的纹理贴到2D四边形上，然后把这个四边形放置到你的场景中。可是，草并不是像2D四边形这样的形状，而只需要显示草纹理的一部分而忽略其他部分。

下面的纹理正是这样的纹理，它既有完全不透明的部分（alpha值为1.0）也有完全透明的部分（alpha值为0.0），而没有半透明的部分。你可以看到没有草的部分，图片显示了网站的背景色，而不是它自身的那部分颜色。

![](http://learnopengl.com/img/textures/grass.png)

所以，当向场景中添加像这样的纹理时，我们不希望看到一个方块图像，而是只显示实际的纹理像素，剩下的部分可以被看穿。我们要忽略(丢弃)纹理透明部分的像素，不必将这些片段储存到颜色缓冲中。在此之前，我们还要学一下如何加载一个带有透明像素的纹理。

加载带有alpha值的纹理我们需要告诉SOIL，去加载RGBA元素图像，而不再是RGB元素的。SOIL能以RGBA的方式加载大多数没有alpha值的纹理，它会将这些像素的alpha值设为了1.0。

```c++
unsigned char * image = SOIL_load_image(path, &width, &height, 0, SOIL_LOAD_RGBA);
```

不要忘记还要改变OpenGL生成的纹理：

```c++
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image);
```

保证你在片段着色器中获取了纹理的所有4个颜色元素，而不仅仅是RGB元素：

```c++
void main()
{
    // color = vec4(vec3(texture(texture1, TexCoords)), 1.0);
    color = texture(texture1, TexCoords);
}
```

现在我们知道了如何加载透明纹理，是时候试试在深度测试教程里那个场景中添加几根草了。

我们创建一个`std::vector`，并向里面添加几个`glm::vec3`变量，来表示草的位置：

```c++
vector<glm::vec3> vegetation;
vegetation.push_back(glm::vec3(-1.5f,  0.0f, -0.48f));
vegetation.push_back(glm::vec3( 1.5f,  0.0f,  0.51f));
vegetation.push_back(glm::vec3( 0.0f,  0.0f,  0.7f));
vegetation.push_back(glm::vec3(-0.3f,  0.0f, -2.3f));
vegetation.push_back(glm::vec3( 0.5f,  0.0f, -0.6f));
```

一个单独的四边形被贴上草的纹理，这并不能完美的表现出真实的草，但是比起加载复杂的模型还是要高效很多，利用一些小技巧，比如在同一个地方添加多个不同朝向的草，还是能获得比较好的效果的。

由于草纹理被添加到四边形物体上，我们需要再次创建另一个VAO，向里面填充VBO，以及设置合理的顶点属性指针。在我们绘制完地面和两个立方体后，我们就来绘制草叶：

```c++
glBindVertexArray(vegetationVAO);
glBindTexture(GL_TEXTURE_2D, grassTexture);  
for(GLuint i = 0; i < vegetation.size(); i++)
{
    model = glm::mat4();
    model = glm::translate(model, vegetation[i]);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glDrawArrays(GL_TRIANGLES, 0, 6);
}  
glBindVertexArray(0);
```

运行程序你将看到：
![](http://learnopengl.com/img/advanced/blending_no_discard.png)

出现这种情况是因为OpenGL默认是不知道如何处理alpha值的，不知道何时忽略(丢弃)它们。我们不得不手动做这件事。幸运的是这很简单，感谢着色器，GLSL为我们提供了discard命令，它保证了片段不会被进一步处理，这样就不会进入颜色缓冲。有了这个命令我们就可以在片段着色器中检查一个片段是否有在一定的阈限下的alpha值，如果有，那么丢弃这个片段，就好像它不存在一样：

```c++
#version 330 core
in vec2 TexCoords;

out vec4 color;

uniform sampler2D texture1;

void main()
{
    vec4 texColor = texture(texture1, TexCoords);
    if(texColor.a < 0.1)
        discard;
    color = texColor;
}
```

在这儿我们检查被采样纹理颜色包含着一个低于0.1这个阈限的alpha值，如果有，就丢弃这个片段。这个片段着色器能够保证我们只渲染哪些不是完全透明的片段。现在我们来看看效果：

![](http://learnopengl.com/img/advanced/blending_discard.png)

!!! Important

    需要注意的是，当采样纹理边缘的时候，OpenGL在边界值和下一个重复的纹理的值之间进行插值（因为我们把它的放置方式设置成了GL_REPEAT）。这样就行了，但是由于我们使用的是透明值，纹理图片的上部获得了它的透明值是与底边的纯色值进行插值的。结果就是一个有点半透明的边，你可以从我们的纹理四边形的四周看到。为了防止它的出现，当你使用alpha纹理的时候要把纹理环绕方式设置为`GL_CLAMP_TO_EDGE`：

    `glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);`

    `glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);`

你可以[在这里得到源码](http://learnopengl.com/code_viewer.php?code=advanced/blending_discard)。


## 混合

上述丢弃片段的方式，不能使我们获得渲染半透明图像，我们要么渲染出像素，要么完全地丢弃它。为了渲染出不同的透明度级别，我们需要开启**混合**(Blending)。像大多数OpenGL的功能一样，我们可以开启`GL_BLEND`来启用**混合(Blending)**功能：

```c++
glEnable(GL_BLEND);
```

开启混合后，我们还需要告诉OpenGL它该如何混合。

OpenGL以下面的方程进行混合：

$$
\begin{equation}\bar{C}_{result} = \bar{\color{green}C}_{source} * \color{green}F_{source} + \bar{\color{red}C}_{destination} * \color{red}F_{destination}\end{equation}
$$

* \(\bar{\color{green}C}_{source}\)：源颜色向量。这是来自纹理的本来的颜色向量。
* \(\bar{\color{red}C}_{destination}\)：目标颜色向量。这是储存在颜色缓冲中当前位置的颜色向量。
* \(\color{green}F_{source}\)：源因子。设置了对源颜色的alpha值影响。
* \(\color{red}F_{destination}\)：目标因子。设置了对目标颜色的alpha影响。

片段着色器运行完成并且所有的测试都通过以后，混合方程才能自由执行片段的颜色输出，当前它在颜色缓冲中（前面片段的颜色在当前片段之前储存）。源和目标颜色会自动被OpenGL设置，而源和目标因子可以让我们自由设置。我们来看一个简单的例子：

![](http://learnopengl.com/img/advanced/blending_equation.png)

我们有两个方块，我们希望在红色方块上绘制绿色方块。红色方块会成为目标颜色（它会先进入颜色缓冲），我们将在红色方块上绘制绿色方块。

那么问题来了：我们怎样来设置因子呢？我们起码要把绿色方块乘以它的alpha值，所以我们打算把\(F_{src}\)设置为源颜色向量的alpha值：0.6。接着，让目标方块的浓度等于剩下的alpha值。如果最终的颜色中绿色方块的浓度为60%，我们就把红色的浓度设为40%（1.0 – 0.6）。所以我们把\(F_{destination}\)设置为1减去源颜色向量的alpha值。方程将变成：

$$
\begin{equation}\bar{C}_{result} = \begin{pmatrix} \color{red}{0.0} \\ \color{green}{1.0} \\ \color{blue}{0.0} \\ \color{purple}{0.6} \end{pmatrix} * \color{green}{0.6} + \begin{pmatrix} \color{red}{1.0} \\ \color{green}{0.0} \\ \color{blue}{0.0} \\ \color{purple}{1.0} \end{pmatrix} * \color{red}{(1 - 0.6)} \end{equation}
$$

最终方块结合部分包含了60%的绿色和40%的红色，得到一种脏兮兮的颜色：

![](http://learnopengl.com/img/advanced/blending_equation_mixed.png)

最后的颜色被储存到颜色缓冲中，取代先前的颜色。

这个方案不错，但我们怎样告诉OpenGL来使用这样的因子呢？恰好有一个叫做`glBlendFunc`的函数。

`void glBlendFunc(GLenum sfactor, GLenum dfactor)`接收两个参数，来设置源（source）和目标（destination）因子。OpenGL为我们定义了很多选项，我们把最常用的列在下面。注意，颜色常数向量\(\bar{\color{blue}C}_{constant}\)可以用`glBlendColor`函数分开来设置。


选项 |	值
---|---
GL_ZERO  |	\(0\)
GL_ONE	 |  \(1\)
GL_SRC_COLOR |	源颜色向量\(\bar{\color{green}C}_{source}\)
GL_ONE_MINUS_SRC_COLOR | \(1 - \bar{\color{green}C}_{source}\)
GL_DST_COLOR |	 目标颜色向量\(\bar{\color{red}C}_{destination}\)
GL_ONE_MINUS_DST_COLOR | \(1 - \bar{\color{red}C}_{destination}\)
GL_SRC_ALPHA |	\(\bar{\color{green}C}_{source}\)的\(alpha\)值
GL_ONE_MINUS_SRC_ALPHA | \(1 -\) \(\bar{\color{green}C}_{source}\)的\(alpha\)值
GL_DST_ALPHA |	\(\bar{\color{red}C}_{destination}\)的\(alpha\)值
GL_ONE_MINUS_DST_ALPHA | \(1 -\) \(\bar{\color{red}C}_{destination}\)的\(alpha\)值
GL_CONSTANT_COLOR	   | 常颜色向量\(\bar{\color{blue}C}_{constant}\)
GL_ONE_MINUS_CONSTANT_COLOR |	\(1 - \bar{\color{blue}C}_{constant}\)
GL_CONSTANT_ALPHA	   | \(\bar{\color{blue}C}_{constant}\)的\(alpha\)值
GL_ONE_MINUS_CONSTANT_ALPHA |	\(1 -\) \(\bar{\color{blue}C}_{constant}\)的\(alpha\)值

为从两个方块获得混合结果，我们打算把源颜色的\(alpha\)给源因子，\(1 - alpha\)给目标因子。调整到`glBlendFunc`之后就像这样：

```c++
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
```

也可以为RGB和alpha通道各自设置不同的选项，使用`glBlendFuncSeperate`：

```c++
glBlendFuncSeperate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,GL_ONE, GL_ZERO);
```

这个方程就像我们之前设置的那样，设置了RGB元素，但是只让最终的alpha元素被源alpha值影响到。

OpenGL给了我们更多的自由，我们可以改变方程源和目标部分的操作符。现在，源和目标元素已经相加了。如果我们愿意的话，我们还可以把它们相减。

`void glBlendEquation(GLenum mode)`允许我们设置这个操作，有3种可行的选项：

* GL_FUNC_ADD：默认的，彼此元素相加：\(\bar{C}_{result} = \color{green}{Src} + \color{red}{Dst}\)
* GL_FUNC_SUBTRACT：彼此元素相减： \(\bar{C}_{result} = \color{green}{Src} - \color{red}{Dst}\)
* GL_FUNC_REVERSE_SUBTRACT：彼此元素相减，但顺序相反：\(\bar{C}_{result} = \color{red}{Dst} - \color{green}{Src}\).

通常我们可以简单地省略`glBlendEquation`因为GL_FUNC_ADD在大多数时候就是我们想要的，但是如果你如果你真想尝试努力打破主流常规，其他的方程或许符合你的要求。

## 渲染半透明纹理

现在我们知道OpenGL如何处理混合，是时候把我们的知识运用起来了，我们来添加几个半透明窗子。我们会使用本教程开始时用的那个场景，但是不再渲染草纹理，取而代之的是来自教程开始处半透明窗子纹理。

首先，初始化时我们需要开启混合，设置合适和混合方程：

```c++
glEnable(GL_BLEND);
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
```

由于我们开启了混合，就不需要丢弃片段了，所以我们把片段着色器设置为原来的那个版本：

```c++
#version 330 core
in vec2 TexCoords;

out vec4 color;

uniform sampler2D texture1;

void main()
{
    color = texture(texture1, TexCoords);
}
```

这一次（无论OpenGL什么时候去渲染一个片段），它都根据alpha值，把当前片段的颜色和颜色缓冲中的颜色进行混合。因为窗子的玻璃部分的纹理是半透明的，我们应该可以透过玻璃看到整个场景。

![](http://learnopengl.com/img/advanced/blending_incorrect_order.png)

如果你仔细看看，就会注意到有些不对劲。前面的窗子透明部分阻塞了后面的。为什么会这样？

原因是深度测试在与混合的一同工作时出现了点状况。当写入深度缓冲的时候，深度测试不关心片段是否有透明度，所以透明部分被写入深度缓冲，就和其他值没什么区别。结果是整个四边形的窗子被检查时都忽视了透明度。即便透明部分应该显示出后面的窗子，深度缓冲还是丢弃了它们。

所以我们不能简简单单地去渲染窗子，我们期待着深度缓冲为我们解决这所有问题；这也正是混合之处代码不怎么好看的原因。为保证前面窗子显示了它后面的窗子，我们必须首先绘制后面的窗子。这意味着我们必须手工调整窗子的顺序，从远到近地逐个渲染。

!!! Important

    对于全透明物体，比如草叶，我们选择简单的丢弃透明像素而不是混合，这样就减少了令我们头疼的问题（没有深度测试问题）。

## 别打乱顺序

要让混合在多物体上有效，我们必须先绘制最远的物体，最后绘制最近的物体。普通的无混合物体仍然可以使用深度缓冲正常绘制，所以不必给它们排序。我们一定要保证它们在透明物体前绘制好。当无透明度物体和透明物体一起绘制的时候，通常要遵循以下原则：

先绘制所有不透明物体。
为所有透明物体排序。
按顺序绘制透明物体。
一种排序透明物体的方式是，获取一个物体到观察者透视图的距离。这可以通过获取摄像机的位置向量和物体的位置向量来得到。接着我们就可以把它和相应的位置向量一起储存到一个map数据结构（STL库）中。map会自动基于它的键排序它的值，所以当我们把它们的距离作为键添加到所有位置中后，它们就自动按照距离值排序了：

```c++
std::map<float, glm::vec3> sorted;
for (GLuint i = 0; i < windows.size(); i++) // windows contains all window positions
{
    GLfloat distance = glm::length(camera.Position - windows[i]);
    sorted[distance] = windows[i];
}
```

最后产生了一个容器对象，基于它们距离从低到高储存了每个窗子的位置。

随后当渲染的时候，我们逆序获取到每个map的值（从远到近），然后以正确的绘制相应的窗子：

```c++
for(std::map<float,glm::vec3>::reverse_iterator it = sorted.rbegin(); it != sorted.rend(); ++it)
{
    model = glm::mat4();
    model = glm::translate(model, it->second);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glDrawArrays(GL_TRIANGLES, 0, 6);
}
```

我们从map得来一个逆序的迭代器，迭代出每个逆序的条目，然后把每个窗子的四边形平移到相应的位置。这个相对简单的方法对透明物体进行了排序，修正了前面的问题，现在场景看起来像这样：

![](http://learnopengl.com/img/advanced/blending_sorted.png)

你可以[从这里得到完整的带有排序的源码](http://learnopengl.com/code_viewer.php?code=advanced/blending_sorted)。

虽然这个按照它们的距离对物体进行排序的方法在这个特定的场景中能够良好工作，但它不能进行旋转、缩放或者进行其他的变换，奇怪形状的物体需要一种不同的方式，而不能简单的使用位置向量。

在场景中排序物体是个有难度的技术，它很大程度上取决于你场景的类型，更不必说会耗费额外的处理能力了。完美地渲染带有透明和不透明的物体的场景并不那么容易。有更高级的技术例如次序无关透明度（order independent transparency），但是这超出了本教程的范围。现在你不得不采用普通的混合你的物体，但是如果你小心谨慎，并知道这个局限，你仍可以得到颇为合适的混合实现。
