本文作者JoeyDeVries，由gjy_1992翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/OpenGL)

##OpenGL

---

在进行这段旅程之前我们先解释下OpenGL到底是什么。它一般被认为是一个**应用程序编程接口**（API），包含了一系列可以操作图形、画像的方法。然而，OpenGL本身并不是一个API，仅仅是一个规范，由[Khronos组织](http://www.khronos.org/)制定并维护。

OpenGL规范严格规定了每个函数该如何执行，以及它们该如何返回。至于内部具体每个函数是如何实现的，将由openGL库的开发者自行决定（注：这里开发者是指编写OpenGL库的人）。因为OpenGL规范并没有规定实现的细节，具体的OpenGL库允许使用不同的实现，只要其功能和结果与规范相匹配（亦即，作为用户不会感受到功能上的差异）。

实际的OpenGL库的开发者通常是显卡的生产商。每个你购买的显卡都会支持特定版本的OpenGL，通常是为一个系列的显卡专门开发的。当你使用苹果系统的时候，OpenGL库是由苹果自身维护的。在Linux下，有显卡生产商提供的OpenGL库，也有一些爱好者改编的版本。这也意味着任何时候OpenGL库表现的行为与规范规定的不一致时，基本都是库的开发者留下的bug。（快甩锅）


<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
由于大多数实现都是由显卡厂商编写的，当产生一个bug时通常可以通过升级显卡驱动来解决。这些驱动会包括你的显卡能支持的最新版本的OpenGL，这也是为什么总是建议你偶尔更新一下显卡驱动。
</div>


Khronos公开主持所有版本的OpenGL规范书的制定。有兴趣的读者可以找到OpenGL3.3（我们将要提到的版本）的[规范书](https://www.opengl.org/registry/doc/glspec33.core.20100311.withchanges.pdf)。如果你想深入到OpenGL的细节（注意只描述函数的功能而不管实现），这是个很好的选择。该规范还提供一个强大的可以寻找到每个函数具体功能的参考。

##对比核心模式和立即渲染模式

早期的OpenGL使用立即渲染模式（固定渲染管线），这个模式下绘制图形很方便。OpenGl的大多数功能都被隐藏起来，开发者很少能控制OpenGL如何进行计算。开发者最终希望更多的灵活性。随着时间推移，规范越来越灵活，开发者也能更多的控制绘图细节。立即渲染模式确实容易使用和理解，但是效率太低。因此从OpenGL3.2开始，规范书开始废弃立即渲染模式，推行核心模式，这个模式完全移除了旧的特性。

当使用核心模式时，OpenGL迫使我们使用现代的做法。当我们试图使用一个废弃的函数时，OpenGL会抛出一个错误并终止绘图。现代做法的优势是更高的灵活性和效率，然而也更难于学习。立即渲染模式从OpenGL实际操作中抽象掉了很多细节，因而它易于学习的同时，也很难去把握OpenGL具体是如何操作的。现代做法要求使用者真正理解OpenGL和图形编程，它有一些难度，然而提供了更多的灵活性，更高的效率，更重要的可以更深入的理解图形编程。

这也是为什么我们的教程面向OpenGL3.3的核心模式。虽然上手更困难，但是值得去努力。

现今更高版本的OpenGL已经发布（目前最新是4.5），你可能会问：为什么我们还要学习3.3？答案很简单，所有OpenGL的更高的版本都是在3.3的基础上，添加了额外的功能，并不更改核心架构。新版本只是引入了一些更有效率或更有用的方式去完成同样的功能。因此所有的概念和技术在现代OpenGL版本里都保持一致。当你的经验足够，你可以轻松使用来自更高版本OpenGL的新特性。


<div style="border:solid #E1B3B3;border-radius:10px;background-color:#FFD2D2;margin:10px 10px 10px 0px;padding:10px">
当使用新版本OpenGL的新特性时，只有新一代的显卡能够支持你的应用程序。这也是为什么大多数开发者基于较低版本的OpenGL编写程序，并有选择的启用新特性。
</div>


在有些教程里你会发现像如下方式注明的新特性。

##扩展

OpenGL的一大特性就是对扩展的支持，当一个显卡公司提出一个新特性或者渲染上的大优化，通常会以扩展的方式在驱动中实现。如果一个程序在支持这个扩展的显卡上运行，开发者可以使用这个扩展提供的一些更先进更有效的图形功能。通过这种方式，开发者不必等待一个新的OpenGL规范面世，就可以方便的检查显卡是否支持此扩展。通常，当一个扩展非常流行或有用的时候，它将最终成为未来的OpenGL规范的一部分。

使用扩展的代码大多看上去如下：

```c++
	if(GL_ARB_extension_name)
	{
    	// 使用一些新的特性
	}
	else
	{
		// 不支持此扩展: 用旧的方式去做
	}
```

使用OpenGL3.3时，我们很少需要使用扩展来完成大多数功能，但是掌握这种方式是必须的。

##状态机

OpenGL自身是一个巨大的状态机：一个描述OpenGL该如何操作的所有变量的大集合。OpenGL的状态通常被称为OpenGL**上下文**（context）。我们通常使用如下途径去更改OpenGL状态：设置一些选项，操作一些缓存。最后，我们使用当前OpenGl上下文来渲染。

假设当我们想告诉OpenGL去画线而不是三角形的时候，我们通过改变一些上下文变量来改变OpenGL状态，从而告诉OpenGL如何去绘图。一旦我们改变了OpenGL的状态为绘制线段，下一个绘制命令就会画出线段而不是三角形。

用OpenGL工作时，我们会遇到一些**改变OpenGL工作状态的函数**（state-changing function），以及一些在这些状态的基础上**执行操作的函数**（state-using function）。只要你记住OpenGL本质上是个大状态机，就能更容易理解它的大部分特性。

##对象（Object）

OpenGL库是用C写的，同时也支持多种语言的派生，但是核心是一个C库。一些C语言的结构不易被翻译到其他高层语言，因此OpenGL设计的时候引入了一些抽象概念。“对象”就是其中一个。

在OpenGL中一个对象是指一些选项的集合，代表OpenGL状态的一个子集。比如，我们可以有一个对象来代表绘图窗口的设置，可以设置它的大小、支持的颜色位数等等。可以把对象看做一个C风格的结构体：

```c++
	struct object_name {
	    GLfloat  option1;
	    GLuint   option2;
	    GLchar[] name;
	};
```

<div style="border:solid #AFDFAF;border-radius:10px;background-color:#D8F5D8;margin:10px 10px 10px 0px;padding:10px">
<span style="font-size:20px"><b>原始类型</b></span>
<br/>
使用OpenGL时，建议使用OpenGL定义的原始类型。比如使用float时我们加上前缀GL（因此写作GLfloat）。int，uint，char，bool等等类似。OpenGL定义了这些GL原始类型的平台无关的内存排列方式。而int等原始类型在不同平台上可能有不同的内存排列方式。使用GL原始类型可以保证你的程序在不同的平台上工作一致。
</div>


当我们使用一个对象时，通常看起来像如下一样（把OpenGL上下文比作一个大的结构体）：

```c++
	// OpenGL状态
	struct OpenGL_Context {
	  	...
 	 	object* object_Window_Target;
 	 	...  	
	};
```

```c++
	// 创建一个对象
	GLuint objectId = 0;
	glGenObject(1, &objectId);
	// 绑定对象至上下文
	glBindObject(GL_WINDOW_TARGET, objectId);
	// 设置GL_WINDOW_TARGET对象的一些选项
	glSetObjectOption(GL_WINDOW_TARGET, GL_OPTION_WINDOW_WIDTH, 800);
	glSetObjectOption(GL_WINDOW_TARGET, GL_OPTION_WINDOW_HEIGHT, 600);
	// 将上下文的GL_WINDOW_TARGET对象设回默认
	glBindObject(GL_WINDOW_TARGET, 0);
```

这一小片代码将会是以后使用OpenGl时常见的工作流。我们首先创建一个对象，然后用一个id保存它的引用（实际数据被储存在后台）。然后我们将对象绑定至上下文的目标位置（例子里窗口对象的目标位置被定义成GL\_WINDOW\_TARGET）。接下来我们设置窗口的选项，最后我们解绑这个对象，通过将目标位置的对象id设回0。我们设置的选项被保存在objectId代表的对象中，一旦我们重新绑定这个对象到GL\_WINDOW\_TARGET位置，这些选项就会重新生效。


<div style="border:solid #E1B3B3;border-radius:10px;background-color:#FFD2D2;margin:10px 10px 10px 0px;padding:10px">
目前提供的示例代码只是OpenGL如何操作的一个大致描述，通过教程你会遇到很多实际的例子。
</div>


使用对象的一个好事是我们在程序中可以定义不止一个对象，设置他们的选项，当我们需要进行一个操作的时候，只需要绑定预设了需要的状态的对象。比如，有作为3D模型数据（一栋房子或一个人物）容器对象的对象，任何时候我们想绘制其中一个3D模型的时候，只需绑定相应的含模型数据的对象（我们预先创建并设置好了它们的选项）。拥有数个这样的对象允许我们指定多个模型，在想画其中任何一个的时候，简单的将相应的对象绑定上去，不需要进行重复的设置选项的操作。

##让我们开始吧

你现在已经知道一些OpenGL的相关知识了，包括OpenGL作为规范和库，OpenGL大致的操作流程，以及一些使用扩展的小技巧。不要担心没有完全消化它们，通过这个教程我们会仔细讲解每一步，你会通过足够的例子来把握OpenGL。如果你已经做好了下一步的准备，我们可以开始建立OpenGL上下文以及我们的第一个窗口了。[点击这里](http://www.learnopengl.com/#!Getting-started/Creating-a-window)（第一章第二节）

##额外的资源

- [opengl.org](https://www.opengl.org/): OpenGL官方网站.
- [OpenGL registry](https://www.opengl.org/registry/): OpenGL各版本的规范和扩展的主站。