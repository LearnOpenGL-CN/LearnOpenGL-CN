# 着色器(Shaders)

原文     | [Shaders](http://learnopengl.com/#!Getting-started/Shaders)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | Geequlim

在[Hello Triangle](http://learnopengl-cn.readthedocs.org/zh/latest/01%20Getting%20started/04%20Hello%20Triangle/)教程中提到，着色器是运行在GPU上的小程序。这些小程序为图形渲染管线的一个特定部分而运行。从基本意义上来说，着色器不是别的，只是一种把输入转化为输出的程序。着色器也是一种相当独立的程序，它们不能相互通信；只能通过输入和输出的方式来进行沟通。

前面的教程里我们简要地触及了一点着色器的皮毛。了解了如何恰当地使用它们。现在我们会用一种更加通用的方式详细解释着色器，特别是OpenGL着色器语言。

## GLSL

着色器是使用一种叫GLSL的类C语言写成的。GLSL是为图形计算量身定制的，它包含针对向量和矩阵操作的有用特性。

着色器的开头总是要声明版本，接着是输入和输出变量、uniform和`main`函数。每个着色器的入口都是`main`函数，在这里我们处理所有输入变量，用输出变量输出结果。如果你不知道什么是uniform也不用担心，我们后面会进行讲解。

一个典型的着色器有下面的结构：

```c++
#version version_number

in type in_variable_name;
in type in_variable_name;

out type out_variable_name;

uniform type uniform_name;

int main()
{
  // 处理输入
  ...
  // 输出
  out_variable_name = weird_stuff_we_processed;
}
```

当我们谈论特别是谈到顶点着色器的时候，每个输入变量也叫顶点属性(Vertex Attribute)。能声明多少个顶点属性是由硬件决定的。OpenGL确保至少有16个包含4个元素的顶点属性可用，但是有些硬件或许可用更多，你可以查询`GL_MAX_VERTEX_ATTRIB`S来获取这个数目。

```c++
GLint nrAttributes;
glGetIntegerv(GL_MAX_VERTEX_ATTRIBS, &nrAttributes);
std::cout << "Maximum nr of vertex attributes supported: " << nrAttributes << std::endl;
```

通常情况下它会返回至少16个，大部分情况下是够用了。

## 数据类型

GLSL有像其他编程语言相似的数据类型。GLSL有C风格的默认基础数据类型：`int`、`float`、`double`、`uint`和`bool`。GLSL也有两种容器类型，教程中我们会使用很多，它们是向量(Vector)和矩阵(Matrix)，其中矩阵我们会在之后的教程里再讨论。

## 向量(Vector)

GLSL中的向量可以包含有1、2、3或者4个分量，分量类型可以是前面默认基础类型的任意一个。它们可以是下面的形式(n代表元素数量)：

  类型|含义
   ---|---
 vecn | 包含n个默认为float元素的向量
 bvecn| 包含n个布尔元素向量
 ivecn| 包含n个int元素的向量
 uvecn| 包含n个unsigned int元素的向量
 dvecn| 包含n个double元素的向量

大多数时候我们使用vecn，因为float足够满足大多数要求。

一个向量的元素可以通过`vec.x`这种方式获取，这里`x`是指这个向量的第一个元素。你可以分别使用`.x`、`.y`、`.z`和`.w`来获取它们的第1、2、3、4号元素。GLSL也允许你使用**rgba**来获取颜色的元素，或是**stpq**获取纹理坐标元素。

向量的数据类型也允许一些有趣而灵活的元素选择方式，叫做重组(Swizzling)。重组允许这样的语法：

```c++
vec2 someVec;
vec4 differentVec = someVec.xyxx;
vec3 anotherVec = differentVec.zyw;
vec4 otherVec = someVec.xxxx + anotherVec.yxzy;
```

你可以使用上面任何4个字母组合来创建一个新的和原来向量一样长的向量(但4个元素需要是同一种类型)；不允许在一个vec2向量中去获取.z元素。我们可以把一个向量作为一个参数传给不同的向量构造函数，以减少参数需求的数量：

```c++
vec2 vect = vec2(0.5f, 0.7f);
vec4 result = vec4(vect, 0.0f, 0.0f);
vec4 otherResult = vec4(result.xyz, 1.0f);
```

向量是一种灵活的数据类型，我们可以把用在所有输入和输出上。学完教程你会看到很多如何创造性地管理向量的例子。

## 输入与输出(in vs out)

着色器是各自独立的小程序，但是它们都是一个整体的局部，出于这样的原因，我们希望每个着色器都有输入和输出，这样才能进行数据交流和传递。GLSL定义了`in`和`out`关键字来实现这个目的。每个着色器使用这些关键字定义输入和输出，无论在哪儿，一个输出变量就能与一个下一个阶段的输入变量相匹配。他们在顶点和片段着色器之间有点不同。

顶点着色器应该接收的输入是一种特有形式，否则就会效率低下。顶点着色器的输入是特殊的，它所接受的是从顶点数据直接输入的。为了定义顶点数据被如何组织，我们使用`location`元数据指定输入变量，这样我们才可以在CPU上配置顶点属性。我们已经在前面的教程看过`layout (location = 0)`。顶点着色器需要为它的输入提供一个额外的`layout`定义，这样我们才能把它链接到顶点数据。

!!! Important

	也可以移除`layout (location = 0)`，通过在OpenGL代码中使用`glGetAttribLocation`请求属性地址(Location)，但是我更喜欢在着色器中设置它们，理解容易而且节省时间。

另一个例外是片段着色器需要一个`vec4`颜色输出变量，因为片段着色器需要生成一个最终输出的颜色。如果你在片段着色器没有定义输出颜色，OpenGL会把你的物体渲染为黑色(或白色)。

所以，如果我们打算从一个着色器向另一个着色器发送数据，我们必须**在发送方着色器中声明一个输出，在接收方着色器中声明一个同名输入**。当名字和类型都一样的时候，OpenGL就会把两个变量链接到一起，它们之间就能发送数据了(这是在链接程序(Program)对象时完成的)。为了展示这是这么工作的，我们会改变前面教程里的那个着色器，让顶点着色器为片段着色器决定颜色。

#### 顶点着色器

```c++
#version 330 core
layout (location = 0) in vec3 position; // 位置变量的属性为0

out vec4 vertexColor; // 为片段着色器指定一个颜色输出

void main()
{
    gl_Position = vec4(position, 1.0); // 把一个vec3作为vec4的构造器的参数
    vertexColor = vec4(0.5f, 0.0f, 0.0f, 1.0f); // 把输出颜色设置为暗红色
}
```
#### 片段着色器

```c++
#version 330 core
in vec4 vertexColor; // 和顶点着色器的vertexColor变量类型相同、名称相同

out vec4 color; // 片段着色器输出的变量名可以任意命名，类型必须是vec4

void main()
{
    color = vertexColor;
}
```

你可以看到我们在顶点着色器中声明了一个`vertexColor`变量作为`vec4`输出，在片段着色器声明了一个一样的`vertexColor`。由于它们**类型相同并且名字也相同**，片段着色器中的`vertexColor`就和顶点着色器中的`vertexColor`链接了。因为我们在顶点着色器中设置的颜色是深红色的，片段着色器输出的结果也是深红色的。下面的图片展示了输出结果：

![](http://learnopengl.com/img/getting-started/shaders.png)

我们完成了从顶点着色器向片段着色器发送数据。让我们更上一层楼，看看能否从应用程序中直接给片段着色器发送一个颜色！

## Uniform

uniform是另一种从CPU应用向GPU着色器发送数据的方式，但uniform和顶点属性有点不同。首先，uniform是**全局的(Global)**。这里全局的意思是uniform变量必须在所有着色器程序对象中都是独一无二的，它可以在着色器程序的任何着色器任何阶段使用。第二，无论你把uniform值设置成什么，uniform会一直保存它们的数据，直到它们被重置或更新。

我们可以简单地通过在片段着色器中设置uniform关键字接类型和变量名来声明一个GLSL的uniform。之后，我们可以在着色器中使用新声明的uniform了。我们来看看这次是否能通过uniform设置三角形的颜色：

```c++
#version 330 core
out vec4 color;

uniform vec4 ourColor; //在程序代码中设置

void main()
{
    color = ourColor;
}  
```

我们在片段着色器中声明了一个uniform vec4的`ourColor`，并把片段着色器的输出颜色设置为uniform值。因为uniform是全局变量，我们我们可以在任何着色器中定义它们，而无需通过顶点着色器作为中介。顶点着色器中不需要这个uniform所以不用在那里定义它。

!!! Attention

	如果你声明了一个uniform却在GLSL代码中没用过，编译器会静默移除这个变量，从而最后编译出的版本中并不会包含它，如果有一个从没用过的uniform出现在已编译版本中会出现几个错误，记住这点！

uniform现在还是空的；我们没有给它添加任何数据，所以下面就做这件事。我们首先需要找到着色器中uniform的索引/地址。当我们得到uniform的索引/地址后，我们就可以更新它的值了。这里我们不去给像素传递一个颜色，而是随着时间让它改变颜色：

```c++
GLfloat timeValue = glfwGetTime();
GLfloat greenValue = (sin(timeValue) / 2) + 0.5;
GLint vertexColorLocation = glGetUniformLocation(shaderProgram, "ourColor");
glUseProgram(shaderProgram);
glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 1.0f);
```

首先我们通过`glfwGetTime()`获取运行的秒数。然后我们使用余弦函数在0.0到-1.0之间改变颜色，最后储存到`greenValue`里。

接着，我们用`glGetUniformLocation`请求`uniform ourColor`的地址。我们为请求函数提供着色器程序和uniform的名字(这是我们希望获得的地址的来源)。如果`glGetUniformLocation`返回`-1`就代表没有找到这个地址。最后，我们可以通过`glUniform4f`函数设置uniform值。注意，查询uniform地址不需要在之前使用着色器程序，但是更新一个unform之前**必须**使用程序(调用`glUseProgram`)，因为它是在当前激活的着色器程序中设置unform的。

!!! Important

	因为OpenGL是C库内核，所以它不支持函数重载，在函数参数不同的时候就要定义新的函数；glUniform是一个典型例子。这个函数有一个特定的作为类型的后缀。有几种可用的后缀：

    后缀|含义
     ---|--
	  f | 函数需要以一个float作为它的值
	  i | 函数需要一个int作为它的值
	  ui| 函数需要一个unsigned int作为它的值
	  3f| 函数需要3个float作为它的值
	  fv| 函数需要一个float向量/数组作为它的值

    每当你打算配置一个OpenGL的选项时就可以简单地根据这些规则选择适合你的数据类型的重载的函数。在我们的例子里，我们使用uniform的4float版，所以我们通过`glUniform4f`传递我们的数据(注意，我们也可以使用fv版本)。

现在你知道如何设置uniform变量的值了，我们可以使用它们来渲染了。如果我们打算让颜色慢慢变化，我们就要在游戏循环的每一帧更新这个uniform，否则三角形就不会改变颜色。下面我们就计算greenValue然后每个渲染迭代都更新这个uniform：

```c++
while(!glfwWindowShouldClose(window))
{
    // 检测事件
    glfwPollEvents();

    // 渲染
    // 清空颜色缓冲
    glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);

    // 激活着色器
    glUseProgram(shaderProgram);

    // 更新uniform颜色
    GLfloat timeValue = glfwGetTime();
    GLfloat greenValue = (sin(timeValue) / 2) + 0.5;
    GLint vertexColorLocation = glGetUniformLocation(shaderProgram, "ourColor");
    glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 1.0f);

    // 绘制三角形
    glBindVertexArray(VAO);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    glBindVertexArray(0);
}
```

新代码和上一节的很相似。这次，我们在每个循环绘制三角形前先更新uniform值。如果你成功更新uniform了，你会看到你的三角形逐渐由绿变黑再变绿。

<video src="http://learnopengl.com/video/getting-started/shaders.mp4" controls="controls"/></video>

如果你在哪儿卡住了，[这里有源码](http://www.learnopengl.com/code_viewer.php?code=getting-started/shaders-uniform)。

就像你所看到的那样，uniform是个设置属性的很有用的工具，它可以在渲染循环中改变，也可以在你的应用和着色器之间进行数据交互，但假如我们打算为每个顶点设置一个颜色的时候该怎么办？这种情况下，我们就不得不声明和顶点数目一样多的uniform了。在顶点属性问题上一个更好的解决方案一定要能包含足够多的数据，这是我们接下来要讲的内容。

## 更多属性

前面的教程中，我们了解了如何填充VBO、配置顶点属性指针以及如何把它们都储存到VAO里。这次，我们同样打算把颜色数据加进顶点数据中。我们将把颜色数据表示为3个float的**顶点数组(Vertex Array)**。我们为三角形的每个角分别指定为红色、绿色和蓝色：

```c++
GLfloat vertices[] = {
    // 位置                 // 颜色
     0.5f, -0.5f, 0.0f,  1.0f, 0.0f, 0.0f,   // 右下
    -0.5f, -0.5f, 0.0f,  0.0f, 1.0f, 0.0f,   // 左下
     0.0f,  0.5f, 0.0f,  0.0f, 0.0f, 1.0f    // 顶部
};
```

由于我们现在发送到顶点着色器的数据更多了，有必要调整顶点着色器，使它能够把颜色值作为一个顶点属性输入。需要注意的是我们用`layout`标识符来吧`color`属性的`location`设置为1：

```c++
#version 330 core
layout (location = 0) in vec3 position; // 位置变量的属性position为 0 
layout (location = 1) in vec3 color;	// 颜色变量的属性position为 1

out vec3 ourColor; // 向片段着色器输出一个颜色

void main()
{
    gl_Position = vec4(position, 1.0);
    ourColor = color; // 把ourColor设置为我们从顶点数据那里得到的输入颜色
}
```

由于我们不再使用uniform来传递片段的颜色了，现在使用的`ourColor`输出变量要求必须也去改变片段着色器：

```c++
#version 330 core
in vec3 ourColor
out vec4 color;
void main()
{
    color = vec4(ourColor, 1.0f);
}
```

因为我们添加了另一个顶点属性，并且更新了VBO的内存，我们就必须重新配置顶点属性指针。更新后的VBO内存中的数据现在看起来像这样：

![](http://learnopengl.com/img/getting-started/vertex_attribute_pointer_interleaved.png)

知道了当前使用的layout，我们就可以使用`glVertexAttribPointer`函数更新顶点格式，

```c++
// 顶点属性
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), (GLvoid*)0);
glEnableVertexAttribArray(0);
// 颜色属性
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), (GLvoid*)(3* sizeof(GLfloat)));
glEnableVertexAttribArray(1);
```

`glVertexAttribPointer`函数的前几个参数比较明了。这次我们配置属性location为1的顶点属性。颜色值有3个float那么大，我们不去标准化这些值。

由于我们现在有了两个顶点属性，我们不得不重新计算步长值(Stride)。为获得数据队列中下一个属性值(比如位置向量的下个x元素)我们必须向右移动6个float，其中3个是位置值，另外三个是颜色值。这给了我们6个步长的大小，每个步长都是float的字节数(=24字节)。

同样，这次我们必须指定一个偏移量(Offset)。对于每个顶点来说，位置(Position)顶点属性是先声明的，所以它的偏移量是0。颜色属性紧随位置数据之后，所以偏移量就是`3*sizeof(GLfloat)`，用字节来计算就是12字节。

运行应用你会看到如下结果：
![](http://learnopengl.com/img/getting-started/shaders3.png)

如果你有困惑，可以[在这里获得源码](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-interpolated)。

这个图片可能不是你所期望的那种，因为我们只提供3个颜色，而不是我们现在看到的大调色板。这是所谓片段着色器进行**片段插值(Fragment Interpolation)**的结果。当渲染一个三角形在像素化(Rasterization 也译为光栅化)阶段通常生成比原来的顶点更多的像素。像素器就会基于每个像素在三角形的所处相对位置决定像素的位置。

基于这些位置，它**插入(Interpolate)**所有片段着色器的输入变量。比如说，我们有一个线段，上面的那个点是绿色的，下面的点是蓝色的。如果一个片段着色器正在处理的那个片段(实际上就是像素)是在线段的70%的位置，它的颜色输入属性就会是一个绿色和蓝色的线性结合；更精确地说就是30%蓝+70%绿。

这正是这个三角形里发生的事。我们有3个顶点，和相应的3个颜色，从这个三角形的像素来看它可能包含50,000左右的像素，片段着色器为这些像素进行插值。如果你仔细看这些颜色，你会发现其中的奥秘：红到紫再到蓝。像素插值会应用到所有片段着色器的输入属性上。

## 我们自己的着色器类

编写、编译、管理着色器是件麻烦事。在着色器的最后主题里，我们会写一个类来让我们的生活轻松一点，这个类从硬盘读着色器，然后编译和链接它们，对它们进行错误检测，这就变得很好用了。这也会给你一些关于如何把我们目前所学的知识封装到一个抽象的对象里的灵感。

我们会在头文件里创建整个类，主要为了学习，也可以方便移植。我们先来添加必要的include，定义类结构：

```c++
#ifndef SHADER_H
#define SHADER_H

#include <string>
#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

#include <GL/glew.h>; // 包含glew获取所有的OpenGL必要headers

class Shader
{
public:
        // 程序ID
        GLuint Program;
        // 构造器读取并创建Shader
        Shader(const GLchar * vertexSourcePath, const GLchar * fragmentSourcePath);
        // 使用Program
        void Use();
};

#endif
```

!!! Important

	在上面，我们用了几个预处理指令(Preprocessor Directives)。这些预处理指令告知你的编译器，只在没被包含过的情况下才包含和编译这个头文件，即使多个文件都包含了这个shader头文件,它是用来防止链接冲突的。

shader类保留了着色器程序的ID。它的构造器需要顶点和片段着色器源代码的文件路径，我们可以把各自的文本文件储存在硬盘上。`Use`函数看似平常，但是能够显示这个自造类如何让我们的生活变轻松(虽然只有一点)。

### 从文件读取

我们使用C++文件流读取着色器内容，储存到几个string对象里([译注1])

```c++
Shader(const GLchar * vertexPath, const GLchar * fragmentPath)
{
    // 1. 从文件路径获得vertex/fragment源码
    std::string vertexCode;
    std::string fragmentCode;

    try {
        // 打开文件
        std::ifstream vShaderFile(vertexPath);
        std::ifstream fShaderFile(fragmentPath);

        std::stringstream vShaderStream, fShaderStream;
        // 读取文件缓冲到流
        vShaderStream << vShaderFile.rdbuf();
        fShaderStream << fShaderFile.rdbuf();

        // 关闭文件句柄
        vShaderFile.close();
        fShaderFile.close();

        // 将流转为GLchar数组
        vertexCode = vShaderStream.str();
        fragmentCode = fShaderStream.str();
    }
    catch(std::exception e)
    {
        std::cout << "ERROR::SHADER::FILE_NOT_SUCCESFULLY_READ" << std::endl;  
    }
```

下一步，我们需要编译和链接着色器。注意，我们也要检查编译/链接是否失败，如果失败，打印编译错误，调试的时候这及其重要(这些错误日志你总会需要的)：

```c++
// 2. 编译着色器
GLuint vertex, fragment;
GLint success;
GLchar infoLog[512];

// 顶点着色器
vertex = glCreateShader(GL_VERTEX_SHADER);
glShaderSource(vertex, 1, &vShaderCode, NULL);
glCompileShader(vertex);

// 打印编译时错误
glGetShaderiv(vertex, GL_COMPILE_STATUS, &success);
if(!success)
{
    glGetShaderInfoLog(vertex, 512, NULL, infoLog);
    std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
};

// 对片段着色器进行类似处理
[...]

// 着色器程序
this->Program = glCreateProgram();
glAttachShader(this->Program, vertex);
glAttachShader(this->Program, fragment);
glLinkProgram(this->Program);

// 打印连接错误
glGetProgramiv(this->Program, GL_LINK_STATUS, &success);
if(!success)
{
    glGetProgramInfoLog(this->Program, 512, NULL, infoLog);
    std::cout << "ERROR::SHADER::PROGRAM::LINKING_FAILED\n" << infoLog << std::endl;
}

// 删除着色器
glDeleteShader(vertex);
glDeleteShader(fragment);
```

最后我们也要实现Use函数：

```c++
void Use()
{
    glUseProgram(this->Program);
}
```

现在我们写完了一个完整的着色器类。使用着色器类很简单；我们创建一个着色器对象以后，就可以简单的使用了：

```c++
Shader ourShader("path/to/shaders/shader.vs", "path/to/shaders/shader.frag");
...
while(...)
{
    ourShader.Use();
    glUniform1f(glGetUniformLocation(ourShader.Program, "someUniform"), 1.0f);
    DrawStuff();
}
```

我们把顶点和片段着色器储存为两个叫做`shader.vs`和`shader.frag`的文件。你可以使用自己喜欢的名字命名着色器文件；我自己觉得用`.vs`和`.frag`作为扩展名很直观。

使用新着色器类的[程序](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-using-object)，[着色器类](http://learnopengl.com/code_viewer.php?type=header&code=shader)，[顶点着色器](http://learnopengl.com/code_viewer.php?type=vertex&code=getting-started/basic)，[片段着色器](http://learnopengl.com/code_viewer.php?type=fragment&code=getting-started/basic)。

## 练习

1. 修改顶点着色器让三角形上下颠倒：[参考解答](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise1)
2. 通过使用uniform定义一个水平偏移，在顶点着色器中使用这个偏移量把三角形移动到屏幕右侧：[参考解答](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise2)
3. 使用`out`关键字把顶点位置输出到片段着色器，把像素的颜色设置为与顶点位置相等(看看顶点位置值是如何在三角形中进行插值的)。做完这些后，尝试回答下面的问题：为什么在三角形的左下角是黑的?：[参考解答](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise3)

[译注1]: http://learnopengl-cn.readthedocs.org/zh/latest/01%20Getting%20started/05%20Shaders/#_5 "译者注：实际上把着色器代码保存在文件中适合学习OpenGL的时候，实际开发中最好把一个着色器直接储存为多个字符串，这样具有更高的灵活度。"
