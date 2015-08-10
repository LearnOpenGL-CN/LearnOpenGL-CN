# 网格(Mesh)

原文     | [Mesh](http://learnopengl.com/#!Model-Loading/Mesh)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)

使用Assimp可以把多种不同格式的模型加载到程序中，但是一旦载入，它们就都被储存为Assimp自己的数据结构。我们最终的目的是把这些数据转变为OpenGL可读的数据，才能用OpenGL来渲染物体。我们从前面的教程了解到，一个网格(Mesh)代表一个可绘制实体，现在我们就定义一个自己的网格类。

先来复习一点目前学到知识，考虑一个网格最少需要哪些数据。一个网格应该至少需要一组顶点，每个顶点包含一个位置向量，一个法线向量，一个纹理坐标向量。一个网格也应该包含一个索引绘制用的索引，以纹理（diffuse/specular map）形式表现的材质数据。

为了在OpenGL中定义一个顶点，现在我们设置有最少需求一个网格类:


```c++
struct Vertex
{
    glm::vec3 Position;
    glm::vec3 Normal;
    glm::vec2 TexCoords;
};
```

我们把每个需要的向量储存到一个叫做`Vertex`的结构体中，它被用来索引每个顶点属性。另外除了`Vertex`结构体外，我们也希望组织纹理数据，所以我们定义一个`Texture`结构体：


```c++
struct Texture
{
    GLuint id;
    String type;
};
```

我们储存纹理的id和它的类型，比如`diffuse`纹理或者`specular`纹理。

知道了顶点和纹理的实际表达，我们可以开始定义网格类的结构：


```c++
class Mesh
{
Public:
    vector<Vertex> vertices;
    vector<GLuint> indices;
    vector<Texture> textures;
    Mesh(vector<Vertex> vertices, vector<GLuint> indices, vector<Texture> texture);
    Void Draw(Shader shader);
 
private:
    GLuint VAO, VBO, EBO;
    void setupMesh();
}
```

如你所见这个类一点都不复杂，构造方法里我们初始化网格所有必须数据。在`setupMesh`函数里初始化缓冲。最后通过`Draw`函数绘制网格。注意，我们把`shader`传递给`Draw`函数。通过把`shader`传递给Mesh，在绘制之前我们设置几个uniform（就像链接采样器到纹理单元）。

构造函数的内容非常直接。我们简单设置类的公有变量，使用的是构造函数相应的参数。我们在构造函数中也调用`setupMesh`函数：


```c++
Mesh(vector<Vertex> vertices, vector<GLuint> indices, vector<Texture> textures)
{
    this->vertices = vertices;
    this->indices = indices;
    this->textures = textures;
 
    this->setupMesh();
}
```

这里没什么特别的，现在让我们研究一下`setupMesh`函数。

 
## 初始化

现在我们有一大列的网格数据可用于渲染，这要感谢构造函数。我们确实需要设置合适的缓冲，通过顶点属性指针（vertex attribute pointers）定义顶点着色器layout。现在你应该对这些概念很熟悉，但是我们我们通过介绍了结构体中使用顶点数据，所以稍微有点不一样：


```c++
void setupMesh()
{
    glGenVertexArrays(1, &this->VAO);
    glGenBuffers(1, &this->VBO);
    glGenBuffers(1, &this->EBO);
  
    glBindVertexArray(this->VAO);
    glBindBuffer(GL_ARRAY_BUFFER, this->VBO);
 
    glBufferData(GL_ARRAY_BUFFER, this->vertices.size() * sizeof(Vertex), 
                 &this->vertices[0], GL_STATIC_DRAW);  
 
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, this->EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, this->indices.size() * sizeof(GLuint), 
                 &this->indices[0], GL_STATIC_DRAW);
 
    // 设置顶点坐标指针
    glEnableVertexAttribArray(0); 
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), 
                         (GLvoid*)0);
    // 设置法线指针
    glEnableVertexAttribArray(1); 
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), 
                         (GLvoid*)offsetof(Vertex, Normal));
    // 设置顶点的纹理坐标
    glEnableVertexAttribArray(2); 
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), 
                         (GLvoid*)offsetof(Vertex, TexCoords));
 
    glBindVertexArray(0);
}
```

如你所想代码没什么特别不同的地方，在`Vertex`结构体的帮助下有了一些小把戏。

C++的结构体有一个重要的属性，那就是在内存中它们是连续的。如果我们用结构体表示一列数据，这个结构体只包含结构体的连续的变量，它就会直接转变为一个`float`（实际上是byte）数组，我们就能用于一个数组缓冲（array buffer）中了。比如，如果我们填充一个`Vertex`结构体，它在内存中的排布等于：


```c++
Vertex vertex;
vertex.Position = glm::vec3(0.2f, 0.4f, 0.6f);
vertex.Normal = glm::vec3(0.0f, 1.0f, 0.0f);
vertex.TexCoords = glm::vec2(1.0f, 0.0f);
// = [0.2f, 0.4f, 0.6f, 0.0f, 1.0f, 0.0f, 1.0f, 0.0f];
```

感谢这个有用的特性，我们能直接把一个作为缓冲数据的一大列`Vertex`结构体的指针传递过去，它们会翻译成`glBufferData`能用的参数：


```c++
glBufferData(GL_ARRAY_BUFFER, this->vertices.size() * sizeof(Vertex), 
             &this->vertices[0], GL_STATIC_DRAW);
```

自然地，`sizeof`函数也可以使用于结构体来计算字节类型的大小。它应该是32字节（8float * 4）。

一个预处理指令叫做`offsetof(s,m)`把结构体作为它的第一个参数，第二个参数是这个结构体名字的变量。这是结构体另外的一个重要用途。函数返回这个变量从结构体开始的字节偏移量（offset）。这对于定义`glVertexAttribPointer`函数偏移量参数效果很好：


```c++
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), 
                     (GLvoid*)offsetof(Vertex, Normal));
```
偏移量现在使用`offsetof`函数定义了，在这个例子里，设置法线向量的字节偏移量等于法线向量在结构体的字节偏移量，它是`3float`，也就是12字节（一个float占4字节）。注意，我们同样设置步长参数等于`Vertex`结构体的大小。

使用一个像这样的结构体，不仅能提供可读性更高的代码同时也是我们可以轻松的扩展结构体。如果我们想要增加另一个顶点属性，我们把它可以简单的添加到结构体中，由于它的可扩展性，渲染代码不会被破坏。

## 渲染

我们需要为`Mesh`类定义的最后一个函数，是它的Draw函数。在真正渲染前我们希望绑定合适的纹理，然后调用`glDrawElements`。可因为我们从一开始不知道这个网格有多少纹理以及它们应该是什么类型的，所以这件事变得很困难。所以我们该怎样在着色器中设置纹理单元和采样器呢？

解决这个问题，我们需要假设一个特定的名称惯例：每个`diffuse`纹理被命名为`texture_diffuseN`,每个`specular`纹理应该被命名为`texture_specularN`。N是一个从1到纹理才抢其允许使用的最大值之间的数。可以说，在一个网格中我们有3个`diffuse`纹理和2个`specular`纹理，它们的纹理采样器应该这样被调用：


```c++
uniform sampler2D texture_diffuse1;
uniform sampler2D texture_diffuse2;
uniform sampler2D texture_diffuse3;
uniform sampler2D texture_specular1;
uniform sampler2D texture_specular2;
```

使用这样的惯例，我们能定义我们在着色器中需要的纹理采样器的数量。如果一个网格真的有（这么多）纹理，我们就知道它们的名字应该是什么。这个惯例也使我们能够处理一个网格上的任何数量的纹理，通过定义合适的采样器开发者可以自由使用希望使用的数量（虽然定义少的话就会有点浪费绑定和uniform调用了）。

像这样的问题有很多不同的解决方案，如果你不喜欢这个方案，你可以自己创造一个你自己的方案。
最后的绘制代码：


```c++
void Draw(Shader shader) 
{
    GLuint diffuseNr = 1;
    GLuint specularNr = 1;
    for(GLuint i = 0; i < this->textures.size(); i++)
    {
        glActiveTexture(GL_TEXTURE0 + i); // 在绑定纹理前需要激活适当的纹理单元
        // 检索纹理序列号 (N in diffuse_textureN)
        stringstream ss;
        string number;
        string name = this->textures[i].type;
        if(name == "texture_diffuse")
            ss << diffuseNr++; // 将GLuin输入到string stream
        else if(name == "texture_specular")
            ss << specularNr++; // 将GLuin输入到string stream
        number = ss.str(); 
 
        glUniform1f(glGetUniformLocation(shader.Program, ("material." + name + number).c_str()), i);
        glBindTexture(GL_TEXTURE_2D, this->textures[i].id);
    }
    glActiveTexture(GL_TEXTURE0);
 
    // 绘制Mesh
    glBindVertexArray(this->VAO);
    glDrawElements(GL_TRIANGLES, this->indices.size(), GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
}
```

这不是最漂亮的代码，但是这主要归咎于C++转换类型时的丑陋，比如`int`转`string`时。我们首先计算N-元素每个纹理类型，把它链接到纹理类型字符串来获取合适的uniform名。然后查找合适的采样器位置，给它位置值对应当前激活纹理单元，绑定纹理。这也是我们需要在`Draw`方法是用`shader`的原因。我们添加`material.`到作为结果的uniform名，因为我们通常把纹理储存进材质结构体（对于每个实现也许会有不同）。

!!! Important

    注意，当我们把`diffuse`和`specular`传递到字符串流（`stringstream`）的时候，计数器会增加，在C++自增叫做：变量++，它会先返回自身然后加1，而++变量，先加1再返回自身，我们的例子里，我们先传递原来的计数器值到字符串流，然后再加1，下一轮生效。

你可以从这里得到[Mesh类的源码](http://learnopengl.com/code_viewer.php?code=mesh&type=header)。

Mesh类是对我们前面的教程里讨论的很多话题的的简洁的抽象在下面的教程里，我们会创建一个模型，它用作乘放多个网格物体的容器，真正的实现Assimp的加载接口。