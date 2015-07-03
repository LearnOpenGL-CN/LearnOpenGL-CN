本文作者JoeyDeVries，由Meow J翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/Shaders)

##变换(Transformations)

尽管我们现在已经知道了如何创建物体，着色，与加入纹理，他们仍然是静态的，还不是那么有趣. 我们可以尝试着在每一帧改变物体的顶点并且重设缓冲区从而使他们移动，但这太繁琐了，而且会消耗很多的处理时间. 然而，我们现在有一个更好的解决方案，那就是使用(多个)矩阵来对这个物体进行**变换**(Transform).

**矩阵**(Matrix)是一种非常有用的数学工具，尽管听起来可能有些吓人. 不过一旦你适应了使用它们，你会发现它们非常的有用. 在讨论矩阵的过程中，我们必须使用到一些数学知识，如果你对这块的数学非常感兴趣，我会提供给你提供额外的拓展资源.

为了深入了解变换，我们需要在讨论矩阵之前先来深入探讨**矢量**(Vector). 这一节的目标是让你拥有将来需要的最基础的数学背景知识. 如果你发现这节十分困难，尽量去理解吧. 你以后遇见问题也可以回来复习这节的概念.

##矢量(Vectors)

最简单的来定义，矢量表示一个方向. 更正式的说，矢量同时拥有**方向** (Direction)和**大小** (Magnitude). 你可以想象一下，把矢量当做藏宝图的指示：左走10步，之后向北走3步，再向右走5步. 在这个例子当中，“左”就是方向，“10步”就是这个矢量的大小. 你可以发现，这个藏宝图的指示一共有三个矢量. 矢量可以在任意**维度**(Dimension)上，但我们最常使用的是从二维到四维. 如果一个矢量有两个维度，它就表示在平面上的一个方向；如果一个矢量有三个维度，他就能表示在3D世界中的一个方向.

下图中你可以看到三个矢量，每一个矢量都由一个箭头表示，并且记为(x,y). 我们在2D图片中展示这些矢量，因为这样子会更直观. 你仍然可以把这些2D矢量当做z坐标为0的3D矢量. 因为矢量代表着一个方向，矢量原点的不同**并不会**改变它的值. 在图像中，矢量![](http://latex2png.com/output//latex_e91010b29e958e4fbc824584145939c6.png)和![](http://latex2png.com/output//latex_d9ed1f291de6a7f8f8b98910b32d1b1f.png)是**相等**的，尽管他们的原点不一样.

![](http://learnopengl.com/img/getting-started/vectors.png)

当表示一个矢量的时候，通常我们使用在字符上面加一道杠的方法来表示，比如![](http://latex2png.com/output//latex_bd890aa3934604aac5038acd23d62d50.png). 在公式中是这样表示的:

![](http://latex2png.com/output//latex_f6b0b4b613d888bc3239069623169884.png)

因为矢量是方向，所以有些时候会很难形象地用位置(Position)表示出来. 我们通常设定这个方向的原点为(0,0,0)，然后指向对应坐标的点，使其变为位置矢量(Position Vector)来表示(我们也可以定义一个不同的原点并认为其从该原点的空间指向那个点). 位置矢量(3,5)将在图像中从原点(0,0)指向点(3,5). 因此，我们可以使用矢量在2D或3D空间中表示方向**与**位置.


就像普通的数字一样，我们也可以给矢量定义一些运算(你可能已经知道一些了).

### 矢量与标量运算(Scalar Vector Operations)

**标量**(Scalar)仅仅是一个数字(或者说是仅有一个分量的矢量). 当使用标量对矢量进行加/减/乘/除运算时，我们可以简单地对该矢量的每一个元素进行该运算. 对于加法来说会像这样:

![](http://latex2png.com/output//latex_ced260b3ce642ed56f177244c3b4189e.png)

其中的＋可以是＋/－/×/÷，注意－和÷运算时不能颠倒，颠倒的运算是没有定义的(标量-/÷矢量)

### 矢量的取反(Vector Negation)

对一个矢量取反会将其方向逆转，比如说一个指向东北方向的矢量取反后将会指向西南方向. 我们在一个矢量的每个分量前加负号从而实现取反(或者说用-1数乘该矢量):

![](http://latex2png.com/output//latex_8d5dcc978ccf9d559d64af04b1ddfa7c.png)

### 矢量的加与减(Addition and Subtraction)

矢量的加法可以被定义为是分量的相加，即将一个矢量中的每一个分量加上另一个矢量的对应分量：

![](http://latex2png.com/output//latex_3d5a8fd9db45ecfed81acdad2691caa8.png)

在图像上v=(4,2)与k=(1,2)相加是这样的：

![](http://learnopengl.com/img/getting-started/vectors_addition.png)

就像数字的加减一样，矢量的减法等同于一个矢量加上取反的另一个矢量.

![](http://latex2png.com/output//latex_aa68be1c1c3294bf4d931c39d9fe8ea1.png)

两个矢量的相减会得到这两个矢量指向位置的差. 这在我们想要获取两点的差会非常有用.

### 矢量的长度(Length)

我们使用勾股定理(Pythagoras theorem)来获取矢量的长度(大小). 如果你把矢量的x与y分量画出来，该矢量会形成一个以x与y分量为边的三角形:

![](http://learnopengl.com/img/getting-started/vectors_triangle.png)

因为x与y已知，我们可以用勾股定理求出斜边![](http://latex2png.com/output//latex_e91010b29e958e4fbc824584145939c6.png)：

![](http://latex2png.com/output//latex_25a4b63018e587812dd6625a075ec9dd.png)

其中![](http://latex2png.com/output//latex_8f7bf6541904f09a5318814c6b03fe17.png)代表矢量![](http://latex2png.com/output//latex_e91010b29e958e4fbc824584145939c6.png)的大小. 我们也可以很容易加上![](http://latex2png.com/output//latex_a1049fd26252d4e0795dd75bd0bb8e12.png)把这个公式拓展到三维空间

#WIP
