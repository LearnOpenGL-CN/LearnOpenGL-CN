# 帧缓冲

原文     | [Framebuffers](http://learnopengl.com/#!Advanced-OpenGL/Framebuffers)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)

到目前为止，我们使用了几种不同类型的屏幕缓冲：用于写入颜色值的颜色缓冲，用于写入深度信息的深度缓冲，以及允许我们基于一些条件丢弃指定片段的模板缓冲。把这几种缓冲结合起来叫做帧缓冲(Framebuffer)，它被储存于内存中。OpenGL给了我们自己定义帧缓冲的自由，我们可以选择性的定义自己的颜色缓冲、深度和模板缓冲。

我们目前所做的渲染操作都是是在默认的帧缓冲之上进行的。当你创建了你的窗口的时候默认帧缓冲就被创建和配置好了（GLFW为我们做了这件事）。通过创建我们自己的帧缓冲我们能够获得一种额外的渲染方式。

你也许不能立刻理解应用程序的帧缓冲的含义，通过帧缓冲可以将你的场景渲染到一个不同的帧缓冲中，可以使我们能够在场景中创建镜子这样的效果，或者做出一些炫酷的特效。首先我们会讨论它们是如何工作的，然后我们将利用帧缓冲来实现一些炫酷的效果。

## 创建一个帧缓冲

就像OpenGL中其他对象一样，我们可以使用一个叫做`glGenFramebuffers`的函数来创建一个帧缓冲对象（简称FBO）：

```c++
GLuint fbo;
glGenFramebuffers(1, &fbo);
```

这种对象的创建和使用的方式我们已经见过不少了，因此它们的使用方式也和之前我们见过的其他对象的使用方式相似。首先我们要创建一个帧缓冲对象，把它绑定到当前帧缓冲，做一些操作，然后解绑帧缓冲。我们使用`glBindFramebuffer`来绑定帧缓冲：

```c++
glBindFramebuffer(GL_FRAMEBUFFER, fbo);
```

绑定到`GL_FRAMEBUFFER`目标后，接下来所有的读、写帧缓冲的操作都会影响到当前绑定的帧缓冲。也可以把帧缓冲分开绑定到读或写目标上，分别使用`GL_READ_FRAMEBUFFER`或`GL_DRAW_FRAMEBUFFER`来做这件事。如果绑定到了`GL_READ_FRAMEBUFFER`，就能执行所有读取操作，像`glReadPixels`这样的函数使用了；绑定到`GL_DRAW_FRAMEBUFFER`上，就允许进行渲染、清空和其他的写入操作。大多数时候你不必分开用，通常把两个都绑定到`GL_FRAMEBUFFER`上就行。

很遗憾，现在我们还不能使用自己的帧缓冲，因为还没做完呢。建构一个完整的帧缓冲必须满足以下条件：

* 我们必须往里面加入至少一个附件（颜色、深度、模板缓冲）。
* 其中至少有一个是颜色附件。
* 所有的附件都应该是已经完全做好的（已经存储在内存之中）。
* 每个缓冲都应该有同样数目的样本。

如果你不知道什么是样本也不用担心，我们会在后面的教程中讲到。

从上面的需求中你可以看到，我们需要为帧缓冲创建一些附件(Attachment)，还需要把这些附件附加到帧缓冲上。当我们做完所有上面提到的条件的时候我们就可以用  `glCheckFramebufferStatus` 带上 `GL_FRAMEBUFFER` 这个参数来检查是否真的成功做到了。然后检查当前绑定的帧缓冲，返回了这些规范中的哪个值。如果返回的是 `GL_FRAMEBUFFER_COMPLETE`就对了：

```c++
if(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE)
  // Execute victory dance
```

后续所有渲染操作将渲染到当前绑定的帧缓冲的附加缓冲中，由于我们的帧缓冲不是默认的帧缓冲，渲染命令对窗口的视频输出不会产生任何影响。出于这个原因，它被称为离屏渲染（off-screen rendering），就是渲染到一个另外的缓冲中。为了让所有的渲染操作对主窗口产生影响我们必须通过绑定为0来使默认帧缓冲被激活：

```c++
glBindFramebuffer(GL_FRAMEBUFFER, 0);
```

当我们做完所有帧缓冲操作，不要忘记删除帧缓冲对象：

```c++
glDeleteFramebuffers(1, &fbo);
```

现在在执行完成检测前，我们需要把一个或更多的附件附加到帧缓冲上。一个附件就是一个内存地址，这个内存地址里面包含一个为帧缓冲准备的缓冲，它可以是个图像。当创建一个附件的时候我们有两种方式可以采用：纹理或渲染缓冲（renderbuffer）对象。

### 纹理附件

当把一个纹理附加到帧缓冲上的时候，所有渲染命令会写入到纹理上，就像它是一个普通的颜色/深度或者模板缓冲一样。使用纹理的好处是，所有渲染操作的结果都会被储存为一个纹理图像，这样我们就可以简单的在着色器中使用了。

创建一个帧缓冲的纹理和创建普通纹理差不多：

```c++
GLuint texture;
glGenTextures(1, &texture);
glBindTexture(GL_TEXTURE_2D, texture);

glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```

这里主要的区别是我们把纹理的维度设置为屏幕大小（尽管不是必须的），我们还传递NULL作为纹理的data参数。对于这个纹理，我们只分配内存，而不去填充它。纹理填充会在渲染到帧缓冲的时候去做。同样，要注意，我们不用关心环绕方式或者Mipmap，因为在大多数时候都不会需要它们的。

如果你打算把整个屏幕渲染到一个或大或小的纹理上，你需要用新的纹理的尺寸作为参数再次调用`glViewport`（要在渲染到你的帧缓冲之前做好），否则只有一小部分纹理或屏幕能够绘制到纹理上。

现在我们已经创建了一个纹理，最后一件要做的事情是把它附加到帧缓冲上：

```c++
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D, texture, 0);
```

`glFramebufferTexture2D`函数需要传入下列参数：

* target：我们所创建的帧缓冲类型的目标（绘制、读取或两者都有）。
* attachment：我们所附加的附件的类型。现在我们附加的是一个颜色附件。需要注意，最后的那个0是暗示我们可以附加1个以上颜色的附件。我们会在后面的教程中谈到。
* textarget：你希望附加的纹理类型。
* texture：附加的实际纹理。
* level：Mipmap level。我们设置为0。

除颜色附件以外，我们还可以附加一个深度和一个模板纹理到帧缓冲对象上。为了附加一个深度缓冲，我们可以知道那个`GL_DEPTH_ATTACHMENT`作为附件类型。记住，这时纹理格式和内部格式类型（internalformat）就成了 `GL_DEPTH_COMPONENT`去反应深度缓冲的存储格式。附加一个模板缓冲，你要使用 `GL_STENCIL_ATTACHMENT`作为第二个参数，把纹理格式指定为 `GL_STENCIL_INDEX`。

也可以同时附加一个深度缓冲和一个模板缓冲为一个单独的纹理。这样纹理的每32位数值就包含了24位的深度信息和8位的模板信息。为了把一个深度和模板缓冲附加到一个单独纹理上，我们使用`GL_DEPTH_STENCIL_ATTACHMENT`类型配置纹理格式以包含深度值和模板值的结合物。下面是一个附加了深度和模板缓冲为单一纹理的例子：

```c++
glTexImage2D( GL_TEXTURE_2D, 0, GL_DEPTH24_STENCIL8, 800, 600, 0, GL_DEPTH_STENCIL, GL_UNSIGNED_INT_24_8, NULL );

glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, texture, 0);
```

### 缓冲对象附件

在介绍了帧缓冲的可行附件类型——纹理后，OpenGL引进了渲染缓冲对象(Renderbuffer objects)，所以在过去那些美好时光里纹理是附件的唯一可用的类型。和纹理图像一样，渲染缓冲对象也是一个缓冲，它可以是一堆字节、整数、像素或者其他东西。渲染缓冲对象的一大优点是，它以OpenGL原生渲染格式储存它的数据，因此在离屏渲染到帧缓冲的时候，这些数据就相当于被优化过的了。

渲染缓冲对象将所有渲染数据直接储存到它们的缓冲里，而不会进行针对特定纹理格式的任何转换，这样它们就成了一种快速可写的存储介质了。然而，渲染缓冲对象通常是只写的，不能修改它们（就像获取纹理，不能写入纹理一样）。可以用`glReadPixels`函数去读取，函数返回一个当前绑定的帧缓冲的特定像素区域，而不是直接返回附件本身。

因为它们的数据已经是原生格式了，在写入或把它们的数据简单地到其他缓冲的时候非常快。当使用渲染缓冲对象时，像切换缓冲这种操作变得异常高速。我们在每个渲染迭代末尾使用的那个`glfwSwapBuffers`函数，同样以渲染缓冲对象实现：我们简单地写入到一个渲染缓冲图像，最后交换到另一个里。渲染缓冲对象对于这种操作来说很完美。

创建一个渲染缓冲对象和创建帧缓冲代码差不多：

```c++
GLuint rbo;
glGenRenderbuffers(1, &rbo);
```

相似地，我们打算把渲染缓冲对象绑定，这样所有后续渲染缓冲操作都会影响到当前的渲染缓冲对象：

```c++
glBindRenderbuffer(GL_RENDERBUFFER, rbo);
```

由于渲染缓冲对象通常是只写的，它们经常作为深度和模板附件来使用，由于大多数时候，我们不需要从深度和模板缓冲中读取数据，但仍关心深度和模板测试。我们就需要有深度和模板值提供给测试，但不需要对这些值进行采样（sample），所以深度缓冲对象是完全符合的。当我们不去从这些缓冲中采样的时候，渲染缓冲对象通常很合适，因为它们等于是被优化过的。

调用`glRenderbufferStorage`函数可以创建一个深度和模板渲染缓冲对象：

```c
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 800, 600);
```

创建一个渲染缓冲对象与创建纹理对象相似，不同之处在于这个对象是专门被设计用于图像的，而不是通用目的的数据缓冲，比如纹理。这里我们选择`GL_DEPTH24_STENCIL8`作为内部格式，它同时代表24位的深度和8位的模板缓冲。

最后一件还要做的事情是把帧缓冲对象附加上：

```c
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);
```

在帧缓冲项目中，渲染缓冲对象可以提供一些优化，但更重要的是知道何时使用渲染缓冲对象，何时使用纹理。通常的规则是，如果你永远都不需要从特定的缓冲中进行采样，渲染缓冲对象对特定缓冲是更明智的选择。如果哪天需要从比如颜色或深度值这样的特定缓冲采样数据的话，你最好还是使用纹理附件。从执行效率角度考虑，它不会对效率有太大影响。

### 渲染到纹理

现在我们知道了（一些）帧缓冲如何工作的，是时候把它们用起来了。我们会把场景渲染到一个颜色纹理上，这个纹理附加到一个我们创建的帧缓冲上，然后把纹理绘制到一个简单的四边形上，这个四边形铺满整个屏幕。输出的图像看似和没用帧缓冲一样，但是这次，它其实是直接打印到了一个单独的四边形上面。为什么这很有用呢？下一部分我们会看到原因。

第一件要做的事情是创建一个帧缓冲对象，并绑定它，这比较明了：

```c++
GLuint framebuffer;
glGenFramebuffers(1, &framebuffer);
glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
```

下一步我们创建一个纹理图像，这是我们将要附加到帧缓冲的颜色附件。我们把纹理的尺寸设置为窗口的宽度和高度，并保持数据未初始化：

```c++
// Generate texture
GLuint texColorBuffer;
glGenTextures(1, &texColorBuffer);
glBindTexture(GL_TEXTURE_2D, texColorBuffer);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glBindTexture(GL_TEXTURE_2D, 0);

// Attach it to currently bound framebuffer object
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texColorBuffer, 0);
```

我们同样打算要让OpenGL确定可以进行深度测试（模板测试，如果你用的话）所以我们必须还要确保向帧缓冲中添加一个深度（和模板）附件。由于我们只采样颜色缓冲，并不采样其他缓冲，我们可以创建一个渲染缓冲对象来达到这个目的。记住，当你不打算从指定缓冲采样的的时候，它们是一个不错的选择。

创建一个渲染缓冲对象不太难。唯一一件要记住的事情是，我们正在创建的是一个渲染缓冲对象的深度和模板附件。我们把它的内部给事设置为`GL_DEPTH24_STENCIL8`，对于我们的目的来说这个精确度已经足够了。

```c++
GLuint rbo;
glGenRenderbuffers(1, &rbo);
glBindRenderbuffer(GL_RENDERBUFFER, rbo);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 800, 600);  
glBindRenderbuffer(GL_RENDERBUFFER, 0);
```

我们为渲染缓冲对象分配了足够的内存空间以后，我们可以解绑渲染缓冲。

接着，在做好帧缓冲之前，还有最后一步，我们把渲染缓冲对象附加到帧缓冲的深度和模板附件上：

```c++
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);
```

然后我们要检查帧缓冲是否真的做好了，如果没有，我们就打印一个错误消息。

```c++
if(glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
 cout << "ERROR::FRAMEBUFFER:: Framebuffer is not complete!" << endl;
glBindFramebuffer(GL_FRAMEBUFFER, 0);
```

还要保证解绑帧缓冲，这样我们才不会意外渲染到错误的帧缓冲上。

现在帧缓冲做好了，我们要做的全部就是渲染到帧缓冲上，而不是绑定到帧缓冲对象的默认缓冲。余下所有命令会影响到当前绑定的帧缓冲上。所有深度和模板操作同样会从当前绑定的帧缓冲的深度和模板附件中读取，当然，得是在它们可用的情况下。如果你遗漏了比如深度缓冲，所有深度测试就不会工作，因为当前绑定的帧缓冲里没有深度缓冲。

所以，为把场景绘制到一个单独的纹理，我们必须以下面步骤来做：

1. 使用新的绑定为激活帧缓冲的帧缓冲，像往常那样渲染场景。
2. 绑定到默认帧缓冲。
3. 绘制一个四边形，让它平铺到整个屏幕上，用新的帧缓冲的颜色缓冲作为他的纹理。

我们使用在深度测试教程中同一个场景进行绘制，但是这次使用老气横秋的[箱子纹理](http://learnopengl.com/img/textures/container.jpg)。

为了绘制四边形我们将会创建新的着色器。我们不打算引入任何花哨的变换矩阵，因为我们只提供已经是标准化设备坐标的[顶点坐标](http://learnopengl.com/code_viewer.php?code=advanced/framebuffers_quad_vertices)，所以我们可以直接把它们作为顶点着色器的输出。顶点着色器看起来像这样：

```c++
#version 330 core
layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texCoords;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(position.x, position.y, 0.0f, 1.0f);
    TexCoords = texCoords;
}
```

没有花哨的地方。片段着色器更简洁，因为我们做的唯一一件事是从纹理采样：

```c++
#version 330 core
in vec2 TexCoords;
out vec4 color;

uniform sampler2D screenTexture;

void main()
{
    color = texture(screenTexture, TexCoords);
}
```

接着需要你为屏幕上的四边形创建和配置一个VAO。渲染迭代中帧缓冲处理会有下面的结构：

```c++
// First pass
glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // We're not using stencil buffer now
glEnable(GL_DEPTH_TEST);
DrawScene();

// Second pass
glBindFramebuffer(GL_FRAMEBUFFER, 0); // back to default
glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
glClear(GL_COLOR_BUFFER_BIT);

screenShader.Use();  
glBindVertexArray(quadVAO);
glDisable(GL_DEPTH_TEST);
glBindTexture(GL_TEXTURE_2D, textureColorbuffer);
glDrawArrays(GL_TRIANGLES, 0, 6);
glBindVertexArray(0);
```

只有很少的事情要说明。第一，由于我们用的每个帧缓冲都有自己的一系列缓冲，我们打算使用`glClear`设置的合适的位（bits）来清空这些缓冲。第二，当渲染四边形的时候，我们关闭深度测试，因为我们不关系深度测试，我们绘制的是一个简单的四边形；当我们绘制普通场景时我们必须再次开启深度测试。

这里的确有很多地方会做错，所以如果你没有获得任何输出，尝试排查任何可能出现错误的地方，再次阅读教程中相关章节。如果每件事都做对了就一定能成功，你将会得到这样的输出：

![](http://learnopengl.com/img/advanced/framebuffers_screen_texture.png)

左侧展示了和深度测试教程中一样的输出结果，但是这次却是渲染到一个简单的四边形上的。如果我们以线框方式显示的话，那么显然，我们只是绘制了一个默认帧缓冲中单调的四边形。

你可以[从这里得到应用的源码](http://learnopengl.com/code_viewer.php?code=advanced/framebuffers_screen_texture)。

然而这有什么好处呢？好处就是我们现在可以自由的获取已经渲染场景中的任何像素，然后把它当作一个纹理图像了，我们可以在片段着色器中创建一些有意思的效果。所有这些有意思的效果统称为后处理特效。


# 后期处理

现在，整个场景渲染到了一个单独的纹理上，我们可以创建一些有趣的效果，只要简单操纵纹理数据就能做到。这部分，我们会向你展示一些流行的后期处理(Post-processing)特效，以及怎样添加一些创造性去创建出你自己的特效。

### 反相

我们已经取得了渲染输出的每个颜色，所以在片段着色器里返回这些颜色的反色(Inversion)并不难。我们得到屏幕纹理的颜色，然后用1.0减去它：

```c++
void main()
{
    color = vec4(vec3(1.0 - texture(screenTexture, TexCoords)), 1.0);
}
```

虽然反相是一种相对简单的后处理特效，但是已经很有趣了：

![image description](http://learnopengl.com/img/advanced/framebuffers_grayscale.png)

整个场景现在的颜色都反转了，只需在着色器中写一行代码就能做到，酷吧？

### 灰度

另一个有意思的效果是移除所有除了黑白灰以外的颜色作用，是整个图像成为黑白的。实现它的简单的方式是获得所有颜色元素，然后将它们平均化：

```c++
void main()
{
    color = texture(screenTexture, TexCoords);
    float average = (color.r + color.g + color.b) / 3.0;
    color = vec4(average, average, average, 1.0);
}
```
这已经创造出很赞的效果了，但是人眼趋向于对绿色更敏感，对蓝色感知比较弱，所以为了获得更精确的符合人体物理的结果，我们需要使用加权通道：

```c++
void main()
{
    color = texture(screenTexture, TexCoords);
    float average = 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b;
    color = vec4(average, average, average, 1.0);
}
```

![](http://learnopengl.com/img/advanced/framebuffers_grayscale.png)

## Kernel effects

在单独纹理图像上进行后处理的另一个好处是我们可以从纹理的其他部分进行采样。比如我们可以从当前纹理值的周围采样多个纹理值。创造性地把它们结合起来就能创造出有趣的效果了。

kernel是一个长得有点像一个小矩阵的数值数组，它中间的值中心可以映射到一个像素上，这个像素和这个像素周围的值再乘以kernel，最后再把结果相加就能得到一个值。所以，我们基本上就是给当前纹理坐标加上一个它四周的偏移量，然后基于kernel把它们结合起来。下面是一个kernel的例子：

$$
\begin{bmatrix}2 & 2 & 2 \\ 2 & -15 & 2 \\ 2 & 2 & 2 \end{bmatrix}
$$

这个kernel表示一个像素周围八个像素乘以2，它自己乘以-15。这个例子基本上就是把周围像素乘上2，中间像素去乘以一个比较大的负数来进行平衡。

!!! Important

    你在网上能找到的kernel的例子大多数都是所有值加起来等于1，如果加起来不等于1就意味着这个纹理值比原来更大或者更小了。

kernel对于后处理来说非常管用，因为用起来简单。网上能找到有很多实例，为了能用上kernel我们还得改改片段着色器。这里假设每个kernel都是3×3（实际上大多数都是3×3）：

```c++
const float offset = 1.0 / 300;  

void main()
{
    vec2 offsets[9] = vec2[](
        vec2(-offset, offset),  // top-left
        vec2(0.0f,    offset),  // top-center
        vec2(offset,  offset),  // top-right
        vec2(-offset, 0.0f),    // center-left
        vec2(0.0f,    0.0f),    // center-center
        vec2(offset,  0.0f),    // center-right
        vec2(-offset, -offset), // bottom-left
        vec2(0.0f,    -offset), // bottom-center
        vec2(offset,  -offset)  // bottom-right
    );

    float kernel[9] = float[](
        -1, -1, -1,
        -1,  9, -1,
        -1, -1, -1
    );

    vec3 sampleTex[9];
    for(int i = 0; i < 9; i++)
    {
        sampleTex[i] = vec3(texture(screenTexture, TexCoords.st + offsets[i]));
    }
    vec3 col;
    for(int i = 0; i < 9; i++)
        col += sampleTex[i] * kernel[i];

    color = vec4(col, 1.0);
}
```

在片段着色器中我们先为每个四周的纹理坐标创建一个9个vec2偏移量的数组。偏移量是一个简单的常数，你可以设置为自己喜欢的。接着我们定义kernel，这里应该是一个锐化kernel，它通过一种有趣的方式从所有周边的像素采样，对每个颜色值进行锐化。最后，在采样的时候我们把每个偏移量加到当前纹理坐标上，然后用加在一起的kernel的值乘以这些纹理值。

这个锐化的kernel看起来像这样：

![](http://learnopengl.com/img/advanced/framebuffers_sharpen.png)

这里创建的有趣的效果就好像你的玩家吞了某种麻醉剂产生的幻觉一样。

### 模糊

创建模糊(Blur)效果的kernel定义如下：

$$
\(\begin{bmatrix} 1 & 2 & 1 \\ 2 & 4 & 2 \\ 1 & 2 & 1 \end{bmatrix} / 16\)
$$

由于所有数值加起来的总和为16,简单返回结合起来的采样颜色是非常亮的,所以我们必须将kernel的每个值除以16.最终的kernel数组会是这样的:

```c++
float kernel[9] = float[](
    1.0 / 16, 2.0 / 16, 1.0 / 16,
    2.0 / 16, 4.0 / 16, 2.0 / 16,
    1.0 / 16, 2.0 / 16, 1.0 / 16  
);
```

通过在像素着色器中改变kernel的float数组,我们就完全改变了之后的后处理效果.现在看起来会像是这样:

![](http://learnopengl.com/img/advanced/framebuffers_blur.png)

这样的模糊效果具有创建许多有趣效果的潜力.例如,我们可以随着时间的变化改变模糊量,创建出类似于某人喝醉酒的效果,或者,当我们的主角摘掉眼镜的时候增加模糊.模糊也能为我们在后面的教程中提供都颜色值进行平滑处理的能力.

你可以看到我们一旦拥有了这个kernel的实现以后,创建一个后处理特效就不再是一件难事.最后,我们再来讨论一个流行的特效,以结束本节内容.

### 边检测

下面的边检测(Edge-detection)kernel与锐化kernel类似:

$$
\begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix}
$$

这个kernel将所有的边提高亮度,而对其他部分进行暗化处理,当我们值关心一副图像的边缘的时候,它非常有用.

![](http://learnopengl.com/img/advanced/framebuffers_edge_detection.png)

在一些像Photoshop这样的软件中使用这些kernel作为图像操作工具/过滤器一点都不奇怪.因为掀开可以具有很强的平行处理能力，我们以实时进行针对每个像素的图像操作便相对容易，图像编辑工具因而更经常使用显卡来进行图像处理。

## 练习

* 你可以使用帧缓冲来创建一个后视镜吗?做到它,你必须绘制场景两次:一次正常绘制,另一次摄像机旋转180度后绘制.尝试在你的显示器顶端创建一个小四边形,在上面应用后视镜的镜面纹理:[解决方案](http://learnopengl.com/code_viewer.php?code=advanced/framebuffers-exercise1),[视觉效果](http://learnopengl.com/img/advanced/framebuffers_mirror.png)
* 自己随意调整一下kernel值,创建出你自己后处理特效.尝试在网上搜索其他有趣的kernel.
