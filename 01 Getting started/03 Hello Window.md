本文作者JoeyDeVries，由Geequlim翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/Hello-Window)

##你好，窗口

上一节中我们获取到了GLFW和GLEW这两个开源库，现在我们就可以使用它们来创建一个OpenGL绘图窗口了。首先，新建一个 .cpp文件，然后把下面的代码粘贴到该文件的最前面。注意，之所以定义GLEW_STATIC宏，是因为我们使用GLEW的静态链接库。

```c++
// GLEW
#define GLEW_STATIC
#include <GL/glew.h>
// GLFW
#include <GLFW/glfw3.h>
```

> 请确认在包含GLFW的头文件之前包含了GLEW的头文件。在包含glew.h头文件时会引入许多OpenGL必要的头文件（例如GL/gl.h），所以#include < GL/glew.h\>应放在引入其他头文件的代码之前。

接下来我们创建main函数，并做一些初始化GLFW的操作：

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

首先我们在main函数中调用glfwInit函数来初始化GLFW，然后我们可以使用glfwWindowHint函数来配置GLFW。glfwWindowHint函数的第一个参数表示我们要进行什么样的配置，我们可以选择大量以“GLFW\_”开头的枚举值；第二个参数接受一个整形，用来设置这个配置的值。该函数的所有的选项以及对应的值都可以在 [GLFW's window handling](http://www.glfw.org/docs/latest/window.html#window_hints) 这篇文档中找到。如果你现在编译你的cpp文件会得到大量的连接错误，这是因为你还需要设置GLFW的链接库。

由于本网站的教程都是基于OpenGL3.3以后的版本展开讨论的，所以我们需要告诉GLFW我们要使用的OpenGL版本是3.3，这样GLFW会在创建OpenGL上下文时做出适当的调整。这也可以确保用户在没有适当的OpenGL版本支持的情况下无法运行。在这里我们告诉GLFW想要的OpenGL版本号是3.3，并且不允许用户调整窗口的大小。我们明确地告诉GLFW我们想要使用核心模式（core-profile），这将导致我们无法使用那些已经废弃的API，而这不正是一个很好的提醒吗？当我们不小心用了旧功能时报错，就能避免使用一些被废弃的用法了。如果你使用的是Mac OSX系统你还需要加下面这行代码这些配置才能起作用：

```c++
 glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
```
>请确认您的系统支持OpenGL3.3或更高版本，否则此应用有可能会崩溃或者出现不可预知的错误。可以通过运行glew附带的glxinfo程序或者其他的工具（例如[OpenGL Extension Viewer ](http://download.cnet.com/OpenGL-Extensions-Viewer/3000-18487_4-34442.html)来查看的OpenGL版本。如果您的OpenGL版本低于3.3请更新您的驱动程序或者有必要的话更新您的设备。

接下来我们创建一个窗口对象，这个窗口对象中具有关和窗口相关的许多数据，而且会被GLFW的其他函数频繁地用到。

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

glfwCreateWindow函数需要窗口的宽和高作为它的前两个参数；第三个参数表示只这个窗口的名称（标题），这里我们使用"LearnOpenGL"，当然你可以使用你喜欢的名称；最后两个参数我们暂时忽略，先置为空指针就行。它的返回值GLFWwindow对象的指针会在其他的GLFW操作中使用到。创建完窗口我们就可以通知GLFW给我们的窗口在当前的线程中创建我们等待已久的OpenGL上下文了。

###GLEW

在之前的教程中已经提到过，GLEW是用来管理OpenGL的函数指针的，所以在调用任何OpenGL的函数之前我们需要初始化GLEW。

```c++
glewExperimental = GL_TRUE;
if (glewInit() != GLEW_OK)
{
    std::cout << "Failed to initialize GLEW" << std::endl;
    return -1;
}
```
请注意，我们在初始化GLEW之前设置glewExperimental变量的值为GL_TRUE，这样做能让GLEW在管理OpenGL的函数指针时更多地使用现代化的技术，如果把它设置为GL_FALSE的话可能会在使用OpenGL的核心模式（core-profile）时出现一些问题。

###视口（Viewport）

在我们绘制之前还有一件重要的事情要做，我们必须告诉OpenGL渲染窗口的尺寸大小，这样OpenGL才只能知道要显示数据的窗口坐标。我们可以通过调用glViewport函数来设置这些维度：

```c++
glViewport(0, 0, 800, 600);  
```
前两个参数设置窗口左下角的位置。第三个和第四个参数设置渲染窗口的宽度和高度,我们设置成与GLFW的窗口的宽高大小，我们也可以将这个值设置成比窗口小的数值，然后所有的OpenGL渲染将会显示在一个较小的区域。

>OpenGL 使用glViewport定义的位置和宽高进行位置坐标的转换，将OpenGL中的位置坐标转换为你的屏幕坐标。例如，OpenGL中的坐标(0.5,0.5)有可能被转换为屏幕中的坐标(200,450)。注意，OpenGL只会把-1到1之间的坐标转换为屏幕坐标，因此在此例中(-1，1)转换为屏幕坐标是（0,600）。

###准备好你的引擎

我们可不希望只绘制一个图像之后我们的应用程序就关闭窗口并立即退出。我们希望程序在我们明确地关闭它之前一直保持运行状态并能够接受用户输入。因此，我们需要在程序中添加一个while循环，我们可以把它称之为游戏循环（game loop），这样我们的程序就能在我们让GLFW退出前保持运行了。下面几行的代码就实现了一个简单的游戏循环：

```c++
while(!glfwWindowShouldClose(window))
{
    glfwPollEvents();
    glfwSwapBuffers(window);
}
```

* glfwWindowShouldClose函数在我们每次循环的开始前检查一次GLFW是否准备好要退出，如果是这样的话该函数返回true然后游戏循环便结束了，之后为我们就可以关闭应用程序了。
* glfwPollEvents函数检查有没有触发什么事件（比如键盘有按钮按下、鼠标移动等）然后调用对应的回调函数（我们可以手动设置这些回调函数）。我们一般在游戏循环的一开始就检查事件。
* 调用glfwSwapBuffers会交换缓冲区（储存着GLFW窗口每一个像素颜色的缓冲区）

>双缓冲区

>应用程序使用单缓冲区绘图可能会存在图像闪烁的问题。 这是因为生成的图像不是一下子被绘制出来的，而是按照从左到右，由上而下逐像素地绘制而成的。因为这些不是在瞬间显示给用户,而是通过一步一步地计算结果绘制的，这可能会花费一些时间。为了规避这些问题，我们应用双缓冲区渲染窗口应用程序。前面的缓冲区保存着计算后可显示给用户的图像，被显示到屏幕上；所有的的渲染命令被传递到后台的缓冲区进行计算。当所有的渲染命令执行结束后，我们交换前台缓冲和后台缓冲，这样图像就立即呈显出来，之后清空缓冲区。

###最后一件事

当游戏循环结束后我们需要释放之前的操作分配的资源，我们可以在main函数的最后调用glfwTerminate函数来释放GLFW分配的内存。

```c++
glfwTerminate();
return 0;
```
这样便能清空GLFW分配的内存然后正确地退出应用程序。现在你可以尝试编译并运行你的应用程序了，你将会看到如下的一个黑色窗口：

![](http://learnopengl.com/img/getting-started/hellowindow.png)

如果你没有编译通过或者有什么问题的话，首先请检查你程序的的链接选项是否正确
。然后对比本教程的代码，检查你的代码是不是哪里写错了，你也可以[点击这里](http://learnopengl.com/code_viewer.php?code=getting-started/hellowindow)获取我的完整代码。

###输入

我们可以通过多种用户输入来控制GLFW，这是通过设置GLFW的回调函数来实现的。回调函数事实上是一个函数指针，当我们为GLFW设置回调函数后，GLWF会在恰当的时候调用它。按键回调（KeyCallback）是众多回调函数中的一种，当我们为GLFW设置按键回调之后，GLFW会在用户有键盘交互时调用它。该回调函数的原型如下所示：

```c++
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode);
```
按键回调函数接受一个GLFWwindow指针作为它的第一个参数；第二个整形参数用来表示事件的按键；第三个整形参数描述用户是否有第二个键按下或释放；第四个整形参数表示事件类型，如按下或释放；最后一个参数是表示是否有Ctrl、Shift等按钮的操作。GLFW会在恰当的时候调用它，并为各个参数传入适当的值。

```c++
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mode)
{
    // 当用户按下ESC键,我们设置window窗口的WindowShouldClose属性为true
    // 关闭应用程序
    if(key == GLFW_KEY_ESCAPE && action == GLFW_PRESS)
    	glfwSetWindowShouldClose(window, GL_TRUE);
}    
```
当用户按下ESC键时我们设置窗口的WindowShouldClose(窗口是否应该被关闭)属性的值为真。当执行下一次游戏循环时，glfwWindowShouldClose(window)返回真，此时游戏循环便不再继续，然后释放资源结束程序。

最后我们还要为GLFW注册这个按键回调函数，这样它才能被GLFW在触发按键事件时被调用。

```c++
glfwSetKeyCallback(window, key_callback);  
```
除了按键回调函数之外，我们还能为GLFW注册其他的回调函数。例如，我们可以注册一个函数来处理窗口尺寸变化、处理一些错误信息等。我们可以在创建窗口之后到开始游戏循环之前注册各种回调函数。

###渲染

我们要把所有的渲染操作放到游戏循环中，因为我们想让这些渲染操作在每次游戏循环迭代的时候都能被执行。我们将做如下的操作：

```c++
// 程序循环
while(!glfwWindowShouldClose(window))
{
    // 检查事件
    glfwPollEvents();

    // 在这里执行各种渲染操作
    ...

    //交换缓冲区
    glfwSwapBuffers(window);
}
```
为了测试一切都正常，我们想让屏幕清空为一种我们选择的颜色。在每次执行新的渲染之前我们都希望清除上一次循环的渲染结果，除非我们想要看到上一次的结果。我们可以通过调用glClear函数来清空屏幕缓冲区的颜色，他接受一个整形常量参数来指定要清空的缓冲区，这个常量可以是GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT和 GL_STENCIL_BUFFER_BIT。由于现在我们只关心颜色值，所以我们只清空颜色缓冲区。

```c++
glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
glClear(GL_COLOR_BUFFER_BIT);
```
注意，除了glClear之外，我们还要调用glClearColor来设置要清空缓冲的颜色。当调用glClear函数之后，整个指定清空的缓冲区都被填充为glClearColor所设置的颜色。在这里，我们将屏幕设置为了类似黑板的深蓝绿色。

>你应该能够想起来我们在 [OpenGL]() 教程的内容， glClearColor函数是一个状态设置函数，而glClear函数则是一个状态应用的函数。

![](http://learnopengl.com/img/getting-started/hellowindow2.png)

此程序的完整源代码可以在[这里](http://learnopengl.com/code_viewer.php?code=getting-started/hellowindow2)找到。

好了，到目前为止我们已经做好开始在游戏循环中添加许多渲染操作的准备了，我认为我们的闲扯已经够多了，从[设置：：：：：下一篇教程](http://www.learnopengl.com/#!Getting-started/Hello-Triangle)开始我们将真正的征程