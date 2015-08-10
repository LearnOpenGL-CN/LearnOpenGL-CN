# 立方体贴图(Cubemap)

原文     | [Cubemaps](http://learnopengl.com/#!Advanced-OpenGL/Cubemaps)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)

我们之前一直使用的是2D纹理，还有更多的纹理类型我们没有探索过，本教程中我们讨论的纹理类型是将多个纹理组合起来映射到一个单一纹理，它就是cubemap。

基本上说cubemap它包含6个2D纹理，这每个2D纹理是一个立方体（cube）的一个面，也就是说它是一个有贴图的立方体。你可能会奇怪这样的立方体有什么用？为什么费事地把6个独立纹理结合为一个单独的纹理，只使用6个各自独立的不行吗？这是因为cubemap有自己特有的属性，可以使用方向向量对它们索引和采样。想象一下，我们有一个1×1×1的单位立方体，有个以原点为起点的方向向量在它的中心。

从cubemap上使用橘黄色向量采样一个纹理值看起来和下图有点像：

![](http://learnopengl.com/img/advanced/cubemaps_sampling.png)

!!! Important

        方向向量的大小无关紧要。一旦提供了方向，OpenGL就会获取方向向量触碰到立方体表面上的相应的纹理像素（texel），这样就返回了正确的纹理采样值。


方向向量触碰到立方体表面的一点也就是cubemap的纹理位置，这意味着只要立方体的中心位于原点上，我们就可以使用立方体的位置向量来对cubemap进行采样。然后我们就可以获取所有顶点的纹理坐标，就和立方体上的顶点位置一样。所获得的结果是一个纹理坐标，通过这个纹理坐标就能获取到cubemap上正确的纹理。

### 创建一个Cubemap

Cubemap和其他纹理一样，所以要创建一个cubemap，在进行任何纹理操作之前，需要生成一个纹理，激活相应纹理单元然后绑定到合适的纹理目标上。这次要绑定到 `GL_TEXTURE_CUBE_MAP`纹理类型：

```c++
GLuint textureID;
glGenTextures(1, &textureID);
glBindTexture(GL_TEXTURE_CUBE_MAP, textureID);
```

由于cubemap包含6个纹理，立方体的每个面一个纹理，我们必须调用`glTexImage2D`函数6次，函数的参数和前面教程讲的相似。然而这次我们必须把纹理目标（target）参数设置为cubemap特定的面，这是告诉OpenGL我们创建的纹理是对应立方体哪个面的。因此我们便需要为cubemap的每个面调用一次 `glTexImage2D`。

由于cubemap有6个面，OpenGL就提供了6个不同的纹理目标，来应对cubemap的各个面。

纹理目标（Texture target）	   | 方位
                            ---|---
GL_TEXTURE_CUBE_MAP_POSITIVE_X |	右
GL_TEXTURE_CUBE_MAP_NEGATIVE_X |	左
GL_TEXTURE_CUBE_MAP_POSITIVE_Y |	上
GL_TEXTURE_CUBE_MAP_NEGATIVE_Y |	下
GL_TEXTURE_CUBE_MAP_POSITIVE_Z |	后
GL_TEXTURE_CUBE_MAP_NEGATIVE_Z |	前

和很多OpenGL其他枚举一样，对应的int值都是连续增加的，所以我们有一个纹理位置的数组或vector，就能以 `GL_TEXTURE_CUBE_MAP_POSITIVE_X`为起始来对它们进行遍历，每次迭代枚举值加 `1`，这样循环所有的纹理目标效率较高：

```c++
int width,height;
unsigned char* image;  
for(GLuint i = 0; i < textures_faces.size(); i++)
{
    image = SOIL_load_image(textures_faces[i], &width, &height, 0, SOIL_LOAD_RGB);
    glTexImage2D(
        GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
        0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image
    );
}
```

这儿我们有个vector叫`textures_faces`，它包含cubemap所各个纹理的文件路径，并且以上表所列的顺序排列。它将为每个当前绑定的cubemp的每个面生成一个纹理。

由于cubemap和其他纹理没什么不同，我们也要定义它的环绕方式和过滤方式：

```c++
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
```

别被 `GL_TEXTURE_WRAP_R`吓到，它只是简单的设置了纹理的R坐标，R坐标对应于纹理的第三个维度（就像位置的z一样）。我们把放置方式设置为 `GL_CLAMP_TO_EDGE` ，由于纹理坐标在两个面之间，所以可能并不能触及哪个面（由于硬件限制），因此使用 `GL_CLAMP_TO_EDGE` 后OpenGL会返回它们的边界的值，尽管我们可能在两个两个面中间进行的采样。

在绘制物体之前，将使用cubemap，而在渲染前我们要激活相应的纹理单元并绑定到cubemap上，这和普通的2D纹理没什么区别。

在片段着色器中，我们也必须使用一个不同的采样器——**samplerCube**，用它来从`texture`函数中采样，但是这次使用的是一个`vec3`方向向量，取代`vec2`。下面是一个片段着色器使用了cubemap的例子：

```c++
in vec3 textureDir; // 用一个三维方向向量来表示Cubemap纹理的坐标

uniform samplerCube cubemap;  // Cubemap纹理采样器

void main()
{
    color = texture(cubemap, textureDir);
}
```

看起来不错，但是何必这么做呢？因为恰巧使用cubemap可以简单的实现很多有意思的技术。其中之一便是著名的**天空盒(Skybox)**。



## 天空盒(Skybox)

天空盒是一个包裹整个场景的立方体，它由6个图像构成一个环绕的环境，给玩家一种他所在的场景比实际的要大得多的幻觉。比如有些在视频游戏中使用的天空盒的图像是群山、白云或者满天繁星。比如下面的夜空繁星的图像就来自《上古卷轴》：

![](http://learnopengl.com/img/advanced/cubemaps_morrowind.jpg)

你现在可能已经猜到cubemap完全满足天空盒的要求：我们有一个立方体，它有6个面，每个面需要一个贴图。上图中使用了几个夜空的图片给予玩家一种置身广袤宇宙的感觉，可实际上，他还是在一个小盒子之中。

网上有很多这样的天空盒的资源。[这个网站](http://www.custommapmakers.org/skyboxes.php)就提供了很多。这些天空盒图像通常有下面的样式：

![](http://learnopengl.com/img/advanced/cubemaps_skybox.png)

如果你把这6个面折叠到一个立方体中，你机会获得模拟了一个巨大的风景的立方体。有些资源所提供的天空盒比如这个例子6个图是连在一起的，你必须手工它们切割出来，不过大多数情况它们都是6个单独的纹理图像。

这个细致（高精度）的天空盒就是我们将在场景中使用的那个，你可以[在这里下载](http://learnopengl.com/img/textures/skybox.rar)。

### 加载一个天空盒

由于天空盒实际上就是一个cubemap，加载天空盒和之前我们加载cubemap的没什么大的不同。为了加载天空盒我们将使用下面的函数，它接收一个包含6个纹理文件路径的vector：

```c++
GLuint loadCubemap(vector<const GLchar*> faces)
{
    GLuint textureID;
    glGenTextures(1, &textureID);
    glActiveTexture(GL_TEXTURE0);

    int width,height;
    unsigned char* image;

    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID);
    for(GLuint i = 0; i < faces.size(); i++)
    {
        image = SOIL_load_image(faces[i], &width, &height, 0, SOIL_LOAD_RGB);
        glTexImage2D(
            GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0,
            GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image
        );
    }
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
    glBindTexture(GL_TEXTURE_CUBE_MAP, 0);

    return textureID;
}
```

这个函数没什么特别之处。这就是我们前面已经见过的cubemap代码，只不过放进了一个可管理的函数中。

然后，在我们调用这个函数之前，我们将把合适的纹理路径加载到一个vector之中，顺序还是按照cubemap枚举的特定顺序：

```c++
vector<const GLchar*> faces;
faces.push_back("right.jpg");
faces.push_back("left.jpg");
faces.push_back("top.jpg");
faces.push_back("bottom.jpg");
faces.push_back("back.jpg");
faces.push_back("front.jpg");
GLuint cubemapTexture = loadCubemap(faces);
```

现在我们已经用`cubemapTexture`作为id把天空盒加载为cubemap。我们现在可以把它绑定到一个立方体来替换不完美的`clear color`，在前面的所有教程中这个东西做背景已经很久了。



### 天空盒的显示

因为天空盒绘制在了一个立方体上，我们还需要另一个VAO、VBO以及一组全新的顶点，和任何其他物体一样。你可以[从这里获得顶点数据](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps_skybox_data)。

cubemap用于给3D立方体帖上纹理，可以用立方体的位置作为纹理坐标进行采样。当一个立方体的中心位于原点(0，0，0)的时候，它的每一个位置向量也就是以原点为起点的方向向量。这个方向向量就是我们要得到的立方体某个位置的相应纹理值。出于这个理由，我们只需要提供位置向量，而无需纹理坐标。为了渲染天空盒，我们需要一组新着色器，它们不会太复杂。因为我们只有一个顶点属性，顶点着色器非常简单：

```c++
#version 330 core
layout (location = 0) in vec3 position;
out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position =   projection * view * vec4(position, 1.0);  
    TexCoords = position;
}
```

注意，顶点着色器有意思的地方在于我们把输入的位置向量作为输出给片段着色器的纹理坐标。片段着色器就会把它们作为输入去采样samplerCube：

```c++
#version 330 core
in vec3 TexCoords;
out vec4 color;

uniform samplerCube skybox;

void main()
{
    color = texture(skybox, TexCoords);
}
```

片段着色器比较明了，我们把顶点属性中的位置向量作为纹理的方向向量，使用它们从cubemap采样纹理值。渲染天空盒现在很简单，我们有了一个cubemap纹理，我们简单绑定cubemap纹理，天空盒就自动地用天空盒的cubemap填充了。为了绘制天空盒，我们将把它作为场景中第一个绘制的物体并且关闭深度写入。这样天空盒才能成为所有其他物体的背景来绘制出来。

```c++

glDepthMask(GL_FALSE);
skyboxShader.Use();
// ... Set view and projection matrix
glBindVertexArray(skyboxVAO);
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemapTexture);
glDrawArrays(GL_TRIANGLES, 0, 36);
glBindVertexArray(0);
glDepthMask(GL_TRUE);
// ... Draw rest of the scene
```

如果你运行程序就会陷入困境，我们希望天空盒以玩家为中心，这样无论玩家移动了多远，天空盒都不会变近，这样就产生一种四周的环境真的非常大的印象。当前的视图矩阵对所有天空盒的位置进行了转转缩放和平移变换，所以玩家移动，cubemap也会跟着移动！我们打算移除视图矩阵的平移部分，这样移动就影响不到天空盒的位置向量了。在基础光照教程里我们提到过我们可以只用4X4矩阵的3×3部分去除平移。我们可以简单地将矩阵转为33矩阵再转回来，就能达到目标

```c++
glm::mat4 view = glm::mat4(glm::mat3(camera.GetViewMatrix()));
```

这会移除所有平移，但保留所有旋转，因此用户仍然能够向四面八方看。由于有了天空盒，场景即可变得巨大了。如果你添加些物体然后自由在其中游荡一会儿你会发现场景的真实度有了极大提升。最后的效果看起来像这样：

![](http://learnopengl.com/img/advanced/cubemaps_skybox_result.png)

[这里有全部源码](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps_skybox)，你可以对比一下你写的。

尝试用不同的天空盒实验，看看它们对场景有多大影响。

### 优化

现在我们在渲染场景中的其他物体之前渲染了天空盒。这么做没错，但是不怎么高效。如果我们先渲染了天空盒，那么我们就是在为每一个屏幕上的像素运行片段着色器，即使天空盒只有部分在显示着；fragment可以使用前置深度测试（early depth testing）简单地被丢弃，这样就节省了我们宝贵的带宽。

所以最后渲染天空盒就能够给我们带来轻微的性能提升。采用这种方式，深度缓冲被全部物体的深度值完全填充，所以我们只需要渲染通过前置深度测试的那部分天空的片段就行了，而且能显著减少片段着色器的调用。问题是天空盒是个1×1×1的立方体，极有可能会渲染失败，因为极有可能通不过深度测试。简单地不用深度测试渲染它也不是解决方案，这是因为天空盒会在之后覆盖所有的场景中其他物体。我们需要耍个花招让深度缓冲相信天空盒的深度缓冲有着最大深度值1.0，如此只要有个物体存在深度测试就会失败，看似物体就在它前面了。

在坐标系教程中我们说过，透视除法（perspective division）是在顶点着色器运行之后执行的，把`gl_Position`的xyz坐标除以w元素。我们从深度测试教程了解到除法结果的z元素等于顶点的深度值。利用这个信息，我们可以把输出位置的z元素设置为它的w元素，这样就会导致z元素等于1.0了，因为，当透视除法应用后，它的z元素转换为w/w = 1.0：

```c++
void main()
{
    vec4 pos = projection * view * vec4(position, 1.0);
    gl_Position = pos.xyww;
    TexCoords = position;
}
```

最终，标准化设备坐标就总会有个与1.0相等的z值了，1.0就是深度值的最大值。只有在没有任何物体可见的情况下天空盒才会被渲染（只有通过深度测试才渲染，否则假如有任何物体存在，就不会被渲染，只去渲染物体）。

我们必须改变一下深度方程，把它设置为`GL_LEQUAL`，原来默认的是`GL_LESS`。深度缓冲会为天空盒用1.0这个值填充深度缓冲，所以我们需要保证天空盒是使用小于等于深度缓冲来通过深度测试的，而不是小于。

你可以在这里找到优化过的版本的[源码](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps_skybox_optimized)。

### 环境映射

我们现在有了一个把整个环境映射到为一个单独纹理的对象，我们利用这个信息能做的不仅是天空盒。使用带有场景环境的cubemap，我们还可以让物体有一个反射或折射属性。像这样使用了环境cubemap的技术叫做**环境贴图技术**，其中最重要的两个是**反射(reflection)**和**折射(refraction)**。

#### 反射(reflection)

凡是是一个物体（或物体的某部分）反射他周围的环境的属性，比如物体的颜色多少有些等于它周围的环境，这要基于观察者的角度。例如一个镜子是一个反射物体：它会基于观察者的角度泛着它周围的环境。

反射的基本思路不难。下图展示了我们如何计算反射向量，然后使用这个向量去从一个cubemap中采样：

![](http://learnopengl.com/img/advanced/cubemaps_reflection_theory.png)

我们基于观察方向向量I和物体的法线向量N计算出反射向量R。我们可以使用GLSL的内建函数reflect来计算这个反射向量。最后向量R作为一个方向向量对cubemap进行索引/采样，返回一个环境的颜色值。最后的效果看起来就像物体反射了天空盒。

因为我们在场景中已经设置了一个天空盒，创建反射就不难了。我们改变一下箱子使用的那个片段着色器，给箱子一个反射属性：

```c++
#version 330 core
in vec3 Normal;
in vec3 Position;
out vec4 color;

uniform vec3 cameraPos;
uniform samplerCube skybox;

void main()
{
    vec3 I = normalize(Position - cameraPos);
    vec3 R = reflect(I, normalize(Normal));
    color = texture(skybox, R);
}
```

我们先来计算观察/摄像机方向向量I，然后使用它来计算反射向量R，接着我们用R从天空盒cubemap采样。要注意的是，我们有了片段的插值Normal和Position变量，所以我们需要修正顶点着色器适应它。

```c++
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

out vec3 Normal;
out vec3 Position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0f);
    Normal = mat3(transpose(inverse(model))) * normal;
    Position = vec3(model * vec4(position, 1.0f));
}
```

我们用了法线向量，所以我们打算使用一个**法线矩阵(normal matrix)**变换它们。`Position`输出的向量是一个世界空间位置向量。顶点着色器输出的`Position`用来在片段着色器计算观察方向向量。

因为我们使用法线，你还得更新顶点数据，更新属性指针。还要确保设置`cameraPos`的uniform。

然后在渲染箱子前我们还得绑定cubemap纹理：

```c++
glBindVertexArray(cubeVAO);
glBindTexture(GL_TEXTURE_CUBE_MAP, skyboxTexture);
glDrawArrays(GL_TRIANGLES, 0, 36);
glBindVertexArray(0);
```

编译运行你的代码，你等得到一个镜子一样的箱子。箱子完美地反射了周围的天空盒：

![](http://learnopengl.com/img/advanced/cubemaps_reflection.png)

你可以[从这里找到全部源代码](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps_reflection)。

当反射应用于整个物体之上的时候，物体看上去就像有一个像钢和铬这种高反射材质。如果我们加载[模型教程](http://learnopengl-cn.readthedocs.org/zh/latest/03%20Model%20Loading/03%20Model/)中的纳米铠甲模型，我们就会获得一个铬金属制铠甲：

![](http://learnopengl.com/img/advanced/cubemaps_reflection_nanosuit.png)

看起来挺惊艳，但是现实中大多数模型都不是完全反射的。我们可以引进反射贴图（reflection map）来使模型有另一层细节。和diffuse、specular贴图一样，我们可以从反射贴图上采样来决定fragment的反射率。使用反射贴图我们还可以决定模型的哪个部分有反射能力，以及强度是多少。本节的练习中，要由你来在我们早期创建的模型加载器引入反射贴图，这回极大的提升纳米服模型的细节。

#### 折射(refraction)

环境映射的另一个形式叫做折射，它和反射差不多。折射是光线通过特定材质对光线方向的改变。我们通常看到像水一样的表面，光线并不是直接通过的，而是让光线弯曲了一点。它看起来像你把半只手伸进水里的效果。

折射遵守[斯涅尔定律](http://en.wikipedia.org/wiki/Snell%27s_law)，使用环境贴图看起来就像这样：

![](http://learnopengl.com/img/advanced/cubemaps_refraction_theory.png)

我们有个观察向量I，一个法线向量N，这次折射向量是R。就像你所看到的那样，观察向量的方向有轻微弯曲。弯曲的向量R随后用来从cubemap上采样。

折射可以通过GLSL的内建函数refract来实现，除此之外还需要一个法线向量，一个观察方向和一个两种材质之间的折射指数。

折射指数决定了一个材质上光线扭曲的数量，每个材质都有自己的折射指数。下表是常见的折射指数：

材质  |	折射指数
---|---
空气 |	1.00
水	 | 1.33
冰	 | 1.309
玻璃 |	1.52
宝石 |	2.42

我们使用这些折射指数来计算光线通过两个材质的比率。在我们的例子中，光线/视线从空气进入玻璃（如果我们假设箱子是玻璃做的）所以比率是1.001.52 = 0.658。

我们已经绑定了cubemap，提供了定点数据，设置了摄像机位置的uniform。现在只需要改变片段着色器：

```c++
void main()
{
    float ratio = 1.00 / 1.52;
    vec3 I = normalize(Position - cameraPos);
    vec3 R = refract(I, normalize(Normal), ratio);
    color = texture(skybox, R);
}
```

通过改变折射指数你可以创建出完全不同的视觉效果。编译运行应用，结果也不是太有趣，因为我们只是用了一个普通箱子，这不能显示出折射的效果，看起来像个放大镜。使用同一个着色器，纳米服模型却可以展示出我们期待的效果：玻璃制物体。

![](http://learnopengl.com/img/advanced/cubemaps_refraction.png)

你可以向想象一下，如果将光线、反射、折射和顶点的移动合理的结合起来就能创造出漂亮的水的图像。一定要注意，出于物理精确的考虑当光线离开物体的时候还要再次进行折射；现在我们简单的使用了单边（一次）折射，大多数目的都可以得到满足。

#### 动态环境贴图（Dynamic environment maps）

现在，我们已经使用了静态图像组合的天空盒，看起来不错，但是没有考虑到物体可能移动的实际场景。我们到现在还没注意到这点，是因为我们目前还只使用了一个物体。如果我们有个镜子一样的物体，它周围有多个物体，只有天空盒在镜子中可见，和场景中只有这一个物体一样。

使用帧缓冲可以为提到的物体的所有6个不同角度创建一个场景的纹理，把它们每次渲染迭代储存为一个cubemap。之后我们可以使用这个（动态生成的）cubemap来创建真实的反射和折射表面，这样就能包含所有其他物体了。这种方法叫做动态环境映射（dynamic environment mapping）,因为我们动态地创建了一个物体的以其四周为参考的cubemap，并把它用作环境贴图。

它看起效果很好，但是有一个劣势：使用环境贴图我们必须为每个物体渲染场景6次，这需要非常大的开销。现代应用尝试尽量使用天空盒子，凡可能预编译cubemap就创建少量动态环境贴图。动态环境映射是个非常棒的技术，要想在不降低执行效率的情况下实现它就需要很多巧妙的技巧。



## 练习

尝试在模型加载中引进反射贴图，你将再次得到很大视觉效果的提升。这其中有几点需要注意：

- Assimp并不支持反射贴图，我们可以使用环境贴图的方式将反射贴图从`aiTextureType_AMBIENT`类型中来加载反射贴图的材质。
- 我匆忙地使用反射贴图来作为镜面反射的贴图，而反射贴图并没有很好的映射在模型上:)。
- 由于加载模型已经占用了3个纹理单元，因此你要绑定天空盒到第4个纹理单元上，这样才能在同一个着色器内从天空盒纹理中取样。

You can find the solution source code here together with the updated model and mesh class. The shaders used for rendering the reflection maps can be found here: vertex shader and fragment shader. 

你可以在此获取解决方案的[源代码](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1)，这其中还包括升级过的[Model](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1-model)和[Mesh](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1-mesh)类，还有用来绘制反射贴图的[顶点着色器](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1-vertex)和[片段着色器](http://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1-fragment)。

如果你一切都做对了，那你应该看到和下图类似的效果：

![](http://learnopengl.com/img/advanced/cubemaps_reflection_map.png)
