# Assimp

原文     | [Assimp](http://learnopengl.com/#!Model-Loading/Assimp)
      ---|---
作者     | JoeyDeVries
翻译     | Cocoonshu
校对     | [Geequlim](http://geequlim.com)


到目前为止，我们已经在所有的场景中大面积滥用了我们的容器盒小盆友，但就是容器盒是我们的好朋友，时间久了我们也会喜新厌旧。一些图形应用里经常会使用很多复杂且好玩儿的模型，它们看起来比静态的容器盒可爱多了。但是，我们无法像定义容器盒一样手动地去指定房子、货车或人形角色这些复杂模型的顶点、法线和纹理坐标。我们需要做的也是应该要做的，是把这些模型导入到应用程序中，而设计制作这些3D模型的工作应该交给像[Blender](http://www.blender.org/)、[3DS Max](http://www.autodesk.nl/products/3ds-max/overview)或者[Maya](http://www.autodesk.com/products/autodesk-maya/overview)这样的工具软件。

那些3D建模工具，可以让美工们构建一些复杂的形状，并将贴图应用到形状上去，即纹理映射。然后，在导出模型文件时，建模工具会自己生成所有的顶点坐标、顶点法线和纹理坐标。这样，美工们可以不用了解大量的图像技术细节，就能有大量的工具集去随心地构建高品质的模型。所有的技术细节内容都隐藏在里导出的模型文件里。而我们，这些图形开发者，就必须得去关注这些技术细节了。

因此，我们的工作就是去解析这些导出的模型文件，并将其中的模型数据存储为OpenGL能够使用的数据。一个常见的问题是，导出的模型文件通常有几十种格式，不同的工具会根据不同的文件协议把模型数据导出到不同格式的模型文件中。有的模型文件格式只包含模型的静态形状数据和颜色、漫反射贴图、高光贴图这些基本的材质信息，比如Wavefront的.obj文件。而有的模型文件则采用XML来记录数据，且包含了丰富的模型、光照、各种材质、动画、摄像机信息和完整的场景信息等，比如Collada文件格式。Wavefront的obj格式是为了考虑到通用性而设计的一种便于解析的模型格式。建议去Wavefront的Wiki上看看obj文件格式是如何封装的。这会给你形成一个对模型文件格式的一个基本概念和印象。

## 模型加载库

现在市面上有一个很流行的模型加载库，叫做Assimp，全称为Open Asset Import Library。Assimp可以导入几十种不同格式的模型文件（同样也可以导出部分模型格式）。只要Assimp加载完了模型文件，我们就可以从Assimp上获取所有我们需要的模型数据。Assimp把不同的模型文件都转换为一个统一的数据结构，所有无论我们导入何种格式的模型文件，都可以用同一个方式去访问我们需要的模型数据。

当导入一个模型文件时，即Assimp加载一整个包含所有模型和场景数据的模型文件到一个scene对象时，Assimp会为这个模型文件中的所有场景节点、模型节点都生成一个具有对应关系的数据结构，且将这些场景中的各种元素与模型数据对应起来。下图展示了一个简化的Assimp生成的模型文件数据结构：


![](http://learnopengl.com/img/model_loading/assimp_structure.png)


 - 所有的模型、场景数据都包含在scene对象中，如所有的材质和Mesh。同样，场景的根节点引用也包含在这个scene对象中
 - 场景的根节点可能也会包含很多子节点和一个指向保存模型点云数据mMeshes[]的索引集合。根节点上的mMeshes[]里保存了实际了Mesh对象，而每个子节点上的mMesshes[]都只是指向根节点中的mMeshes[]的一个引用(译者注：C/C++称为指针，Java/C#称为引用)
 - 一个Mesh对象本身包含渲染所需的所有相关数据，比如顶点位置、法线向量、纹理坐标、面片及物体的材质
 - 一个Mesh会包含多个面片。一个Face（面片）表示渲染中的一个最基本的形状单位，即图元（基本图元有点、线、三角面片、矩形面片）。一个面片记录了一个图元的顶点索引，通过这个索引，可以在mMeshes[]中寻找到对应的顶点位置数据。顶点数据和索引分开存放，可以便于我们使用缓存（VBO、NBO、TBO、IBO）来高速渲染物体。（详见[Hello Triangle](http://www.learnopengl.com/#!Getting-started/Hello-Triangle)）
 - 一个Mesh还会包含一个Material（材质）对象用于指定物体的一些材质属性。如颜色、纹理贴图（漫反射贴图、高光贴图等）

所以我们要做的第一件事，就是加载一个模型文件为scene对象，然后获取每个节点对应的Mesh对象（我们需要递归搜索每个节点的子节点来获取所有的节点），并处理每个Mesh对象对应的顶点数据、索引以及它的材质属性。最终我们得到一个只包含我们需要的数据的Mesh集合。

!!! Important

    **网格(Mesh)**
    
    用建模工具构建物体时，美工通常不会直接使用单个形状来构建一个完整的模型。一般来说，一个模型会由几个子模型/形状组合拼接而成。而模型中的那些子模型/形状就是我们所说的一个网格。例如一个人形模型，美工通常会把头、四肢、衣服、武器这些组件都分别构建出来，然后在把所有的组件拼合在一起，形成最终的完整模型。一个网格（包含顶点、索引和材质属性）是我们在OpenGL中绘制物体的最小单位。一个模型通常有多个网格组成。

下一节教程中，我们将用上述描述的数据结构来创建我们自己的Model类和Mesh类，用于加载和保存那些导入的模型。如果我们想要绘制一个模型，我们不会去渲染整个模型，而是去渲染这个模型所包含的所有独立的Mesh。不管怎样，我们开始导入模型之前，我们需要先把Assimp导入到我们的工程中。

## 构建Assimp

你可以在[Assimp的下载页面](http://assimp.sourceforge.net/main_downloads.html)选择一个想要的版本去下载Assimp库。到目前为止，Assimp可用的最新版本是3.1.1。我们建议你自己编译Assimp库，因为Assimp官方的已编译库不能很好地覆盖在所有平台上运行。如果你忘记怎样使用CMake编译一个库，请详见[Creating a window(创建一个窗口)](http://www.learnopengl.com/#!Getting-started/Creating-a-window)教程。

这里我们列出一些编译Assimp时可能遇到的问题，以便大家参考和排除:

 - CMake在读取配置列表时，报出与DirectX库丢失相关的一些错误。报错如下：
 
```
Could not locate DirecX
CMake Error at cmake-modules/FindPkgMacros.cmake:110 (message):
Required library DirectX not found! Install the library (including dev packages) and try again. If the library is already installed, set the missing variables manually in cmake.
```

这个问题的解决方案：如果你之前没有安装过DirectX SDK，那么请安装。下载地址：[DirectX SDK](http://www.microsoft.com/en-us/download/details.aspx?id=6812)。

 - 安装DirectX SDK时，可能遇到一个错误码为<b>S1023</b>的错误。遇到这个问题，请在安装DirectX SDK前，先安装C++ Redistributable package(s)。
  问题解释：[已知问题：DirectX SDK (June 2010) 安装及S1023错误](https://blogs.msdn.microsoft.com/chuckw/2011/12/09/known-issue-directx-sdk-june-2010-setup-and-the-s1023-error/)。
  
 - 一旦配置完成，你就可以生成解决方案文件了，打开解决方案文件并编译Assimp库（编译为Debug版本还是Release版本，根据你的需要和心情来定吧）。
 
 - 使用默认配置构建的Assimp是一个动态库，所以我们需要把编译出来的assimp.dll文件拷贝到我们自己程序的可执行文件的同一目录里。
 
 - 编译出来的Assimp的LIB文件和DLL文件可以在code/Debug或者code/Release里找到。
 
 - 把编译好的LIB文件和DLL文件拷贝到工程的相应目录下，并链接到你的解决方案中。同时还好记得把Assimp的头文件也拷贝到工程里去（Assimp的头文件可以在include目录里找到）。

如果你还遇到了其他问题，可以在下面给出的链接里获取帮助。

!!! Important

    如果你想要让Assimp使用多线程支持来提高性能，你可以使用<b>Boost</b>库来编译 Assimp。在[Boost安装页面](http://assimp.sourceforge.net/lib_html/install.html)，你能找到关于Boost的完整安装介绍。

现在，你应该已经能够编译Assimp库，并链接Assimp到你的工程里去了。下一步：[导入完美的3D物件！](02 Mesh.md)
