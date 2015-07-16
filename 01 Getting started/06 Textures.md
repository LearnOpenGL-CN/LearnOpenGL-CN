##纹理（Textures）
本文作者JoeyDeVries，由Django翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/Textures)

我们已经了解，可以为每个顶点使用颜色来增加物体细节，从而创建出有趣的图像。但是，为了获得足够的显示我们就必须有足够多的顶点，才能指定足够多的颜色。这会花费很多额外开销，因为每个模型都会需求更多的顶点和顶点颜色。

艺术家和程序员更喜欢使用纹理（texture）。纹理是一个2D图片（也有1D和3D），它用来添加物体的细节；这就像有一张绘有砖块的图片贴到你的3D的房子上，你的房子看起来就有了一个砖墙。因为我们可以在一张图片上插入足够多的细节，这样物体就会拥有很多细节而不会增加额外的顶点。

!!! Important

         除了图像以外，纹理也可以储存数据，这些数据用来发送到着色器上，但是我们会留在其他主题来讨论这个问题。
         
下面你会看到前面的那个三角形平铺了一个砖墙的图片。

![](http://learnopengl.com/img/getting-started/textures.png)

为了能够把纹理映射到三角形上，我们需要说明三角形的每个顶点各自对应纹理的哪个部分。这样每个顶点就会有一个纹理坐标（texture coordinate），它指明从纹理图像的哪个地方采样。之后在所有的其他的像素上进行像素插值。

纹理坐标是x和y轴上0到1之间的范围（我们使用的是2D纹理图片）。使用纹理坐标获取纹理颜色叫做采样（sampling）。纹理坐标起始于（0, 0）也就是纹理图片的左下角，终结于纹理图片的右上角。下面的图片展示了我们是如何把纹理坐标映射到三角形上的：

![](http://learnopengl.com/img/getting-started/tex_coords.png)

我们为三角形准备了3个纹理坐标点。我们希望三角形的左下角对应纹理的左下角，因此我们把三角左下角的顶点的纹理坐标设置为（0, 0）。三角形的顶点对应于图片的中间所以我们把它的纹理坐标设置为（0.5, 1.0）。我们只要传递三个纹理坐标给顶点着色器就行了，接着片段着色器会为每个像素生成纹理坐标的插值。

纹理坐标看起来就像这样：

```c++
GLfloat texCoords[] = {
    0.0f, 0.0f, // 左下角
    1.0f, 0.0f, // 右下角
    0.5f, 1.0f // 顶部位置
};
```
纹理采样有几种不同的插值方式。我们需要自己告诉OpenGL在纹理中采用哪种采样方式。

###纹理环绕方式（Texture Wrapping）

纹理坐标通常的范围是从(0, 0)到(1, 1)，如果我们把纹理坐标设置为范围以外会发生什么？OpenGL默认的行为是重复这个纹理图像（我们简单地忽略浮点纹理坐标的整数部分），但OpenGL提供了更多的选择：

GL_REPEAT：纹理的默认行为。重复纹理图像。
GL_MIRRORED_REPEAET：和GL_REPEAT一样，除了重复的图片是镜像放置的。
GL_CLAMP_TO_EDGE：纹理坐标会在0到1之间。超出的部分会重复纹理坐标的边缘，就是边缘被拉伸。
GL_CLAMP_TO_BORDER：超出的部分是用户指定的边缘的颜色。
当纹理坐标超出默认范围时，每个选项都有一个不同的视觉效果输出。我们来看看这些纹理图像的例子：

![](http://learnopengl.com/img/getting-started/texture_wrapping.png)

前面提到的选项都可以使用glTexParameter*函数单独设置每个坐标轴s、t(如果是使用3D纹理那么也有一个r）它们和x、y（z）是相等的：

* glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT);

* glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT);

第一个参数指定了纹理目标；我们使用的是2D纹理，因此纹理目标是GL_TEXTURE_2D。

第二个参数需要我们去告知我们希望去设置哪个纹理轴。

我们打算设置的是WRAP选项，并且指定S和T轴。最后一个参数需要我们传递放置方式，在这个例子里我们在党建激活纹理上应用GL_MIRRORED_REPEAT。

如果我们选择GL_CLAMP_TO_BORDER选项，我们还要指定一个边缘的颜色。这次使用glTexParameter函数的fv后缀形式，加上GL_TEXTURE_BORDER_COLOR作为选项，这个函数需要我们传递一个边缘颜色的float数组作为颜色值：

```c++
float borderColor[] = { 1.0f, 1.0f, 0.0f, 1.0f };
glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);
```
###纹理过滤（Texture Filtering）

纹理坐标不依赖解析度，它可以是任何浮点数值，这样OpenGL需要描述出哪个纹理像素对应哪个纹理坐标（译注：texture pixel也叫texel，你可以想象你打开一张.jpg格式图片不断放大你会发现它是由无数像素点组成的，这个点就是纹理像素；注意不要和纹理坐标搞混，纹理坐标是你给模型顶点设置的那个数组，OpenGL以这个顶点的纹理坐标数据去查找纹理图像上的像素，然后进行采样提取纹理像素的颜色）。当你有一个很大的物体但是纹理解析度很低的时候这就变得很重要了。你可能已经猜到了，OpenGL也有一个叫做纹理过滤的选项。有多种不同的选项可用，但是现在我们只讨论最重要的两种：GL_NEAREST和GL_LINEAR。

GL_NEAREST(也叫最邻近过滤）是一种OpenGL默认的纹理过滤方式。当设置为GL_NEAREST的时候，OpenGL选择最接近纹理坐标中心点的那个像素。下图你会看到四个像素，加号代表纹理坐标。左上角的纹理像素是距离纹理坐标最近的那个，这样它就会选择这个作为采样颜色：

![](http://learnopengl.com/img/getting-started/filter_nearest.png)

GL_LINEAR也叫做线性过滤，它会从纹理坐标的临近纹理像素进行插值，返回一个多个纹理像素的近似值。一个纹理像素距离纹理坐标越近，那么这个纹理像素对最终的采样颜色的影响越大。下面你会看到临近像素返回的混合颜色：

![](http://learnopengl.com/img/getting-started/filter_linear.png)

不同的纹理过滤方式有怎样的视觉效果呢？让我们看看当在一个很大的物体上应用一张地解析度的纹理会发生什么吧（纹理被放大了，纹理像素也能看到）：

![](http://learnopengl.com/img/getting-started/texture_filtering.png)

GL_NEAREST返回了格子一样的样式，我们能够清晰看到纹理由像素组成，而GL_LINEAR产生出更平滑的样式，看不出纹理像素。GL_LINEAR是一种更真实的输出，但有些开发者更喜欢8-bit风格，所以他们还是用GL_NEAREST选项。

纹理过滤可已设置放大和缩小的选项，这样你可以在纹理被缩小的时候使用最临近过滤，被放大时使用线性过滤。我们必须通过glTexParameter*为放大和缩小指定过滤方式。这段代码看起来和纹理放置方式（Texture Wrapping）的设置相似：

```c++
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```
###Mipmaps

想象一下，如果我们在一个有着上千物体的大房间，每个物体上都有纹理。距离观察者远的与距离近的物体的纹理的解析度是相同的。由于远处的物体可能只产生很少的片段，OpenGL从高解析度纹理中为这些片段获取正确的颜色值就很困难。这是因为它不得不拾为一个纹理跨度很大的片段取纹理颜色。在小物体上这会产生人工感，更不用说在小物体上使用高解析度纹理浪费内存的问题了。

OpenGL使用一种叫做mipmaps的概念解决这个问题，大概来说它就是一系列纹理，每个后面的一个纹理是前一个的二分之一。mipmaps背后的思想很简单：距离观察者更远的距离的一段确定的阈值，OpenGL会把最适合这个距离的物体的不同的mipmap纹理应用其上。由于距离远，解析度不高也不会被使用者注意到。同时，mipmap另一加分之处是，执行效率不错。让我们近距离看一看mipmap纹理：

![](http://learnopengl.com/img/getting-started/mipmaps.png)

手工为每个纹理图像创建一系列mipmap纹理很麻烦，幸好OpenGL有一个glGenerateMipmaps函数，它可以在我们创建完一个纹理后帮我们做所有的mipmap创建工作。后面的纹理教程中你会看到如何使用它。

OpenGL渲染的时候，两个不同级别的mipmap之间会产生不真实感的生硬的边界。就像普通的纹理过滤一样，也可以在两个不同mipmap级别之间使用NEAREST和LINEAR过滤。指定不同mipmap级别之间的过滤方式可以使用下面四种选项代替原来的过滤方式：

* GL_NEAREST_MIPMAP_NEAREST：接收最近的mipmap来匹配像素大小，并使用最临近插值进行纹理采样。
* GL_LINEAR_MIPMAP_NEAREST：接收最近的mipmap级别，并使用线性插值采样。
* GL_NEAREST_MIPMAP_LINEAR：在两个mipmap之间进行线性插值，通过最邻近插值采样。
* GL_LINEAR_MIPMAP_LINEAR：在两个相邻的mipmap进行线性插值，并通过线性插值进行采样。
就像纹理过滤一样，前面提到的四种方法也可以使用glTexParameteri设置过滤方式：

```c++
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```
常见的错误是，为mipmap过滤选项设置放大过滤。这样没有任何效果，因为mipmap主要使用在纹理被缩小的情况下的：纹理放大不会使用mipmap，为mipmap设置放大过滤选项会产生一个GL_INVALID_ENUM错误码。

###加载和创建纹理

使用纹理之前要做的第一件事是把它们加载到应用中。纹理图像可能储存为各种各样的格式，每种都有自己的数据结构和排列，所以我们如何才能把这些图像加载到应用中呢？一个解决方案是写一个我们自己的某种图像格式加载器比如.PNG，用它来把图像转化为byte序列。写自己的图像加载器虽然不难，但是仍然挺烦人的，而且如果要支持更多文件格式呢？你就不得不为每种你希望支持的格式写加载器了。

另一个解决方案是，也许是更好的一种选择，就是使用一个支持多种流行格式的图像加载库，来为我们解决这个问题。就像SOIL这种库①。

###SOIL

SOIL代表Simple OpenGL Image Library（简易OpenGL图像库），它支持大多数流行的图像格式，使用起来也很简单，可以从他们的主页下载。像大多数其他库一样，你必须自己生成.lib。可以使用/projects文件夹里的solution文件（不用但系他们的visual studio版本太老，你可以把它们转变为新的版本；这总是可行的。译注：用VS2010的时候，你要用VC8而不是VC9的solution，想必更高版本的情况亦是如此），也可以使用CMake你自己生成。还要添加src文件夹到你的includes文件夹；不要忘记添加SOIL.lib到你的连接器选项，添加#include 到你的代码上部。

下面的纹理部分，我们会使用一张木箱的图片。使用SOIL加载一个图片，我们使用它的SOIL_load_image函数：

```c++
int width, height;
unsigned char* image = SOIL_load_image(“container..jpg”, &width, &height, 0, SOIL_LOAD_RGB);
```
函数首先需要输入图片文件的路径。然后需要两个int作为第二个和第三个参数，SOIL会返回图片的宽度和高度到其中。之后，我们需要图片的宽度和高度来生成纹理。第四个参数指定图片的通道（channel）数量，但是这里我们只留0。最后一个参数告诉SOIL如何来加载图片：我们只对图片的RGB感兴趣。结果储存为一个大的char/byte数组。

生成一个纹理和OpenGL前面的对象一样，纹理也是使用ID引用；我们就创建一个：

```c++
GLuint texture;
glGenTextures(1, &texture);
```
glGenTextures函数首先需要输入纹理生成的数量，然后把它们储存在第二个参数的GLuint数组中（我们的例子里只有一个GLuint），就像其他对象一样，我们需要绑定它，所以下面的纹理命令会配置当前绑定的纹理：

```c++
glBindTexture(GL_TEXTURE_2D, texture);
```

现在纹理绑定了，我们可以使用前面载入的图片数据生成纹理了，纹理通过glTexImage2D来生成：

```c++
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image);
glGenerateMipmap(GL_TEXTURE_2D);
```

函数很长，参数不少，所以我们一个一个地讲解：

* 第一个参数指定纹理目标（环境）；设置为GL_TEXTURE_2D意味着会生成与当前绑定的纹理对象在同一个目标（target）上的纹理（任何绑定到GL_TEXTURE_1D和GL_TEXTURE_3D的纹理不会受到影响）。
* 第二个参数为我们打算创建的纹理指定mipmap层级，如果你希望为每个mimap层级单独手工设置的话。这里我们填0基本级。
* 第三个参数告诉OpenGL，我们希望把纹理储存为何种格式。我们的图像只有RGB值，因此我们把纹理储存为RGB值。
* 第四个和第五个参数设置最终的纹理的宽度和高度。我们加载图像的时候提前储存它们这样我们就能使用相应变量了。
下个参数应该一直被设为0（遗留问题）。
* 第七第八个参数定义了源图的格式和数据类型。我们使用RGB值加载这个图像，并把它们储存在char(byte)，我们将会传入相应值。
* 最后一个参数是真实的图像数据。

当调用glTexImage2D，当前绑定的纹理对象就会被附加上纹理图像。然而，当前只有基本级别（base-level）纹理图像加载了，如果要使用mipmap，我们必须手工设置不同的图像（通过不断把第二个参数增加的方式）或者，在生成纹理之后调用glGenerateMipmap。这会为当前绑定的纹理自动生成所有需要的mipmap。

生成了纹理和相应的mipmap后，解绑纹理对象、释放图像的内存很重要。

```c++
SOIL_free_image_data(image);
glBindTexture(GL_TEXTURE_2D, 0);
```

生成一个纹理的过程应该看起来像这样：

```c++
GLuint texture;
glGenTextures(1, &texture);
glBindTexture(GL_TEXTURE_2D, texture);
// Set the texture wrapping/filtering options (on the currently bound texture object)
...
// Load and generate the texture
int width, height;
unsigned char * image = SOIL_load_image("container.jpg", &width, &eight, 0, SOIL_LOAD_RGB);
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image);
glGenerateMipmap(GL_TEXTURE_2D);
SOIL_free_image_data(image);
glBindTexture(GL_TEXTURE_2D, 0);
```

###应用纹理

后面的部分我们会使用glDrawElements绘制Hello Triangle教程的最后一部分的矩形。我们下需要告知OpenGL如何采样纹理，这样我们必须更新顶点纹理坐标数据：

```c++
GLfloat vertices[] = {
    // 位置             // 颜色     // 纹理坐标
    0.5f, 0.5f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f, 1.0f, // 右上
    0.5f, -0.5f, 0.0f, 0.0f, 1.0f, 0.0f, 1.0f, 0.0f, // 右下
    -0.5f, -0.5f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, // 左下
    -0.5f, 0.5f, 0.0f, 1.0f, 1.0f, 0.0f, 0.0f, 1.0f // 左上
};
```

由于我们添加了一个额外的顶点属性，我们必须通知OpenGL新的顶点格式：

![](http://learnopengl.com/img/getting-started/vertex_attribute_pointer_interleaved_textures.png)

```c++
glVertexAttribPointer(2, 2, GL_FLOAT,GL_FALSE, 8 * sizeof(GLfloat), (GLvoid*)(6 * sizeof(GLfloat)));
glEnableVertexAttribArray(2);  
```

注意，我们必须修正前面两个顶点属性的步长参数为8*sizeof(GLfloat)。

接着我们需要让顶点着色器把纹理坐标作为一个顶点属性，把坐标传给片段着色器：

```c++
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec2 texCoord;
out vec3 ourColor;
out vec2 TexCoord;
void main()
{
    gl_Position = vec4(position, 1.0f);
    ourColor = color;
    TexCoord = texCoord;
}
```
片段色器应该把输出变量TexCoord作为输入变量。

片段着色器应该也获取纹理对象，但是我们怎样把纹理对象传给片段着色器？GLSL有一个内建数据类型，供纹理对象使用，叫做采样器（sampler），它以纹理类型作为后缀，比如sampler1D、sampler3D，在我们的例子中它是sampler2D。我们可以简单的声明一个uniform sampler2D把一个纹理传到片段着色器中，稍后我们把我们的纹理赋值给这个uniform。

```c++
#version 330 core
in vec3 ourColor;
in vec2 TexCoord;
out vec4 color;
uniform sampler2D ourTexture;
void main()
{
    color = texture(ourTexture, TexCoord);
}
```
我们使用GLSL的内建texture函数来采样纹理的颜色，它第一个参数是纹理采样器，第二个参数是相应的纹理坐标。texture函数使用前面设置的纹理参数对相应颜色值进行采样。这个片段着色器的输出就是纹理的（插值）纹理坐标上的（过滤）颜色。

现在要做的就是在调用glDrawElements之前绑定纹理，它会自动把纹理赋值给片段着色器的采样器：

```c++
glBindTexture(GL_TEXTURE_2D, texture);
glBindVertexArray(VAO);
glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
glBindVertexArray(0);
```
如果你每件事都做对了，你会看到下面的图像：

![](http://learnopengl.com/img/getting-started/textures2.png)

如果你的矩形是全黑或全白的你可能在哪儿做出了什么。检查你的着色器日志，尝试对比应用源码。

我们还可以把纹理颜色和顶点颜色混合，来获得有趣的效果。我们简单的把纹理颜色与顶点颜色在片段着色器中相乘来混合二者的颜色：

```c++
color = texture(ourTexture, TexCoord) * vec4(ourColor, 1.0f);
```

最终的效果应该是顶点颜色和纹理颜色的混合色：

![](http://learnopengl.com/img/getting-started/textures_funky.png)

这个箱子看起来有点70年代迪斯科风格。

###纹理单元

你可能感到奇怪为什么sampler2D是个uniform变量，你却不用glUniform给它赋值，使用glUniform1i我们就可以给纹理采样器确定一个位置，这样的话我们能够一次在一个片段着色器中设置多纹理。一个纹理的位置通常称为一个纹理单元。一个纹理的默认纹理单元是0，它是默认激活的纹理单元，所以教程前面部分我们不用给它确定一个位置。

纹理单元的主要目的是让我们在着色器中可以使用多于一个的纹理。通过把纹理单元赋值给采样器，我们可以一次绑定多纹理，只要我们首先激活相应的纹理单元。就像glBindTexture一样，我们可以使用glActiveTexture激活纹理单元，传入我们需要使用的纹理单元：

```c++
glActiveTexture(GL_TEXTURE0); //在绑定纹理之前，先激活纹理单元
glBindTexture(GL_TEXTURE_2D, texture);
```

激活纹理单元之后，接下来glBindTexture调用函数，会绑定这个纹理到当前激活的纹理单元，纹理单元GL_TEXTURE0总是默认被激活，所以我们在前面的例子里当我们使用glBindTexture的时候，无需激活任何纹理单元。

!!! Important

        OpenGL至少提供16个纹理单元供你使用，也就是说你可以激活GL_TEXTURE0到GL_TEXTRUE15。它们都是顺序定义的，所以我们也可以通过GL_TEXTURE0+8的方式获得GL_TEXTURE8，这个例子在当我们不得不循环几个纹理的时候变得很有用。
        
我们仍然要编辑片段着色器来接收另一个采样器。方法现在相对简单了：

```c++
#version 330 core
...
uniform sampler2D ourTexture1;
uniform sampler2D ourTexture2;
void main()
{
    color = mix(texture(ourTexture1, TexCoord), texture(ourTexture2, TexCoord), 0.2);
}
```

最终输出颜色现在结合了两个纹理查找。GLSL的内建mix函数需要两个参数将根据第三个参数为前两者作为输入，并在之间进行线性插值。如果第三个值是0.0，它返回第一个输入；如果是1.0，就返回第二个输入值。0.2返回80%的第一个输入颜色和20%的第二个输入颜色，返回两个纹理的混合。

我们现在需要载入和创建另一个纹理；我们应该对这些步骤感到熟悉了。确保创建另一个纹理对象，载入图片，使用glTexImage2D生成最终纹理。对于第二个纹理我们使用一张你学习OpenGL时的表情图片。

为了使用第二个纹理（也包括第一个），我们必须改变一点渲染流程，先绑定两个纹理到相应的纹理单元，然后定义哪个uniform采样器对应哪个纹理单元：
```c++
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, texture1);
glUniform1i(glGetUniformLocation(ourShader.Program, “ourTexture1”), 0);
glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, texture2);
glUniform1i(glGetUniformLocation(ourShader.Program, “ourTexture2”), 1);
 
glBindVertexArray(VAO);
glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_IN, 0);
glBindVertexArray(0);
```
注意，我们使用了glUniform1i设置uniform采样器的位置或曰纹理单元。通过glUniform1i的设置，我们保证了每个uniform采样器对应于合适的纹理单元。可以获得下面的结果：

![](http://learnopengl.com/img/getting-started/textures_combined.png)

你可能注意到纹理上下颠倒了！这是因为OpenGL要求y轴0.0坐标是在图片的下面的，但是图片通常y轴0.0坐标在上面。一些图片加载器比如DevIL在加载的时候有选项重置y原点，但是SOIL没有。SOIL有一个叫做SOIL_load_OGL_texture函数可以使用一个叫做SOIL_FLAG_INVERT_Y的标记加载和生成纹理，它用来解决我们的问题。不过这个函数在现代OpenGL中的这个特性失效了，所以现在我们必须坚持使用SOIL_load_image，自己做纹理生成。

所以修复我们的小问题，有两个选择：

1. 我们切换顶点数据的纹理坐标，翻转y值（用1减去y坐标）。
2. 我们可以编辑顶点着色器来翻转y坐标，自动替换TexCoord赋值：TexCoord = vec2(texCoord.x, 1 – texCoord.y);

!!! Attention

        这个提供的解决方案对图片翻转进行了一点hack。大多数情况都能工作，但是仍然执行起来以来纹理，所以最好的解决方案是换一个图片加载器，或者以一种y原点符合OpenGL需求的方式编辑你的纹理图像。
        
如果你编辑了顶点数据，在顶点着色器中翻转了y坐标，你会得到下面的结果：

![](http://learnopengl.com/img/getting-started/textures_combined2.png)

7.8 练习
纹理更熟练地使用纹理，建议在继续下面的学习之间做完这些练习：

Make sure only the happy face looks in the other/reverse direction by changing the fragment
shader: solution.

Experiment with the different texture wrapping methods by specifying texture coordinates in the range 0.0f to 2.0f instead of 0.0f to 1.0f . See if you can display 4 smiley faces on a single container image clamped at its edge: solution, result. See if you can experiment with other wrapping methods as well.

Try to display only the center pixels of the texture image on the rectangle in such a way that the individual pixels are getting visible by changing the texture coordinates. 

Try to set the texture filtering method to GL_NEAREST to see the pixels more clearly: solution.

Use a uniform variable as the mix function’s third parameter to vary the amount the two textures are visible. Use the up and down arrow keys to change how much the container or the smiley face is visible: solution, fragment shader.

---
①译注：SOIL不推荐使用，这个库很久没有更新过，可以试试FreeImage。