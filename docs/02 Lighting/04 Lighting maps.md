# 光照贴图

原文     | [Lighting maps](http://learnopengl.com/#!Lighting/Lighting-maps)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com), [BLumia](https://github.com/blumia/)

前面的教程，我们讨论了让不同的物体拥有各自不同的材质并对光照做出不同的反应的方法。在一个光照场景中，让每个物体拥有和其他物体不同的外观很棒，但是这仍然不能对一个物体的图像输出提供足够多的灵活性。

前面的教程中我们将一个物体自身作为一个整体为其定义了一个材质，但是现实世界的物体通常不会只有这么一种材质，而是由多种材质组成。想象一辆车：它的外表质地光亮，车窗会部分反射环境，它的轮胎没有specular高光，轮彀却非常闪亮（在洗过之后）。汽车同样有diffuse和ambient颜色，它们在整个车上都不相同；一辆车显示了多种不同的ambient/diffuse颜色。总之，这样一个物体每个部分都有多种材质属性。

所以，前面的材质系统对于除了最简单的模型以外都是不够的，所以我们需要扩展前面的系统，我们要介绍diffuse和specular贴图。它们允许你对一个物体的diffuse（而对于简洁的ambient成分来说，它们几乎总是是一样的）和specular成分能够有更精确的影响。

# 漫反射贴图

我们希望通过某种方式对每个原始像素独立设置diffuse颜色。有可以让我们基于物体原始像素的位置来获取颜色值的系统吗？

这可能听起来极其相似，坦白来讲我们使用这样的系统已经有一段时间了。听起来很像在一个[之前的教程](../01 Getting started/06 Textures.md)中谈论的**纹理**，它基本就是一个纹理。我们其实是使用同一个潜在原则下的不同名称：使用一张图片覆盖住物体，以便我们为每个原始像素索引独立颜色值。在光照场景中，通过纹理来呈现一个物体的diffuse颜色，这个做法被称做**漫反射贴图(Diffuse texture)**(因为3D建模师就是这么称呼这个做法的)。

为了演示漫反射贴图，我们将会使用[下面的图片](http://learnopengl.com/img/textures/container2.png)，它是一个有一圈钢边的木箱：

![](http://www.learnopengl.com/img/textures/container2.png)

在着色器中使用漫反射贴图和纹理教程介绍的一样。这次我们把纹理以sampler2D类型储存在Material结构体中。我们使用diffuse贴图替代早期定义的vec3类型的diffuse颜色。

!!! Attention
    
    要记住的是sampler2D也叫做模糊类型，这意味着我们不能以某种类型对它实例化，只能用uniform定义它们。如果我们用结构体而不是uniform实例化（就像函数的参数那样），GLSL会抛出奇怪的错误；这同样也适用于其他模糊类型。
我们也要移除amibient材质颜色向量，因为ambient颜色绝大多数情况等于diffuse颜色，所以不需要分别去储存它：

```c++
struct Material
{
    sampler2D diffuse;
    vec3 specular;
    float shininess;
};
...
in vec2 TexCoords;
```
!!! Important

    如果你非把ambient颜色设置为不同的值不可（不同于diffuse值），你可以继续保留ambient的vec3，但是整个物体的ambient颜色会继续保持不变。为了使每个原始像素得到不同ambient值，你需要对ambient值单独使用另一个纹理。

注意，在片段着色器中我们将会再次需要纹理坐标，所以我们声明一个额外输入变量。然后我们简单地从纹理采样，来获得原始像素的diffuse颜色值：
    
```c++
vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
```

同样，不要忘记把ambient材质的颜色设置为diffuse材质的颜色：

```c++
vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
```

这就是diffuse贴图的全部内容了。就像你看到的，这不是什么新的东西，但是它却极大提升了视觉品质。为了让它工作，我们需要用到纹理坐标更新顶点数据，把它们作为顶点属性传递到片段着色器，把纹理加载并绑定到合适的纹理单元。

更新的顶点数据可以从[这里](http://learnopengl.com/code_viewer.php?code=lighting/vertex_data_textures)找到。顶点数据现在包括了顶点位置，法线向量和纹理坐标，每个立方体的顶点都有这些属性。让我们更新顶点着色器来接受纹理坐标作为顶点属性，然后发送到片段着色器：

```c++
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoords;
...
out vec2 TexCoords;

void main()
{
    ...
    TexCoords = texCoords;
}
```

要保证更新的顶点属性指针，不仅是VAO匹配新的顶点数据，也要把箱子图片加载为纹理。在绘制箱子之前，我们希望首选纹理单元被赋为material.diffuse这个uniform采样器，并绑定箱子的纹理到这个纹理单元：

```c++
glUniform1i(glGetUniformLocation(lightingShader.Program, "material.diffuse"), 0);
...
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, diffuseMap);
```

现在，使用一个diffuse贴图，我们在细节上再次获得惊人的提升，这次添加到箱子上的光照开始闪光了（名符其实）。你的箱子现在可能看起来像这样：

![](http://www.learnopengl.com/img/lighting/materials_diffuse_map.png)

你可以在这里得到应用的[全部代码](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps_diffuse)。


# 镜面贴图

你可能注意到，specular高光看起来不怎么样，由于我们的物体是个箱子，大部分是木头，我们知道木头是不应该有镜面高光的。我们通过把物体设置specular材质设置为vec3(0.0f)来修正它。但是这样意味着铁边会不再显示镜面高光，我们知道钢铁是会显示一些镜面高光的。我们会想要控制物体部分地显示镜面高光，它带有修改了的亮度。这个问题看起来和diffuse贴图的讨论一样。这是巧合吗？我想不是。

我们同样用一个纹理贴图，来获得镜面高光。这意味着我们需要生成一个黑白（或者你喜欢的颜色）纹理来定义specular亮度，把它应用到物体的每个部分。下面是一个[镜面贴图(Specular Map)](http://learnopengl.com/img/textures/container2_specular.png)的例子：

![](http://www.learnopengl.com/img/textures/container2_specular.png)

一个specular高光的亮度可以通过图片中每个纹理的亮度来获得。specular贴图的每个像素可以显示为一个颜色向量，比如：在那里黑色代表颜色向量vec3(0.0f)，灰色是vec3(0.5f)。在片段着色器中，我们采样相应的颜色值，把它乘以光的specular亮度。像素越“白”，乘积的结果越大，物体的specualr部分越亮。

由于箱子几乎是由木头组成，木头作为一个材质不会有镜面高光，整个木头部分的diffuse纹理被用黑色覆盖：黑色部分不会包含任何specular高光。箱子的铁边有一个修改的specular亮度，它自身更容易受到镜面高光影响，木纹部分则不会。

从技术上来讲，木头也有镜面高光，尽管这个闪亮值很小（更多的光被散射），影响很小，但是为了学习目的，我们可以假装木头不会有任何specular光反射。

使用Photoshop或Gimp之类的工具，通过将图片进行裁剪，将某部分调整成黑白图样，并调整亮度/对比度的做法，可以非常容易将一个diffuse纹理贴图处理为specular贴图。


## 镜面贴图采样

一个specular贴图和其他纹理一样，所以代码和diffuse贴图的代码也相似。确保合理的加载了图片，生成一个纹理对象。由于我们在同样的片段着色器中使用另一个纹理采样器，我们必须为specular贴图使用一个不同的纹理单元(参见[纹理](../01 Getting started/06 Textures.md))，所以在渲染前让我们把它绑定到合适的纹理单元

```c++
glUniform1i(glGetUniformLocation(lightingShader.Program, "material.specular"), 1);
...
glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, specularMap);
```

然后更新片段着色器材质属性，接受一个sampler2D作为这个specular部分的类型，而不是vec3：

```c++
struct Material
{
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};
```

最后我们希望采样这个specular贴图，来获取原始像素相应的specular亮度：

```c++
vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
color = vec4(ambient + diffuse + specular, 1.0f);
```

通过使用一个specular贴图我们可以定义极为精细的细节，物体的这个部分会获得闪亮的属性，我们可以设置它们相应的亮度。specular贴图给我们一个附加的高于diffuse贴图的控制权限。

如果你不想成为主流，你可以在specular贴图里使用颜色，不单单为每个原始像素设置specular亮度，同时也设置specular高光的颜色。从真实角度来说，specular的颜色基本是由光源自身决定的，所以它不会生成真实的图像（这就是为什么图片通常是黑色和白色的：我们只关心亮度）。

如果你现在运行应用，你可以清晰地看到箱子的材质现在非常类似真实的铁边的木头箱子了：

![](http://www.learnopengl.com/img/lighting/materials_specular_map.png)

你可以在这里找到[全部源码](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps_specular)。也对比一下你的[顶点着色器](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps&type=vertex)和[片段着色器](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps&type=fragment)。

使用diffuse和specular贴图，我们可以给相关但简单物体添加一个极为明显的细节。我们可以使用其他纹理贴图，比如法线/bump贴图或者反射贴图，给物体添加更多的细节。但是这些在后面教程才会涉及。把你的箱子给你所有的朋友和家人看，有一天你会很满足，我们的箱子会比现在更漂亮！

## 练习

- 调整光源的ambient，diffuse和specular向量值，看看它们如何影响实际输出的箱子外观。
- 尝试在片段着色器中反转镜面贴图(Specular Map)的颜色值，然后木头就会变得反光而边框不会反光了（由于贴图中钢边依然有一些残余颜色，所以钢边依然会有一些高光，不过反光明显小了很多）。[参考解答](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps-exercise2)
- 使用漫反射纹理(Diffuse Texture)原本的颜色而不是黑白色来创建镜面贴图，并观察，你会发现结果显得并不那么真实了。如果你不会处理图片，你可以使用这个[带颜色的镜面贴图](http://learnopengl.com/img/lighting/lighting_maps_specular_color.png)。[最终效果](learnopengl.com/img/lighting/lighting_maps_exercise3.png)
- 添加一个叫做**放射光贴图(Emission Map)**的东西，即记录每个片段发光值(Emission Value)大小的贴图，发光值是(模拟)物体自身**发光(Emit)**时可能产生的颜色。这样的话物体就可以忽略环境光自身发光。通常在你看到游戏里某个东西(比如 [机器人的眼](http://www.witchbeam.com.au/unityboard/shaders_enemy.jpg),或是[箱子上的小灯](http://www.tomdalling.com/images/posts/modern-opengl-08/emissive.png))在发光时，使用的就是放射光贴图。使用[这个](http://learnopengl.com/img/textures/matrix.jpg)贴图(作者为 creativesam)作为放射光贴图并使用在箱子上，你就会看到箱子上有会发光的字了。[参考解答](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps-exercise4),[片段着色器](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps-exercise4_fragment), [最终效果](http://learnopengl.com/img/lighting/lighting_maps_exercise4.png)
