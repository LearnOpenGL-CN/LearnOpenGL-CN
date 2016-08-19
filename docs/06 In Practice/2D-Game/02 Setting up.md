# 准备工作

原文     | [Setting up](http://learnopengl.com/#!In-Practice/2D-Game/Setting-up)
      ---|---
作者     | JoeyDeVries
翻译     | [ZMANT](https://github.com/Itanq)
校对     | 暂无

## 设置

在我们开始实际构造这个游戏之前，我们首先需要设置一些简单的框架来处理这个游戏，这个游戏将会用到几个第三方库，它们大多数都已经在前面的教程中介绍过了。不管在那个地方需要用到新的库的时候，我们都会作出适当的介绍。

首先，我们定义一个叫做`Game`的类来包含所有有关的渲染和游戏设置代码。有了这个类，我们就可以用这个类把游戏代码(稍稍的)有组织的嵌入到游戏窗口代码中。用这种方式，你就可以把相同的代码迁移到完全不同的窗口库(比如 SDL或SFML)而不需要做太多的工作。

> 存在有成千上万的方式来抽象并概括游戏/图形代码然后封装到类和对象中。在这个教程中，你刚好会看到有一个方法来解决这个问题。如果你感到有一个更好的方法，尽量实现你的改进。

这个`Game`类封装了一个初始化函数，一个更新函数，一个处理输入函数以及一个渲染函数：

```C++
class Game
{
    public:
        // Game state
        GameState  State;	
        GLboolean  Keys[1024];
        GLuint	   Width, Height;
        // Constructor/Destructor
        Game(GLuint width, GLuint height);
        ~Game();
        // Initialize game state (load all shaders/textures/levels)
        void Init();
        // GameLoop
        void ProcessInput(GLfloat dt);
        void Update(GLfloat dt);
        void Render();
};
```

这个类可能就是你期望中的游戏类。我们通过一个`width`和`height`(对应于你玩游戏时的设备分辨率)来初始化一个游戏实例并且使用`Init`函数来加载着色器、纹理以及初始化游戏状态。我们可以通过调用`ProcessInput`函数来使用存储在`Keys`数组里的数据来处理输入并且在`Update`函数里面更新游戏设置状态(比如玩家/球的移动)。最后，我们还可以在`Render`函数里面渲染游戏。注意，我们在渲染逻辑里面分离出了运动逻辑。

这个`Game`类同样了封装了一个叫做`State`的变量，它的类型`GameState`如下定义：

```C++
// Represents the current state of the game
enum GameState {
    GAME_ACTIVE,
    GAME_MENU,
    GAME_WIN
};
```

这可以使我们跟踪游戏当前的状态。这样我们就可以根据当前游戏的状态来决定渲染或者处理不同的元素(比如当我们在游戏菜单界面的时候就可能需要渲染和处理不同的元素)。

目前为止，这个`Game`类的函数还完全是空的，因为我们还没有写实际的实现代码，但这里就是`Game`类的[header](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_setting-up.h)和[code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_setting-up)文件。

## 通用

因为我们正在开发一个大型应用，所以我们将不得不频繁的重用一些OpenGL的概念，比如纹理和着色器等。因此，为这两个元素(items)创建一个更加易用的接口就是情理之中的事了，就像在我们前面一个教程中创建的那个`shader`类一样。

定义一个着色器类，它接收两个或三个字符串(如果有几何着色器)然后生成一个编译好的着色器(或者如果失败的话就生成一条错误信息)。这个着色器类同样也包含大量实用的函数来快速的设置`uniform`变量。同样也定义一个纹理类，它从给定的字节数组中生成一个2D纹理图像(基于它的内容)。并且这个纹理类同样也封装了许多实用的函数。

我们并不打算钻研这些类实现的细节，因为学到这里你应该可以很容易的理解它们是如何工作的了。出于这个原因你可以找到它们的头文件和实现的代码文件，有详细的注释，如下：

>* Shader : [header](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/shader.h),[code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/shader)
>* Texture: [header](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/texture.h),[code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/texture)

注意到当前的这个纹理类仅仅设置成单一的`2D`纹理，但你可以很容易的通过可选的纹理类型来扩展。

## 资源管理器

当着色器和纹理类的函数被他们自己使用的时候，他们确实需要一个字节数组或是几个字符串来初始化他们。我们可以很容易的在他们自己的类里面嵌入文件的加载代码，但这就稍微有点违反`单一职责原则`，(也就是说)在这个类里我们应该仅仅关注纹理或着色器本身而不需要关注他们的文件加载结构。

出于这个原因，通常用一个更加有组织的方法(来实现文件的加载)，就是创建一个叫做`resource manager`的单独实体类来加载游戏相关的资源。这里有好几个方法来实现`resouce manager`；在这个教程里我们选择使用一个单独的静态`resouce manager`(就是给它静态属性)，也就是说可以在整个工程中使用它来加载资源以及使用和她相关加载功能。

使用具有静态属性的单独的类有很多好处，但它主要的坏处就是会失去`OOP`特性以及控制结构/破坏。不过，这些对于小项目来说是很容易处理的。

就像其他的类文件一样，这个资源管理器的列表如下：

>* Resource Manager: [header](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/resource_manager.h), [code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/resource_manager)

使用资源管理我们可以很容易的把着色器加载到程序里面，比如：

```C++
Shader shader = ResourceManager::LoadShader("vertex.vs", "fragment.vs", nullptr, "test");
// then use it
shader.Use();
// or
ResourceManager::GetShader("test").Use();
```

通过定义的`Game`类和`resouce manager`类一起就可以很很容易管理`Shader`和`Texture2D`，基于这个基础，在以后的教程里我们将会广泛的使用这些类来实现这个`Breakout`游戏。

## 程序

对这个游戏，我们仍然需要创建一个窗口并且设置OpenGL的初识状态。我们确保使用OpenGL的[面剔除](http://learnopengl.com/#!Advanced-OpenGL/Face-culling)功能和它的[混合](http://learnopengl.com/#!Advanced-OpenGL/Blending)功能。我们不需要使用深度测试；因为这个游戏完全是一个二维的，所有顶点的`z`坐标都具有相同的值。因此开启深度测试并没有什么用还有可能造成`z-fighting`现象。

这个`Breakout`游戏开始时候的代码相当的简单：我们用`GLFW`创建一个窗口，注册了一些回调函数，创建一个`Game`实例并且调用了`Game`类所有相关的函数。这个代码如下：

>* Program: [code](http://learnopengl.com/code_viewer.php?code=in-practice/breakout/program)

运行这个代码，你可能得到下面的输出：

![ans](http://learnopengl.com/img/in-practice/breakout/setting-up.png)

目前为止我们已经有了一个后面的教程需要的固定框架；我们将会持续的扩展这个`Game`类来封装一些新的功能。如果你准备好了就点击[下一个](http://learnopengl.com/#!In-Practice/2D-Game/Rendering-Sprites)教程。

