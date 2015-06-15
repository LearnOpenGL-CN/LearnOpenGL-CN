本文作者JoeyDeVries，由Geequlim翻译自[http://learnopengl.com](http://learnopengl.com/#!Getting-started/Hello-Window)

上一节中我们获取到了GLFW和GLEW这两个开源库，现在我们就可以使用它们来我们创建一个OpenGL绘图窗口了。首先，新建一个 .cpp文件，然后把下面的代码粘贴到该文件的最前面。注意为之所以定义GLEW_STATIC宏，是因为我们使用GLEW的静态链接库。

    // GLEW
    #define GLEW_STATIC
    #include <GL/glew.h>
    // GLFW
    #include <GLFW/glfw3.h>
    


> Be sure to include GLEW before GLFW. The include file for GLEW contains the correct OpenGL header includes (like GL/gl.h) so including GLEW before other header files that require OpenGL does the trick.

> 请确认在包含GLFW头文件之前包含了GLEW，


    
