本文作者JoeyDeVries，由[codeman001](https://github.com/codeman001)翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/Shaders)

##着色器

在[Hello Triangle](https://github.com/Geequlim/LearnOpenGL-CN/blob/master/01%20Getting%20started/04%20Hello%20Triangle.md) 中已经提到，着色器是在GPU上运行的小程序，这些程序负责处理图形渲染管线的特定阶段，简单来说，着色器也是一个处理输入输出的程序。着色器是非常孤立执行的程序，彼此之间没有太多的交互，

在前面的教程中，我们大致介绍了表面着色器和如何正确使用它们。接下来我们讲接触更加流行的OpenGL着色语言

###GLSL
GLSL是写法类似C语言，GLSL是专门针对图形以及向量和矩阵变化设计的。着色器通常开始生命一个版本信息，然后是输入、输出列表以及常量和入口函数（main函数），每个着色器都是在入口函数处来处理输入参数。然后输出结果。


着色器通常具有以下结构：
```c++
#version version_number
  
in type in_variable_name;
in type in_variable_name;

out type out_variable_name;
  
uniform type uniform_name;
  
int main()
{
  // Process input(s) and do some weird graphics stuff
  ...
  // Output processed stuff to output variable
  out_variable_name = weird_stuff_we_processed;
}
```

所谓的顶点着色器就讲顶点属性作为输入的着色器，顶点属性的个数主要受限于硬件实现，OpenGL的保证总有至少16个四分量的顶点可以使用，但是硬件可能个多些，可以通过查询：**GL_MAX_VERTEX_ATTRIBS**
```c++
GLint nrAttributes;
glGetIntegerv(GL_MAX_VERTEX_ATTRIBS, &nrAttributes);
std::cout << "Maximum nr of vertex attributes supported: " << nrAttributes << std::endl;
```

这个结果最小返回16，一般情况下使用。

###类型


GLSL跟一般的编程语言一样，定义了一些常用的数据类型，基础类型比如：int,float, double, uint and bool等，还用两种我们在教程中经常用到的容器类型：vectors(向量) 和 matrices（矩阵），稍后会提到。


####向量
一个向量可以包含1-4个分量，分量的类型可以是上面我们提到的基础类型。向量个类型名字规则如下：

- vecn: 默认向量，有个n浮点型分量.
- bvecn: 有n个bool分量.
- ivecn: 有n个整型分量.
- uvecn: 有n个无符号整型分量.
- dvecn: 有n个双浮点型分量.

大多数情况下我们使用vecn，因为浮点型足够满足我们大多数需求。
向量的分量可以通过vec.x来访问第一个分量，同时可以使用.x,.y,.z,.w来访问一个向量的四个成员，同样可以使用rgba来访问颜色值对应的向量，纹理坐标则可以使用stpq来访问分量的值。
向量的访问方式支持趣味性和扩展性，被称为交叉混合性，实例如下：
```c++
vec2 someVec;
vec4 differentVec = someVec.xyxx;
vec3 anotherVec = differentVec.zyw;
vec4 otherVec = someVec.xxxx + anotherVec.yxzy;
```
可以使用任意组合来组成新向量，同时也可以把维度小的向量放在高纬度向量的构造函数里来构成新的向量。如下代码：
```c++
vec2 vect = vec2(0.5f, 0.7f);
vec4 result = vec4(vect, 0.0f, 0.0f);
vec4 otherResult = vec4(result.xyz, 1.0f);
```
###输入和输出
着色器是运行在GPU上的小程序，但是麻雀虽小五脏俱全，也会有输入和输出来构成完整的程序，GLSL使用in和out关键字来定义输入和输出。每个着色器可以是这些关键字来指定输入和输出，输入变量经过处理以后会得到适合下个处理阶段可以使用的输出变量，顶点着色器和片段着色器有点小却别。

顶点着色器接受特定格式的输入，否则不能正确使用。顶点着色器直接接受输入的顶点数据，但是需要在CPU一边指定数据的对应的位置，前面的教程可以到对位置0的输入（location=0），所以顶点着色器需要一个特定的声明来确定CPU和GPU数据对应关联关系，

<div style="border:solid #AFDFAF;border-radius:5px;background-color:#D8F5D8;margin:20px 20px 20px 0px;padding:15px">
也可以使用*glGetAttribLocation*来查询对应的位置，这样可以省略layout的声明，但是我觉得可以是用layout声明比较好，这也可以减少GPU的一些工作
</div>


对于片段着色器有个vec4的颜色作为特定的输出，因为片段处理后最终是要生产一个颜色来显示的。否则将输出黑色或白色颜色作为输出。

如果我们想从一个着色器向另外一个发送数据，我们需要在发送方定义一个输出，然后再接收方顶一个输入，同时保证这两个变量类型和名字是相同的。
下面是一个实例来展示如何从顶点着色器传递一个颜色值跟片段着色器使用：

***顶点着色器***
```c++
#version 330 core
layout (location = 0) in vec3 position; // The position variable has attribute position 0
  
out vec4 vertexColor; // Specify a color output to the fragment shader

void main()
{
    gl_Position = vec4(position, 1.0); // See how we directly give a vec3 to vec4's constructor
    vertexColor = vec4(0.5f, 0.0f, 0.0f, 1.0f); // Set the output variable to a dark-red color
}
```
***片段着色器***
```c++
#version 330 core
in vec4 vertexColor; // The input variable from the vertex shader (same name and same type)
  
out vec4 color;

void main()
{
    color = vertexColor;
}
```
可以看到在顶点着色器生命了一个向量：*vertexColor* 有out修饰，同时在片段着色器声明了一个*vertexColor* 使用in来修饰，这样片段着色器就可以获取顶点着色器处理的*vertexColor*的结果了。
根据上面shader，可以得出下图的效果：

![shader效果](https://raw.githubusercontent.com/LearnOpenGL-CN/LearnOpenGL-CN/master/img/shaders1.jpg)


**常量**
常量是另外一个中从CPU端向GPU传输数据的方式，常量方式跟顶点数据有非常明显的不同。常量有两个特性：

1.具有全局性，可以在着色器不同阶段来获取同一个常量

2.不变性，一旦设置了值，在渲染过程中就不能被改变，只有从新设置才能改变。

声明常量非常简单使用uniform 放在类型和变量名前面即可。下面看一个例子：
```c++
#version 330 core
  
out vec4 color;
  
uniform vec4 ourColor; // We set this variable in the OpenGL code.

void main()
{
    color = ourColor;
}
```
声明了一个ourColor为常量类型，然后把它的值付给了输出变量color。
<div style="border:solid #E1B3B3;border-radius:10px;background-color:#FFD2D2;margin:10px 10px 10px 0px;padding:10px">
注意：如果声明了一个从来没用到常量，GLSL的编译器会默认删除这个常量，由此可能导致一些莫名的问题。
</div>
现在这个常量还是个空值，接下来给ourColor在CPU端传递数据给它。思路：获取ourColor在索引位置，然后传递数据给这个位置。另外做一些小动作，不传递固定的这个，传递一个随时间变化的值，如下：
```c++
GLfloat timeValue = glfwGetTime();
GLfloat greenValue = (sin(timeValue) / 2) + 0.5;
GLint vertexColorLocation = glGetUniformLocation(shaderProgram, "ourColor");
glUseProgram(shaderProgram);
glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 1.0f);
```
首先通过glfwGetTime函数获取程序运行时间（秒数）。然后使用sin函数将greenValue的值控制在0-1。

然后使用glGetUniformLocation函数查询ourColor的索引位置。是一个参数是要查询的着色器程序，第二个参数是常量在着色器中声明的变量名。如果glGetUniformLocation函数返回-1，表明没找到对应的常量的索引位置。

最合使用glUniform4f来完成赋值。

注意：使用glGetUniformLocation 不需要在glUseProgram之后，但是glUniform4f一定要在lUseProgram之后，因为我们也只能对当前激活的着色器程序传递数据。
到目前为止已经学会了这么给常量传递数据和渲染使用这些数据，如果我们想每帧改变常量的值，我们需要在主循环的不停的计算和更新常量的值。
```c++
while(!glfwWindowShouldClose(window))
{
    // Check and call events
    glfwPollEvents();

    // Render
    // Clear the colorbuffer
    glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);

    // Be sure to activate the shader
    glUseProgram(shaderProgram);
  
    // Update the uniform color
    GLfloat timeValue = glfwGetTime();
    GLfloat greenValue = (sin(timeValue) / 2) + 0.5;
    GLint vertexColorLocation = glGetUniformLocation(shaderProgram, "ourColor");
    glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 1.0f);

    // Now draw the triangle
    glBindVertexArray(VAO);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    glBindVertexArray(0);
}
```
如果运行正常的话我们能看到一个绿色到黑色，黑色到绿色变化的三角形，
可以查看完整的代码[实例](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-interpolated)


**着色器程序管理程序**

编写、编译和管理着色器程序是非常繁重的工作，为了减轻这个工作量我们自己定义一个着色器程序管理器，负责读取着色器程序文件，然后编译他们，链接并检查着色器程序有无错误发生。这也可以让我们把已经学到的知识封装到抽象的对象里。

我们首先顶一个着色器程序的头文件，如下：
```c++
#ifndef SHADER_H
#define SHADER_H

#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
using namespace std;
  
#include <GL/glew.h>; // Include glew to get all the required OpenGL headers

class Shader
{
public:
  	// The program ID
	GLuint Program;
	// Constructor reads and builds the shader
	Shader(const GLchar* vertexSourcePath, const GLchar* fragmentSourcePath);
  	// Use the program
  	void Use();
};
  
#endif
```
着色器程序类包含一个着色器程序ID，有一个接受顶点和片段程序的接口，这个两个路径就是普通的文本文件就可以了。
Use函数是一个工具属性的函数，主要是控制当前着色器程序是否激活。

读取着色器程序文件
```c++
Shader(const GLchar* vertexPath, const GLchar* fragmentPath)
{
    // 1. Retrieve the vertex/fragment source code from filePath
    std::string vertexCode;
    std::string fragmentCode;
    std::ifstream vShaderFile;
    std::ifstream fShaderFile;
    // ensures ifstream objects can throw exceptions:
    vShaderFile.exceptions (std::ifstream::failbit | std::ifstream::badbit);
    fShaderFile.exceptions (std::ifstream::failbit | std::ifstream::badbit);
    try 
    {
        // Open files
        vShaderFile.open(vertexPath);
        fShaderFile.open(fragmentPath);
        std::stringstream vShaderStream, fShaderStream;
        // Read file's buffer contents into streams
        vShaderStream << vShaderFile.rdbuf();
        fShaderStream << fShaderFile.rdbuf();		
        // close file handlers
        vShaderFile.close();
        fShaderFile.close();
        // Convert stream into GLchar array
        vertexCode = vShaderStream.str();
        fragmentCode = fShaderStream.str();		
    }
    catch(std::ifstream::failure e)
    {
        std::cout << "ERROR::SHADER::FILE_NOT_SUCCESFULLY_READ" << std::endl;
    }
    const GLchar* vShaderCode = vertexCode.c_str();
    const GLchar* fShaderCode = fragmentCode.c_str();
    [...]
```

接下来编译和链接这些程序，同时收集一些编译和链接的错误，来帮助我们调试。
```c++
// 2. Compile shaders
GLuint vertex, fragment;
GLint success;
GLchar infoLog[512];
   
// Vertex Shader
vertex = glCreateShader(GL_VERTEX_SHADER);
glShaderSource(vertex, 1, &vShaderCode, NULL);
glCompileShader(vertex);
// Print compile errors if any
glGetShaderiv(vertex, GL_COMPILE_STATUS, &success);
if(!success)
{
    glGetShaderInfoLog(vertex, 512, NULL, infoLog);
    std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
};
  
// Similiar for Fragment Shader
[...]
  
// Shader Program
this->Program = glCreateProgram();
glAttachShader(this->Program, vertex);
glAttachShader(this->Program, fragment);
glLinkProgram(this->Program);
// Print linking errors if any
glGetProgramiv(this->Program, GL_LINK_STATUS, &success);
if(!success)
{
    glGetProgramInfoLog(this->Program, 512, NULL, infoLog);
    std::cout << "ERROR::SHADER::PROGRAM::LINKING_FAILED\n" << infoLog << std::endl;
}
  
// Delete the shaders as they're linked into our program now and no longer necessery
glDeleteShader(vertex);
glDeleteShader(fragment);
```
最后来实现一个use函数
	
	void Use() { glUseProgram(this->Program); }
接下来是一个使用这个简单实例：
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
上面我们已经把顶点着色器和片段着色器代码分别放在shader.vs和shader.frag里面了，这些文件的名字和后缀名都可以随意命名的，只要符合文件名规范就好。
完整的代码实例：

[使用的实例](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-using-object)

[着色器类](http://learnopengl.com/code_viewer.php?type=header&code=shader)

[顶点着色器代码](http://learnopengl.com/code_viewer.php?type=vertex&code=getting-started/basic)

[片段着色器代码](http://learnopengl.com/code_viewer.php?type=fragment&code=getting-started/basic)


**练习题**

1.通过调整的顶点着色器，以使三角形是倒置 [答案](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise1)

2.通过一个常量，使得三角在x方向偏移 [答案](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise2)

3.使用in 和out 关键字，把顶点着色器的位置数据作为片段着色器的颜色，然后看看得出的三角形颜色，进一步理解差值的问题，同时可以尝试回答下面的问题：为什么我们三角形左下侧有黑边?:[答案](http://learnopengl.com/code_viewer.php?code=getting-started/shaders-exercise3)


