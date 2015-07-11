本文作者JoeyDeVries，由[Django](http://bullteacher.com/4-hello-window.html)翻译自[http://learnopengl.com](http://www.learnopengl.com/#!Getting-started/Hello-Window)

# Hello Window

我们看看GLFW是否能够运行。首先，创建一个.cpp文件，在新创建的文件的顶部包含下面的头文件。注意，我们定义了`GLEW_STATIC`，这是因为我们将使用静态GLEW库。

```c++
// GLEW
#define GLEW_STATIC
#include <GL/glew.h>
// GLFW
#include <GLFW/glfw3.h>
```

<div style="border:solid #E1B3B3;border-radius:10px;background-color:#FFD2D2;margin:10px 10px 10px 0px;padding:10px">
必须在GLFW之前引入GLEW。GLEW的头文件已经包含了OpenGL的头文件（`GL/gl.h`），所以要在其他头文件之前引入GLEW，因为它们需要有OpenGL才能起作用。
</div>

下面，我们创建main函数，在main函数中我们会实例化一个GLFW窗口：

```c++
int main()
{
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_RESIZABLE, GL_FALSE);

    return 0;
}
```

在main函数中我们首先使用`glfwInit`来初始化GLFW，然后我们可以使用`glfwWindowHint`来配置GLFW。`glfwWindowHint`的第一个参数告诉我们，我们打算配置哪个选项，这里我们可以从一个枚举中选择可用的选项，这些选项带有`GLFW_`前缀。第二个参数是一个整数，它代表我们为选项所设置的值。可用的选项和对应的值可以在[GLFW窗口管理文档](http://www.glfw.org/docs/latest/window.html#window_hints "GLFW窗口管理文档")中列出。现在，如果你去运行应用报出了很多未定义引用错误，这意味着你还没有成功的链接GLFW库。

由于这个教程关注的是OpenGL 3.3版本，我们会告诉GLFW我们使用的OpenGL版本是3.3。这样GLFW在创建**OpenGL环境**的时候可以做出合理的安排。这会保证如果一个用户没有特定的OpenGL版本，GLFW就会运行失败。我们把主和次版本都设置为3。我们同样告诉GLFW，我们希望明确地使用**核心模式(Core Profile)**，同时用户不可以调整窗口大小。显式地告诉GLFW我们希望是用核心模式会导致当我们调用一个OpenGL的遗留函数会产生**非法操作(Invalid Operation)**错误，当我们意外地使用了不该使用的旧函数时它是一个很好的提醒。注意在Mac OS X上在初始化代码里你还需要添加`glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);`才能工作。

<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
你需要确定你的系统/硬件上已经安装了OpenGL3.3或更高的版本，否则应用会崩溃或产生不可预测的结果。在Linux上找到你的机器上OpenGL的版本可以调用`glxinfo`，Windows机器上要使用[OpenGL Extension Viewer](http://download.cnet.com/OpenGL-Extensions-Viewer/3000-18487_4-34442.html "OpenGL Extension Viewer")这样的工具。如果支持的版本太低了，检查一下的你的显卡是否支持OpenGL3.3+（如果不支持那就太老了），先去更新你的驱动。
</div>

下面我们需要创建一个窗口对象。这个窗口对象带有所有的窗口数据，它们通常是GLFW的其他函数经常使用的。

```c++
GLFWwindow* window = glfwCreateWindow(800, 600, "LearnOpenGL", nullptr, nullptr);
if (window == nullptr)
{
    std::cout << "Failed to create GLFW window" << std::endl;
    glfwTerminate();
    return -1;
}
glfwMakeContextCurrent(window);
```
函数`glfwCreateWindow`需要窗口的**宽度**和**高度**作为它前两个参数。第三个参数允许我们给窗口创建一个名字；现在我们把它命名为`"LearnOpenGL"`但是你也可以取个自己喜欢的名字。我们**可以忽略最后两个参数**。这个函数返回一个`GLFWwindow`对象，在后面的其他GLFW操作会需要它。之后，我们告诉GLFW去创建我们窗口的环境（`glfwMakeContextCurrent`），这个环境是当前线程的主环境。

## GLEW

前面的教程里，我们提到GLEW管理着OpenGL的函数指针，所以我们希望在调用任何OpenGL函数前初始化GLEW。

```c++
glewExperimental = GL_TRUE;
if (glewInit() != GLEW_OK)
{
    std::cout << "Failed to initialize GLEW" << std::endl;
    return -1;
}
```

注意，在初始化GLEW前我们把`glewExperimental`变量设置为`GL_TRUE`。设置`glewExperimental`为true可以保证GLEW使用更多的现代技术来管理OpenGL功能。如果不这么设置，它就会使用默认的`GL_FALSE`，这样当使用核心模式时有可能发生问题。

## 视口(Viewport)

在我们开始渲染前，我们必须做这最后一件事。我们必须告诉OpenGL渲染窗口的大小，这样OpenGL才能知道我们希望如何设置窗口的大小和位置。我们可以通过`glViewport`函数设置这些尺寸：

```c++
glViewport(0, 0, 800, 600);
```

前两个参数设置了窗口**左下角的位置**。第三个和第四个参数是这个渲染窗口的**宽度**和**高度**，它和GLFW窗口是一样大的。我们可以把这个值设置得比GLFW窗口尺寸小；这样OpenGL的渲染都会在一个更小的窗口（区域）进行显示，我们可以在OpenGL的视区之外显示其他的元素。

<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
在幕后OpenGL是使用通过`glViewport`指定的数据将2D坐标加工为屏幕上的坐标。比如，一个被加工的点的位置是(-0.5, 0.5)会（作为它最后的变换）被映射到屏幕坐标(200, 450)上。注意，OpenGL中处理的坐标是在-1和1之间，所以我们事实上是把（-1到1）的范围映射到(0, 800)和(0, 600)上了。
</div>

## 准备好你的引擎

我们不希望应用绘制了一个图像之后立即退出，然后关闭窗口。我们想让应用持续地绘制图像，监听用户输入直到软件被明确告知停止。为了达到这个目的，我们必须创建一个while循环，我们称其为游戏循环（Game Loop），这样，在我们告诉GLFW停止之前应用就会一直保持运行状态。下面的代码展示了一个非常简单的游戏循环。

```c++
while(!glfwWindowShouldClose(window))
{
    glfwPollEvents();
    glfwSwapBuffers(window);
}
```

`glfwWindowShouldClose`函数从开始便检验每一次循环迭代中gLFW是否已经得到关闭指示，如果得到这样的指示，函数就会返回true，并且游戏循环停止运行，之后我们就可以关闭应用了。

`glfwPollEvents`函数检验是否有任何事件被处触发（比如键盘输入或是鼠标移动的事件），接着调用相应函数（我们可以通过回调方法设置它们）。我们经常在循环迭代前调用事件处理函数。

`glfwSwapBuffers`函数会交换**颜色缓冲**（颜色缓冲是一个GLFW窗口为每一个像素储存颜色数值的大缓冲），它是在这次迭代中绘制的，也作为输出显示在屏幕上。

<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
**双缓冲（Double buffer）**

当一个应用以单缓冲方式绘制的时候，图像会产生闪缩的问题。这是因为最后的图像输出不是被立即绘制出来的，而是一个像素一个像素绘制出来的，通常是以从左到右从上到下这样的方式。由于这些图像不是立即呈现在用户面前，而是一步一步地生成结果，这就产生很多不真实感。为了规避这些问题，窗口应用使用双缓冲的方式进行渲染。**前缓冲**包含最终的输出图像，它被显示在屏幕上，与此同时，所有的渲染命令绘制**后缓冲**。所有的渲染命令执行结束，我们就把后缓冲**交换**到前缓冲，这样图像就会立即显示到用户面前了，前面提到的不真实感就这样被解决了。
</div>

## 最后一件事

退出游戏循环后，我们就可以合理地清理/释放之前分配的所有资源了。我们可以在`main`函数结尾使用`glfwTerminate`函数来做这件事。

```c++
glfwTerminate();
return 0;
```

这样会清理所有资源，并正确地退出应用。现在尝试编译你的应用，如果所有事情都工作的很好你就会看到下面的结果：

![](http://www.learnopengl.com/img/getting-started/hellowindow.png)

如果出现一个枯燥的黑色图像，你就做对了！如果你没有得到这个图像，或者不知道如何把所有东西组合起来，可以看我们的[完整源码](http://www.learnopengl.com/code_viewer.php?code=getting-started/hellowindow "完整源码")。

如果你在编译应用的时候出现状况，首先要确保链接器的所有配置都正确的做好了，在你的IDE中正确地包含了路径（前面的教程里讲过）。同时你要确保代码也是对的；你可以通过看源代码简单地去验证一下。如果仍然报错，在下面提交一个评论，写上你的问题，我或者其他人会尝试帮助你。

## 输入(Input)

我们同样希望在GLFW中有些控制输入的方式，我们可以使用GLFW的回调函数(Callback functions)做到这点。**回调函数**简单来说就是一个你可以设置的，从而使得GLFW能够在合适的时刻调用的函数指针。其中有一个我们可以设置的回调函数是**KeyCallback**函数，它在用户使用键盘交互的时候被调用。函数的原型是：

```c++
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode);
```

按键输入函数的接收一个`GLFWwindow`参数，一个代表按下按键的整型数字，一个特定动作，按钮是被按下、还是释放，一个代表某个标识的整数告诉你`shift`、`control`、`alt`或`super`是否被同时按下。每当一个用户按下一个按钮，GLFW都会调用这个函数，为你的这个函数填充合适的参数。

```c++
void key_callback(GLFWwindow * window, int key, int scancode, int action, int mode)
{
    // 当用户按下ESC, 我们就把WindowShouldClose设置为true, 关闭应用
    if(key == GLFW_KEY_ESCAPE && action == GLFW_PRESS)
        glfwSetWindowShouldClose(window, GL_TRUE);
}
```

在我们（新创建）的`key_callback`函数中，我们检查被按下的按键是否等于`ESC`健，如果是这个按键被按下（不是释放）的话，我们就用`glfwSetWindowShouldClose`设置它的`WindowShouldClose`属性为`true`来关闭GLFW。下一个主while循环条件检验会失败，应用就关闭了。

最后一件事就是通过GLFW使用合适的回调注册函数。可以这么做：

```c++
glfwSetKeyCallback(window, key_callback);
```

有许多回调函数可供用于注册我们自己的函数。比如，我们可以做一个回调函数处理窗口尺寸的改变，处理错误信息等等。我们要在创建窗口之后，在游戏循环初始化之前注册回调函数。  

## 渲染(Rendering)

我们想把所有渲染命令都放在游戏循环里，因为我们打算在每个循环迭代里都执行所有的渲染命令。这看起来有点像这样：
```c++
// 程序循环
while(!glfwWindowShouldClose(window))
{
    // 检查及调用事件
    glfwPollEvents();

    // 渲染指令放在这里
    ...

    // 交换缓冲
    glfwSwapBuffers(window);
}
```

我们用一种自己选择的颜色来清空屏幕，测试一下是否能够正常工作。每个渲染迭代的开始，我们都要清理屏幕，否则只能一直看到前一个迭代的结果（这可能就是你想要的效果，但通常你不会这么想）。我们可以使用`glClear`函数清理屏幕的颜色缓冲，在这个函数中我们以缓冲位（`BUFFER_BIT`）指定我们希望清理哪个缓冲。可用的位可以是`GL_COLOR_BUFFER_BIT`、`GL_DEPTH_BUFFER_BIT`和`GL_STENCIL_BUFFER_BIT`(译注：缓冲是显存上的一段空间，用来储存多种数据。)。现在，我们关心的只是颜色值，所以我们只清空颜色缓冲。

```c++
glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
glClear(GL_COLOR_BUFFER_BIT);
```

要注意，我们使用了`glClearColor`来设置了清空屏幕用的颜色。当调用`glClear`去清空颜色缓冲时，全部颜色缓冲都将被`glClearColor`所配置的颜色填充。本例会填充为暗蓝绿(Dark Green-blueish)色。

<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
你可能会回想起OpenGL教程，`glClearColor`函数是一个状态设置函数，`glClear`是一个状态使用函数，在这个函数里，它从当前状态获取清空所用的颜色。
</div>

![](http://www.learnopengl.com/img/getting-started/hellowindow2.png)

这个应用的完整代码可以在[这里](http://www.learnopengl.com/code_viewer.php?code=getting-started/hellowindow2 "这里")找到。

现在我们已经准备好把游戏循环用大量渲染函数填满了，但是这是下节要做的事。我认为我们已经在这里讲地够久的了。