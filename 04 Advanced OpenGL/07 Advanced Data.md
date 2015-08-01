## 高级数据

本文作者JoeyDeVries，由Django翻译自http://learnopengl.com

我们在OpenGL中大量使用缓冲来储存数据已经有一会儿了。有一些有趣的方式来操纵缓冲，也有一些有趣的方式通过纹理来向着色器传递大量数据。本教程中，我们会讨论一些更加有意思的缓冲函数，以及如何使用纹理对象来储存大量数据（教程中纹理部分还没写）。

OpenGL中缓冲知识一个管理一块儿内存区域的对象，除此没有更多点的了。当把缓冲绑定到一个特定缓冲对象的时候，我们就给缓冲赋予了一个特殊的意义。当我们绑定到GL_ARRAY_BUFFER的时候，这个缓冲就是一个顶点数组缓冲，我们也可以简单地绑定到GL_ELEMENT_ARRAY_BUFFER。OpenGL内部为每个目标（target）储存一个缓冲，基于目标来处理不同的缓冲。

到目前为止，我们已经使用glBufferData函数填充了缓冲对象管理的内存，这个函数分类了一块内存空间，然后把数据存入内存。如果我们向它的数据（data）这个参数传递的是NULL，只会分类内存，而不会填充它。如果我们先打算开辟一些内存，稍后回到这个缓冲一点一点的填充内存的时候很有用。

我们还可以调用glBufferSubData函数填充特定区域的缓冲，而不是一次填充整个缓冲。这个函数需要一个缓冲目标（target），一个偏移量（offset），数据的大小以及数据本身作为传参数。这个函数新的功能是我们可以给它一个偏移量（offset）来指定我们打算填充缓冲的位置与起始位置之间的偏移量。这样我们就可以插入/更新指定区域的缓冲内存空间了。一定要记住缓冲要有足够的内存分配，所以在调用glBufferSubData之前，调用glBufferData是必须的。

```c++
glBufferSubData(GL_ARRAY_BUFFER, 24, sizeof(data), &data); // 范围： [24, 24 + sizeof(data)]
```

把数据传进缓冲另一个方式是像缓冲内存请求一个指针，你自己直接把数据复制到缓冲中。调用glMapBuffer函数OpenGL会返回一个当前绑定缓冲的内存的地址，供我们操作：

```c++
float data[] = {
  0.5f, 1.0f, -0.35f
  ...
};

glBindBuffer(GL_ARRAY_BUFFER, buffer);
// Get pointer
void* ptr = glMapBuffer(GL_ARRAY_BUFFER, GL_WRITE_ONLY);
// Now copy data into memory
memcpy(ptr, data, sizeof(data));
// Make sure to tell OpenGL we're done with the pointer
glUnmapBuffer(GL_ARRAY_BUFFER);
```

调用glUnmapBuffer函数可以告诉OpenGL我们已经用完指针了，OpenGL会知道你已经做完了。通过解映射（unmapping），指针会不再可用，如果OpenGL可以把你的数据映射到缓冲上，就会返回GL_TRUE。

把数据直接映射到还冲上使用glMapBuffer很有用，因为不用把它储存在临时内存里。你可以从文件读取数据然后直接复制到缓冲的内存里。

### 分批处理顶点属性

使用glVertexAttribPointer函数我们可以指定缓冲内容的顶点数组的属性layout（布局）。顶点数组缓冲，使我们可以交叉属性；也就是说我们把每个顶点的位置、法线、纹理坐标放在彼此挨着的地方。现在我们了解了更多的缓冲的内容，我们可以采取另一种方式了。

我们可以做的是把每种类型的属性的所有向量数据批量保存在一个布局，而不是交叉布局。与交叉布局123123123123不同，我们采取批量方式111122223333。

当从文件加载顶点数据时你通常获取一个位置数组，一个法线数组和一个纹理坐标数组。需要花点力气才能把它们结合为交叉数据。使用glBufferSubData可以简单的实现分批处理方式：

```c++
GLfloat positions[] = { ... };
GLfloat normals[] = { ... };
GLfloat tex[] = { ... };
// Fill buffer
glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(positions), &positions);
glBufferSubData(GL_ARRAY_BUFFER, sizeof(positions), sizeof(normals), &normals);
glBufferSubData(GL_ARRAY_BUFFER, sizeof(positions) + sizeof(normals), sizeof(tex), &tex);
```

这样我们可以把属性数组当作一个整体直接传输给缓冲，不需要再处理它们了。我们还可以把它们结合为一个更大的数组然后使用glBufferData立即直接填充它，不过对于这项任务使用glBufferSubData是更好的选择。

我们还要更新顶点属性指针来反应这些改变：

```c++
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), 0);  
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), (GLvoid*)(sizeof(positions)));  
glVertexAttribPointer(
  2, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), (GLvoid*)(sizeof(positions) + sizeof(normals)));
```

注意，stride参数等于顶点属性的大小，由于下一个顶点属性向量可以在它的后面3（或2）的元素那儿找到。

这是我们有了另一种设置和指定顶点属性的方式。使用哪个方式对OpenGL来说也不会有立竿见影的效果，这只是一种采用更加组织化的方式去设置顶点属性。选用哪种方式取决于你的偏好和应用类型。

 ### 复制缓冲

当你的缓冲被数据填充以后，你可能打算让其他缓冲能分享这些数据或者打算把缓冲的内容复制到另一个缓冲里。glCopyBufferSubData函数让我们能够相对容易地把一个缓冲的数据复制到另一个缓冲里。函数的原型是：

```c++
void glCopyBufferSubData(GLenum readtarget, GLenum writetarget, GLintptr readoffset, GLintptr writeoffset, GLsizeiptr size);
```

readtarget和writetarget参数是复制的来源和目的的缓冲目标。例如我们可以从一个VERTEX_ARRAY_BUFFER复制到一个VERTEX_ELEMENT_ARRAY_BUFFER，各自指定源和目的的缓冲目标。当前绑定到这些缓冲目标上的缓冲会被影响到。

但如果我们打算读写的两个缓冲都是顶点数组缓冲（译注：GL_VERTEX_ARRAY_BUFFER）怎么办？我们不能把用一个缓冲目标用两次。处于这个理由，这是个例外，OpenGL给了我们另外两个缓冲目标叫做：GL_COPY_READ_BUFFER和GL_COPY_WRITE_BUFFER。这样我们就可以把我们选择的缓冲，用上面二者作为readtarget和writetarget的参数绑定到新的缓冲目标上了。

接着glCopyBufferSubData函数会从readoffset处读取的size大小的数据，写入到writetarget缓冲的writeoffset位置。下面是一个复制两个顶点数组缓冲的例子：

```c++
GLfloat vertexData[] = { ... };
glBindBuffer(GL_COPY_READ_BUFFER, vbo1);
glBindBuffer(GL_COPY_WRITE_BUFFER, vbo2);
glCopyBufferSubData(GL_COPY_READ_BUFFER, GL_COPY_WRITE_BUFFER, 0, 0, sizeof(vertexData));
```

我们也可以把writetarget缓冲绑定为新缓冲目标类型其中之一：

```c++
GLfloat vertexData[] = { ... };
glBindBuffer(GL_ARRAY_BUFFER, vbo1);
glBindBuffer(GL_COPY_WRITE_BUFFER, vbo2);
glCopyBufferSubData(GL_ARRAY_BUFFER, GL_COPY_WRITE_BUFFER, 0, 0, sizeof(vertexData));
```

有了这些额外的关于如何操纵缓冲的知识，我们已经可以以更有意思的方式来使用它们了。当你对OpenGL更熟悉，这些新缓冲方法就变得更有用。下个教程中我们会讨论unform缓冲对象，彼时我们会充分利用glBufferSubData。
