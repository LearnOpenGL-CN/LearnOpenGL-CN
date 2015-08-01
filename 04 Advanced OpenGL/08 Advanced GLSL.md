## 高级GLSL

本文作者JoeyDeVries，由Django翻译自http://learnopengl.com

这章不会向你展示什么新的功能，也不会对你的场景的视觉效果有较大提升。本章多多少少地深入探讨了一些GLSL有意思的方面，以及可能在将来能帮助你的技巧。基本来说有些不可不知的内容和功能在你去使用GLSL创建OpenGL应用的时候能让你的生活更轻松。

我们会讨论一些有趣的内建变量、组织着色器输入和输出的新方式以及一个叫做uniform缓冲对象的非常有用的工具。

### GLSL的内建变量

着色器是很小的，如果我们需要从当前着色器以外的别的资源里的数据，那么我们就不得不穿给它。我们学过了使用顶点属性、uniform和采样器可以实现这个目标。GLSL有几个以gl_为前缀的变量，使我们有一个额外的手段来获取和写入数据。我们已经看到了两个：gl_Position和gl_FragCoord，前一个是顶点着色器的输出向量，后一个是片段着色器的变量。

我们会讨论几个有趣的GLSL内建变量，并向你解释为什么它们对我们来说很有好处。注意，我们不会讨论到GLSL中所有的内建变量，因此如果你想看到所有的内建变量还是最好去看[OpenGL的wiki](http://www.opengl.org/wiki/Built-in_Variable_(GLSL)。

#### 顶点着色器变量

我们已经了解gl_Position是顶点着色器裁切空间输出的位置向量。如果你想让屏幕上渲染出东西gl_Position必须使用。否则我们什么都看不到。

##### gl_PointSize

我们可以使用的另一个可用于渲染的基本图形（primitive）是GL_POINTS，使用它每个顶点作为一个基本图形，被渲染为一个点（point）。可以glPointSize函数来设置这个点的大小，但我们还可以在顶点着色器里影响点的大小。

GLSL有一个输出变量叫做gl_PointSize，他是一个float变量，你可以以像素的方式设置点的高度和宽度。每一个在着色器中描述每个顶点做为点的大小。

在着色器中影响点的大小默认是关闭的，但是如果你打算开启它，你需要开启OpenGL的GL_PROGRAM_POINT_SIZE：

```c++
glEnable(GL_PROGRAM_POINT_SIZE);
```

把点的大小设置为裁切空间的z值，这样点的大小就等于顶点距离观察者的距离，这是一种影响点的大小的方式。当顶点距离观察者更远的时候，它就会变得更大。

```c++
void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0f);
    gl_PointSize = gl_Position.z;
}
```

结果是我们绘制的点距离我们越远就越大：

![](http://bullteacher.com/wp-content/uploads/2015/06/advanced_glsl_pointsize.png)

想象一下，每个顶点表示出来的点的大小的不同，如果用在像粒子生成之类的技术里会挺有意思的。

 ##### gl_VertexID

gl_Position和gl_PointSize都是输出变量，因为它们的值是作为顶点着色器的输出被读取的；我们可以向它们写入数据来影响结果。顶点着色器为我们提供了一个有趣的输入变量，我们只能从它那里读取，这个变量叫做gl_VertexID。

gl_VertexID是个整型变量，它储存着我们绘制的当前顶点的ID。当进行索引渲染（indexed rendering，使用glDrawElements）时，这个变量保存着当前绘制的顶点的索引。当用的不是索引绘制（glDrawArrays）时，这个变量保存的是从渲染开始起直到当前处理的这个顶点的（当前顶点）编号。

尽管目前看似没用，但是我们最好知道我们能获取这样的信息。

#### 片段着色器的变量

在片段着色器中也有一些有趣的变量。GLSL给我们提供了两个有意思的输入变量，它们是gl_FragCoord和gl_FrontFacing。

##### gl_FragCoord

在讨论深度测试的时候，我们已经看过gl_FragCoord好几次了，因为gl_FragCoord向量的z元素和特定的fragment的深度值相等。然而，我们也可以使用这个向量的x和y元素来实现一些有趣的效果。

gl_FragCoord的x和y元素是这个fragment窗口空间坐标（window-space coordinate）。它们的起始处是窗口的左下角。如果我们的窗口是800×600的，那么一个fragment的窗口空间坐标x的范围就在0到800之间，y在0到600之间。

我们可以使用片段着色器基于fragment的窗口坐标计算出一个不同的颜色。gl_FragCoord变量的一个常用的方式是与一个不同的fragment计算出来的视频输出进行对比，通常在技术演示中常见。比如我们可以把屏幕分为两个部分，窗口的左侧渲染一个输出，窗口的右边渲染另一个输出。下面是一个基于fragment的窗口坐标的位置的不同输出不同的颜色的片段着色器：


```c++
void main()
{
    if(gl_FragCoord.x < 400)
        color = vec4(1.0f, 0.0f, 0.0f, 1.0f);
    else
        color = vec4(0.0f, 1.0f, 0.0f, 1.0f);
}
```

因为窗口的宽是800，当一个像素的x坐标小于400，那么它一定在窗口的左边，这样我们就让物体有个不同的颜色。

![](http://bullteacher.com/wp-content/uploads/2015/06/advanced_glsl_fragcoord.png)

我们现在可以计算出两个完全不同的片段着色器结果，每个显示在窗口的一端。这对于测试不同的光照技术很有好处。



gl_FrontFacing

片段着色器另一个有意思的输入变量是gl_FrontFacing变量。在面剔除教程中，我们提到过OpenGL可以根据顶点绘制顺序弄清楚一个面是正面还是背面。如果我们不适用面剔除，那么gl_FrontFacing变量能告诉我们当前fragment是一个正面的一部分还是背面的一部分。然后我们可以决定做一些事情，比如为正面计算出不同的颜色。

gl_FrontFacing变量是一个布尔值，如果fragment是正面的一部分那么就是true，否则就是false。这样我们可以创建一个立方体，里面和外面使用不同的纹理：

``c++
#version 330 core
out vec4 color;
in vec2 TexCoords;

uniform sampler2D frontTexture;
uniform sampler2D backTexture;

void main()
{
    if(gl_FrontFacing)
        color = texture(frontTexture, TexCoords);
    else
        color = texture(backTexture, TexCoords);
}
```

如果我们从箱子的一角往里看，就能看到里面用的是另一个纹理。

![](http://bullteacher.com/wp-content/uploads/2015/06/advanced_glsl_frontfacing.png)

注意，如果你开启了面剔除，你就看不到箱子里面有任何东西了，所以再使用gl_FrontFacing毫无意义。

##### gl_FragDepth

输入变量gl_FragCoord让我们可以读得当前fragment的窗口空间坐标和深度值，但是它是只读的。我们不能影响到这个fragment的窗口屏幕坐标，但是可以设置这个像素的深度值。GLSL给我们提供了一个叫做gl_FragDepth的变量，我们可以用它在着色器中遂舍之像素的深度值。

为了在着色器中设置深度值，我们简单的写一个0.0到1.0之间的float数，赋值给这个输出变量：

```c++
gl_FragDepth = 0.0f; // This fragment now has a depth value of 0.0f
```

如果着色器中没有像gl_FragDepth变量写入什么，它就会自动采用gl_FragCoord.z的值。

我们自己设置深度值有一个显著缺点，因为只要我们在片段着色器中对gl_FragDepth写入什么，OpenGL就会关闭所有的前置深度测试。它被关闭的原因是，在我们运行片段着色器之前OpenGL搞不清像素的深度值，因为片段着色器可能会完全改变这个深度值。

你也需要考虑到gl_FragDepth写入所带来的性能的下降。然而从OpenGL4.2起，我们仍然可以对二者进行一定的调和，这需要在片段着色器的顶部使用深度条件（depth condition）来重新声明gl_FragDepth：

```c++
layout (depth_<condition>) out float gl_FragDepth;
```

condition可以使用下面的值：

Condition	| 描述
         ---|---
any	        | 默认值. 前置深度测试是关闭的，你失去了很多性能表现
greater	    |深度值只能比gl_FragCoord.z大
less	    |深度值只能设置得比gl_FragCoord.z小
unchanged	|如果写入gl_FragDepth, 你就会写gl_FragCoord.z

如果把深度条件定义为greater或less，OpenGL会假定你只写入比当前的像素深度值的深度值大或小的。

下面是一个在片段着色器里增加深度值的例子，不过仍可开启前置深度测试：

```c++
#version 330 core
layout (depth_greater) out float gl_FragDepth;
out vec4 color;

void main()
{
    color = vec4(1.0f);
    gl_FragDepth = gl_FragCoord.z + 0.1f;
}
```

一定要记住这个功能只在OpenGL4.2以上版本才有。



### Interface blocks（接口块）

到目前位置，每次我们打算从顶点向片段着色器发送数据，我们都会声明一个相互匹配的输入/输入变量。从一个着色器向另一个着色器发送数据，一次将它们声明好是最简单的方式，但是随着应用变得越来越大，你也许会打算发送的不仅仅是变量，最好还可以包括数组和结构体。

为了帮助我们组织这些变量，GLSL为我们提供了一些叫做interface blocks的东西，好让我们能够组织这些变量。声明interface block和声明struct有点像，不同之处是它现在基于块（block），使用in和out关键字来声明，最后它将成为一个输入或输出块（block）。

```c++
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out VS_OUT
{
    vec2 TexCoords;
} vs_out;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0f);
    vs_out.TexCoords = texCoords;
}
```

这次我们声明一个叫做vs_out的interface block，它把我们需要发送给下个阶段着色器的所有输出变量组合起来。虽然这是一个微不足道的例子，但是你可以想象一下，它的确能够帮助我们组织着色器的输入和输出。当我们希望把着色器的输入和输出组织成数组的时候它就变得很有用，我们会在下节几何着色器（geometry）中见到。

然后，我们还需要在下一个着色器——片段着色器中声明一个输入interface block。块名（block name）应该是一样的，但是实例名可以是任意的。

```c++
#version 330 core
out vec4 color;

in VS_OUT
{
    vec2 TexCoords;
} fs_in;

uniform sampler2D texture;

void main()
{
    color = texture(texture, fs_in.TexCoords);
}
```

如果两个interface block名一致，它们对应的输入和输出就会匹配起来。这是另一个可以帮助我们组织代码的有用功能，特别是在跨着色阶段的情况，比如几何着色器。

### uniform缓冲对象

我们使用OpenGL很长时间了，也学到了一些很酷的技巧，但是产生了一些烦恼。比如说，当时用一个以上的着色器的时候，我们必须一次次设置uniform变量，尽管对于每个着色器来说它们都是一样的，所以为什么还麻烦地多次设置它们呢？

OpenGL为我们提供了一个叫做uniform缓冲对象的工具，使我们能够声明一系列的全局uniform变量， 它们会在几个着色器程序中保持一致。当时用uniform缓冲的对象时相关的uniform只能设置一次。我们仍需为每个着色器手工设置唯一的uniform。创建和配置一个uniform缓冲对象需要费点功夫。

因为uniform缓冲对象是一个缓冲，因此我们可以使用glGenBuffers创建一个，然后绑定到GL_UNIFORM_BUFFER缓冲目标上，然后把所有相关uniform数据存入缓冲。有一些原则，像uniform缓冲对象如何储存数据，我们会在稍后讨论。首先我们我们在一个简单的顶点着色器中，用uniform block（uniform块）储存projection和view矩阵：

```c++
#version 330 core
layout (location = 0) in vec3 position;

layout (std140) uniform Matrices
{
    mat4 projection;
    mat4 view;
};

uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
}
```

前面，大多数例子里我们在每次渲染迭代，都为projection和view矩阵设置uniform。这个例子里使用了uniform缓冲对象，这非常有用，因为这些矩阵我们设置一次就行了。

在这里我们声明了一个叫做Matrices的uniform block，它储存两个4×4矩阵。在uniform block中的变量可以直接获取，而不用使用block名作为前缀。接着我们在缓冲中储存这些矩阵的值，每个声明了这个uniform block的着色器已经能够获取矩阵了。

现在你可能会奇怪layout(std140)是什么意思。它的意思是说当前定义的uniform block为它的内容使用特定的内存布局；这个声明实际上是设置uniform block layout（uniform块布局）。



#### uniform block layout（uniform块布局）

一个uniform block的内容更被储存到一个缓冲对象中，实际上就是在一块内存中。因为这块内存也不清楚它保存着什么类型的数据，我们就必须告诉OpenGL哪一块内存对应着色器中哪一个uniform变量。

假想下面的uniform block在一个着色器中：

```c++
layout (std140) uniform ExampleBlock
{
    float value;
    vec3 vector;
    mat4 matrix;
    float values[3];
    bool boolean;
    int integer;
};
```

我们所希望知道的是每个变量的大小（以字节为单位）和偏移量（从block的起始处），所以我们可以以各自的顺序把它们放进一个缓冲里。每个元素的大小在OpenGL中都很清楚，直接与C++数据类型呼应；向量和矩阵是一个float序列（数组）。OpenGL没有澄清的是变量之间的间距。这让硬件能以它认为合适的位置方式变量。比如有些硬件可以在float旁边放置一个vec3。不是所有硬件都能这样做，在vec3旁边附加一个float之前，给vec3加一个边距使之成为4个（空间连续的）float数组。功能很好，但对于我们来说用起来不方便。

GLSL 默认使用的uniform内存布局叫做shared（共享）布局，叫共享是因为一旦偏移量被硬件定义，它们就会持续地被多个程序所共享。使用共享布局，GLSL可以为了优化而重新放置uniform变量，只要变量的顺序保持完整。因为我们不知道每个uniform变量的偏移量是多少，所以我们也就不知道如何精确地填充uniform缓冲。我们可以使用像glGetUniformIndices这样的函数来查询这个信息，但是这超出了本节教程的范围。

由于共享布局给我们做了一些空间优化。通常在实践中并不适用分享布局，而是使用std140布局。std140通过一系列的规则的规范声明了它们各自的偏移量，std140布局为每个变量类型显式地声明了内存的布局。由于被显式的提及，我们就可以手工算出每个变量的偏移量。

每个变量都有一个base alignment（基线对齐），它等于在一个uniform block中这个变量所占的空间（包含边距），这个基线对齐是使用std140布局原则计算出来的。然后，我们为每个变量计算出它的aligned offset（对齐偏移），这是一个变量从块（block）开始出的字节偏移量。变量对齐的字节偏移一定等于它的基线对齐的倍数。

准确的布局规则可以在OpenGL的uniform缓冲规范中得到，但我们会列出最常见的规范。GLSL中每个变量类型比如int、float和bool被定义为4字节的数量，每4字节被表示为N。

Type	    | Layout rule
         ---|---
Scalar e.g. int or bool |	Each scalar has a base alignment of N.
Vector      |	Either 2N or 4N. This means that a vec3 has a base alignment of 4N.
Array of scalars or vectors	| Each element has a base alignment equal to that of a vec4.
Matrices  |	Stored as a large array of column vectors, where each of those vectors has a base alignment of vec4.
Struct |	Equal to the computed size of its elements according to the previous rules, but padded to a multiple of the size of a vec4.

像OpenGL大多数规范一样，举个例子就很容易理解。再次利用之前介绍的uniform块ExampleBlock，我们用std140布局，计算它的每个成员的aligned offset（对齐偏移）：

```c++
layout (std140) uniform ExampleBlock
{
    //               // base alignment  // aligned offset
    float value;     // 4               // 0
    vec3 vector;     // 16              // 16  (must be multiple of 16 so 4->16)
    mat4 matrix;     // 16              // 32  (column 0)
                     // 16              // 48  (column 1)
                     // 16              // 64  (column 2)
                     // 16              // 80  (column 3)
    float values[3]; // 16              // 96  (values[0])
                     // 16              // 112 (values[1])
                     // 16              // 128 (values[2])
    bool boolean;    // 4               // 144
    int integer;     // 4               // 148
};
```

尝试自己计算出偏移量，把它们和表格对比，你可以把这件事当作一个练习。使用计算出来的偏移量，根据std140布局规则，我们可以用glBufferSubData这样的函数，使用变量数据填充缓冲。虽然不是很高效，但std140布局可以保证在每个程序中声明的这个uniform块的布局保持一致。

在定义uniform块前面添加layout (std140)声明，我们就能告诉OpenGL这个uniform块使用了std140布局。另外还有两种其他的布局可以选择，它们需要我们在填充缓冲之前查询每个偏移量。我们已经了解了分享布局（shared layout）和其他的布局都将被封装（packed）。当使用封装（packed）布局的时候，不能保证布局在别的程序中能够保持一致，因为它允许编译器从uniform block块中优化出去uniform变量，这在每个着色器中都可能不同。

#### 使用uniform缓冲

我们讨论了uniform block在着色器中的定义和如何定义它们的内存布局，但是我们还没有讨论如何使用它们。

首先我们需要创建一个uniform缓冲对象，这要使用glGenBuffers来完成。当我们拥有了一个缓冲对象，我们就把它绑定到GL_UNIFORM_BUFFER目标上，调用glBufferData来给它分配足够的空间。

```c++
GLuint uboExampleBlock;
glGenBuffers(1, &uboExampleBlock);
glBindBuffer(GL_UNIFORM_BUFFER, uboExampleBlock);
glBufferData(GL_UNIFORM_BUFFER, 150, NULL, GL_STATIC_DRAW); // allocate 150 bytes of memory
glBindBuffer(GL_UNIFORM_BUFFER, 0);
```

现在任何时候当我们打算往缓冲中更新或插入数据，我们就绑定到uboExampleBlock上，并使用glBufferSubData来更新它的内存。我们只需要更新这个uniform缓冲一次，所有的使用这个缓冲着色器就都会使用它更新的数据了。但是，OpenGL是如何知道哪个uniform缓冲对应哪个uniform block呢？

在OpenGL环境（context）中，定义了若干绑定点（binding points），在哪儿我们可以把一个uniform缓冲链接上去。当我们创建了一个uniform缓冲，我们把它链接到一个这个绑定点上，我们也把着色器中uniform block链接到同一个绑定点上，这样就把它们链接到一起了。下面的图标表示了这点：

![](http://bullteacher.com/wp-content/uploads/2015/06/advanced_glsl_binding_points.png)

你可以看到，我们可以将多个uniform缓冲绑定都不同绑定点上。因为着色器A和着色器B都有一个链接到同一个绑定点0的uniform block，它们的uniform block分享同样的uniform数据——uboMatrices；有一个前提条件是两个着色器必须都定义了Matrices这个uniform block。

我们调用glUniformBlockBinding函数来把uniform block设置到一个特定的绑定点上。函数的第一个参数是一个程序对象，接着是一个uniform block索引（uniform block index）和打算链接的绑定点。uniform block索引是一个着色器中定义的uniform block的索引位置，可以调用glGetUniformBlockIndex来获取这个值，这个函数接收一个程序对象和uniform block的名字。我们可以从图表设置Lights这个uniform block链接到绑定点2：

```c++
GLuint lights_index = glGetUniformBlockIndex(shaderA.Program, "Lights");
glUniformBlockBinding(shaderA.Program, lights_index, 2);
```

注意，我们必须在每个着色器中重复做这件事。

从OpenGL4.2起，也可以在着色器中通过添加另一个布局标识符来储存一个uniform block的绑定点，就不用我们调用glGetUniformBlockIndex和glUniformBlockBinding了。下面的代表显式设置了Lights这个uniform Block的绑定点：


```c++

layout(std140, binding = 2) uniform Lights { ... };

```

然后我们还需要把uniform缓冲对象绑定到同样的绑定点上，这个可以使用glBindBufferBase或glBindBufferRange来完成。

```c++
glBindBufferBase(GL_UNIFORM_BUFFER, 2, uboExampleBlock);
// or
glBindBufferRange(GL_UNIFORM_BUFFER, 2, uboExampleBlock, 0, 150);
```

函数glBindBufferBase接收一个目标、一个绑定点索引和一个uniform缓冲对象作为它的参数。这个函数把uboExampleBlock链接到绑定点2上面，自此绑定点所链接的两端都链接在一起了。你还可以使用glBindBufferRange函数，这个函数还需要一个偏移量和大小作为参数，这样你就可以只把一定范围的uniform缓冲绑定到一个绑定点上了。使用glBindBufferRage函数，你能够将多个不同的uniform block链接到同一个uniform缓冲对象上。

现在所有事情都做好了，我们可以开始向uniform缓冲添加数据了。我们可以使用glBufferSubData将所有数据添加为一个单独的字节数组或者更新缓冲的部分内容，只要我们愿意。为了更新uniform变量boolean，我们可以这样更新uniform缓冲对象：

```c++
glBindBuffer(GL_UNIFORM_BUFFER, uboExampleBlock);
GLint b = true; // bools in GLSL are represented as 4 bytes, so we store it in an integer
glBufferSubData(GL_UNIFORM_BUFFER, 142, 4, &b);
glBindBuffer(GL_UNIFORM_BUFFER, 0);
```

同样的处理也能够应用到uniform block中其他uniform变量上。

#### 一个简单的例子

我们来师范一个真实的使用uniform缓冲对象的例子。如果我们回头看看前面所有演示的代码，我们一直使用了3个矩阵：投影、视图和模型矩阵。所有这些矩阵中，只有模型矩阵是频繁变化的。如果我们有多个着色器使用了这些矩阵，我们可能最好还是使用uniform缓冲对象。
我们将把投影和视图矩阵储存到一个uniform block中，它被取名为Matrices。我们不打算储存模型矩阵，因为模型矩阵会频繁在着色器间更改，所以使用uniform缓冲对象真的不会带来什么好处。

```c++
#version 330 core
layout (location = 0) in vec3 position;

layout (std140) uniform Matrices
{
    mat4 projection;
    mat4 view;
};
uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
}
```

这儿没什么特别的，除了我们现在使用了一个带有std140布局的uniform block。我们在例程中将显示4个立方体，每个立方体都使用一个不同的着色器程序。4个着色器程序使用同样的顶点着色器，但是它们将使用各自的片段着色器，每个片段着色器输出一个单色。

首先，我们把顶点着色器的uniform block设置为绑定点0。注意，我们必须为每个着色器做这件事。

```c++
GLuint uniformBlockIndexRed = glGetUniformBlockIndex(shaderRed.Program, "Matrices");
GLuint uniformBlockIndexGreen = glGetUniformBlockIndex(shaderGreen.Program, "Matrices");
GLuint uniformBlockIndexBlue = glGetUniformBlockIndex(shaderBlue.Program, "Matrices");
GLuint uniformBlockIndexYellow = glGetUniformBlockIndex(shaderYellow.Program, "Matrices");  

glUniformBlockBinding(shaderRed.Program, uniformBlockIndexRed, 0);
glUniformBlockBinding(shaderGreen.Program, uniformBlockIndexGreen, 0);
glUniformBlockBinding(shaderBlue.Program, uniformBlockIndexBlue, 0);
glUniformBlockBinding(shaderYellow.Program, uniformBlockIndexYellow, 0);
```

然后，我们创建真正的uniform缓冲对象，并把缓冲绑定到绑定点0：

```c++
GLuint uboMatrices
glGenBuffers(1, &uboMatrices);

glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices);
glBufferData(GL_UNIFORM_BUFFER, 2 * sizeof(glm::mat4), NULL, GL_STATIC_DRAW);
glBindBuffer(GL_UNIFORM_BUFFER, 0);

glBindBufferRange(GL_UNIFORM_BUFFER, 0, uboMatrices, 0, 2 * sizeof(glm::mat4));
```

我们纤维我们的缓冲分配足够的内存，它等于glm::mat4的2倍。GLM的矩阵类型的大小直接对应于GLSL的mat4。然后我们把一个特定范围的缓冲链接到绑定点0，这个例子中应该是整个缓冲。

现在所有要做的事只剩下填充缓冲了。如果我们把视野（ field of view）值保持为恒定的投影矩阵（这样就不会有摄像机缩放），我们只要在程序中定义它一次就行了，这也意味着我们只需向缓冲中把它插入一次。因为我们已经在缓冲对象中分配了足够的内存，我们可以在我们进入游戏循环之前使用glBufferSubData来储存投影矩阵：

```c++
glm::mat4 projection = glm::perspective(45.0f, (float)width/(float)height, 0.1f, 100.0f);
glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices);
glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(glm::mat4), glm::value_ptr(projection));
glBindBuffer(GL_UNIFORM_BUFFER, 0);
```

这里我们用投影矩阵储存了uniform缓冲的前半部分。在我们在每次渲染迭代绘制物体前，我们用视图矩阵更新缓冲的第二个部分：

```c++
glm::mat4 view = camera.GetViewMatrix();
glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices);
glBufferSubData(
  GL_UNIFORM_BUFFER, sizeof(glm::mat4), sizeof(glm::mat4), glm::value_ptr(view));
glBindBuffer(GL_UNIFORM_BUFFER, 0);
```

这就是uniform缓冲对象。每个包含着Matrices这个uniform block的顶点着色器豆浆邦汉uboMatrices所储存的数据。所以如果我们现在使用4个不同的着色器绘制4个立方体，它们的投影和视图矩阵都是一样的：

```c++
glBindVertexArray(cubeVAO);
shaderRed.Use();
glm::mat4 model;
model = glm::translate(model, glm::vec3(-0.75f, 0.75f, 0.0f)); // Move top-left
glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
glDrawArrays(GL_TRIANGLES, 0, 36);
// ... Draw Green Cube
// ... Draw Blue Cube
// ... Draw Yellow Cube
glBindVertexArray(0);
```

我们只需要在去设置一个model的unform即可。在一个像这样的场景中使用uniform缓冲对象在每个着色器中可以减少uniform的调用。最后效果看起来像这样：

![](http://learnopengl.com/img/advanced/advanced_glsl_uniform_buffer_objects.png)

通过改变模型矩阵，每个立方体都移动到窗口的一边，由于片段着色器不同，物体的颜色也不同。这是一个相对简单的场景，我们可以使用uniform缓冲对象，但是任何大型渲染程序有成百上千的活动着色程序；彼时uniform缓冲对象就会闪闪发光了。

你可以[在这里获得例程的完整源码](http://www.learnopengl.com/code_viewer.php?code=advanced/advanced_glsl_uniform_buffer_objects)。

uniform缓冲对象比单独的uniform有很多好处。第一，一次设置多个uniform比一次设置一个速度快。第二，如果你打算改变一个横跨多个着色器的uniform，在uniform缓冲中只需更改一次。最后一个好处可能不是很明显，使用uniform缓冲对象你可以在着色器中使用更多的uniform。OpenGL有一个对可使用uniform数据的数量的限制，可以用GL_MAX_VERTEX_UNIFORM_COMPONENTS来获取。当使用uniform缓冲对象中，这个限制的阈限会更高。所以无论何时，你达到了uniform的最大使用数量（比如做谷歌动画的时候），你可以使用uniform缓冲对象。
