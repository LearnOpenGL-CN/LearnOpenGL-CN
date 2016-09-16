# 模板测试

原文     | [Stencil testing](http://learnopengl.com/#!Advanced-OpenGL/Stencil-testing)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)

当片段着色器处理完片段之后，**模板测试(Stencil Test)** 就开始执行了，和深度测试一样，它能丢弃一些片段。仍然保留下来的片段进入深度测试阶段，深度测试可能丢弃更多。模板测试基于另一个缓冲，这个缓冲叫做**模板缓冲(Stencil Buffer)**，我们被允许在渲染时更新它来获取有意思的效果。

模板缓冲中的**模板值(Stencil Value)**通常是8位的，因此每个片段/像素共有256种不同的模板值（译注：8位就是1字节大小，因此和char的容量一样是256个不同值）。这样我们就能将这些模板值设置为我们链接的，然后在模板测试时根据这个模板值，我们就可以决定丢弃或保留它了。

!!! Important

    每个窗口库都需要为你设置模板缓冲。GLFW自动做了这件事，所以你不必告诉GLFW去创建它，但是其他库可能没默认创建模板库，所以一定要查看你使用的库的文档。

下面是一个模板缓冲的简单例子：

![image description](../img/04/02/stencil_buffer.png)

模板缓冲先清空模板缓冲设置所有片段的模板值为0，然后开启矩形片段用1填充。场景中的模板值为1的那些片段才会被渲染（其他的都被丢弃）。

无论我们在渲染哪里的片段，模板缓冲操作都允许我们把模板缓冲设置为一个特定值。改变模板缓冲的内容实际上就是对模板缓冲进行写入。在同一次（或接下来的）渲染迭代我们可以读取这些值来决定丢弃还是保留这些片段。当使用模板缓冲的时候，你可以随心所欲，但是需要遵守下面的原则：

* 开启模板缓冲写入。
* 渲染物体，更新模板缓冲。
* 关闭模板缓冲写入。
* 渲染（其他）物体，这次基于模板缓冲内容丢弃特定片段。

使用模板缓冲我们可以基于场景中已经绘制的片段，来决定是否丢弃特定的片段。

你可以开启`GL_STENCIL_TEST`来开启模板测试。接着所有渲染函数调用都会以这样或那样的方式影响到模板缓冲。

```c++
glEnable(GL_STENCIL_TEST);
```
要注意的是，像颜色和深度缓冲一样，在每次循环，你也得清空模板缓冲。

```c++
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
```

同时，和深度测试的`glDepthMask`函数一样，模板缓冲也有一个相似函数。`glStencilMask`允许我们给模板值设置一个**位遮罩(Bitmask)**，它与模板值进行按位与(AND)运算决定缓冲是否可写。默认设置的位遮罩都是1，这样就不会影响输出，但是如果我们设置为0x00，所有写入深度缓冲最后都是0。这和深度缓冲的`glDepthMask(GL_FALSE)`很类似：

```c++

// 0xFF == 0b11111111
//此时，模板值与它进行按位与运算结果是模板值，模板缓冲可写
glStencilMask(0xFF); 

// 0x00 == 0b00000000 == 0
//此时，模板值与它进行按位与运算结果是0，模板缓冲不可写
glStencilMask(0x00); 
```

大多数情况你的模板遮罩（stencil mask）写为0x00或0xFF就行，但是最好知道有一个选项可以自定义位遮罩。

## 模板函数

和深度测试一样，我们也有几个不同控制权，决定何时模板测试通过或失败以及它怎样影响模板缓冲。一共有两种函数可供我们使用去配置模板测试：`glStencilFunc`和`glStencilOp`。

`void glStencilFunc(GLenum func, GLint ref, GLuint mask)`函数有三个参数：

* **func**：设置模板测试操作。这个测试操作应用到已经储存的模板值和`glStencilFunc`的`ref`值上，可用的选项是：`GL_NEVER`、`GL_LEQUAL`、`GL_GREATER`、`GL_GEQUAL`、`GL_EQUAL`、`GL_NOTEQUAL`、`GL_ALWAYS`。它们的语义和深度缓冲的相似。
* **ref**：指定模板测试的引用值。模板缓冲的内容会与这个值对比。
* **mask**：指定一个遮罩，在模板测试对比引用值和储存的模板值前，对它们进行按位与（and）操作，初始设置为1。

在上面简单模板的例子里，方程应该设置为：

```c
glStencilFunc(GL_EQUAL, 1, 0xFF)
```

它会告诉OpenGL，无论何时，一个片段模板值等于(`GL_EQUAL`)引用值`1`，片段就能通过测试被绘制了，否则就会被丢弃。

但是`glStencilFunc`只描述了OpenGL对模板缓冲做什么，而不是描述我们如何更新缓冲。这就需要`glStencilOp`登场了。

`void glStencilOp(GLenum sfail, GLenum dpfail, GLenum dppass)`函数包含三个选项，我们可以指定每个选项的动作：

* **sfail**：  如果模板测试失败将采取的动作。
* **dpfail**： 如果模板测试通过，但是深度测试失败时采取的动作。
* **dppass**： 如果深度测试和模板测试都通过，将采取的动作。

每个选项都可以使用下列任何一个动作。

操作 | 描述
  ---|---
GL_KEEP     | 保持现有的模板值
GL_ZERO	    | 将模板值置为0
GL_REPLACE  | 将模板值设置为用`glStencilFunc`函数设置的**ref**值
GL_INCR	    | 如果模板值不是最大值就将模板值+1
GL_INCR_WRAP| 与`GL_INCR`一样将模板值+1，如果模板值已经是最大值则设为0
GL_DECR	    | 如果模板值不是最小值就将模板值-1
GL_DECR_WRAP| 与`GL_DECR`一样将模板值-1，如果模板值已经是最小值则设为最大值
GL_INVERT   | Bitwise inverts the current stencil buffer value.

`glStencilOp`函数默认设置为 (GL_KEEP, GL_KEEP, GL_KEEP) ，所以任何测试的任何结果，模板缓冲都会保留它的值。默认行为不会更新模板缓冲，所以如果你想写入模板缓冲的话，你必须像任意选项指定至少一个不同的动作。

使用`glStencilFunc`和`glStencilOp`，我们就可以指定在什么时候以及我们打算怎么样去更新模板缓冲了，我们也可以指定何时让测试通过或不通过。什么时候片段会被抛弃。

# 物体轮廓

看了前面的部分你未必能理解模板测试是如何工作的，所以我们会展示一个用模板测试实现的一个特别的和有用的功能，叫做**物体轮廓(Object Outlining)**。

![](../img/04/02/stencil_object_outlining.png)

物体轮廓就像它的名字所描述的那样，它能够给每个（或一个）物体创建一个有颜色的边。在策略游戏中当你打算选择一个单位的时候它特别有用。给物体加上轮廓的步骤如下：

1. 在绘制物体前，把模板方程设置为`GL_ALWAYS`，用1更新物体将被渲染的片段。
2. 渲染物体，写入模板缓冲。
3. 关闭模板写入和深度测试。
4. 每个物体放大一点点。
5. 使用一个不同的片段着色器用来输出一个纯颜色。
6. 再次绘制物体，但只是当它们的片段的模板值不为1时才进行。
7. 开启模板写入和深度测试。

这个过程将每个物体的片段模板缓冲设置为1，当我们绘制边框的时候，我们基本上绘制的是放大版本的物体的通过测试的地方，放大的版本绘制后物体就会有一个边。我们基本会使用模板缓冲丢弃所有的不是原来物体的片段的放大的版本内容。

我们先来创建一个非常基本的片段着色器，它输出一个边框颜色。我们简单地设置一个固定的颜色值，把这个着色器命名为shaderSingleColor：

```c++
void main()
{
    outColor = vec4(0.04, 0.28, 0.26, 1.0);
}
```

我们只打算给两个箱子加上边框，所以我们不会对地面做什么。这样我们要先绘制地面，然后再绘制两个箱子（同时写入模板缓冲），接着我们绘制放大的箱子（同时丢弃前面已经绘制的箱子的那部分片段）。

我们先开启模板测试，设置模板、深度测试通过或失败时才采取动作：

```c++
glEnable(GL_DEPTH_TEST);
glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);
```

如果任何测试失败我们都什么也不做，我们简单地保持深度缓冲中当前所储存着的值。如果模板测试和深度测试都成功了，我们就将储存着的模板值替换为`1`，我们要用`glStencilFunc`来做这件事。

我们清空模板缓冲为0，为箱子的所有绘制的片段的模板缓冲更新为1：

```c++
glStencilFunc(GL_ALWAYS, 1, 0xFF); //所有片段都要写入模板缓冲
glStencilMask(0xFF); // 设置模板缓冲为可写状态
normalShader.Use();
DrawTwoContainers();
```

使用`GL_ALWAYS`模板测试函数，我们确保箱子的每个片段用模板值1更新模板缓冲。因为片段总会通过模板测试，在我们绘制它们的地方，模板缓冲用引用值更新。

现在箱子绘制之处，模板缓冲更新为1了，我们将要绘制放大的箱子，但是这次关闭模板缓冲的写入：

```c++
glStencilFunc(GL_NOTEQUAL, 1, 0xFF);
glStencilMask(0x00); // 禁止修改模板缓冲
glDisable(GL_DEPTH_TEST);
shaderSingleColor.Use();
DrawTwoScaledUpContainers();
```

我们把模板方程设置为`GL_NOTEQUAL`，它保证我们只箱子上不等于1的部分，这样只绘制前面绘制的箱子外围的那部分。注意，我们也要关闭深度测试，这样放大的的箱子也就是边框才不会被地面覆盖。

做完之后还要保证再次开启深度缓冲。

场景中的物体边框的绘制方法最后看起来像这样：

```c++
glEnable(GL_DEPTH_TEST);
glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);  

glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);

glStencilMask(0x00); // 绘制地板时确保关闭模板缓冲的写入
normalShader.Use();
DrawFloor()  

glStencilFunc(GL_ALWAYS, 1, 0xFF);
glStencilMask(0xFF);
DrawTwoContainers();

glStencilFunc(GL_NOTEQUAL, 1, 0xFF);
glStencilMask(0x00);
glDisable(GL_DEPTH_TEST);
shaderSingleColor.Use();
DrawTwoScaledUpContainers();
glStencilMask(0xFF);
glEnable(GL_DEPTH_TEST);
```

理解这段代码后面的模板测试的思路并不难以理解。如果还不明白尝试再仔细阅读上面的部分，尝试理解每个函数的作用，现在你已经看到了它的使用方法的例子。

这个边框的算法的结果在深度测试教程的那个场景中，看起来像这样：

![](../img/04/02/stencil_scene_outlined.png)

在这里[查看源码](http://learnopengl.com/code_viewer.php?code=advanced/stencil_testing)和[着色器](http://learnopengl.com/code_viewer.php?code=advanced/depth_testing_func_shaders)，看看完整的物体边框算法是怎样的。

!!! Important

	你可以看到两个箱子边框重合通常正是我们希望得到的（想想策略游戏中，我们打算选择10个单位；我们通常会希望把边界合并）。如果你想要让每个物体都有自己的边界那么你需要为每个物体清空模板缓冲，创造性地使用深度缓冲。

你目前看到的物体边框算法在一些游戏中显示备选物体（想象策略游戏）非常常用，这样的算法可以在一个模型类中轻易实现。你可以简单地在模型类设置一个布尔类型的标识来决定是否绘制边框。如果你想要更多的创造性，你可以使用后处理（post-processing）过滤比如高斯模糊来使边框看起来更自然。

除了物体边框以外，模板测试还有很多其他的应用目的，比如在后视镜中绘制纹理，这样它会很好的适合镜子的形状，比如使用一种叫做shadow volumes的模板缓冲技术渲染实时阴影。模板缓冲在我们的已扩展的OpenGL工具箱中给我们提供了另一种好用工具。