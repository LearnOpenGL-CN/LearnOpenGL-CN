# 代码仓库

你可以在每一篇教程中找到在线的代码范例，但如果你想自己运行教程的Demo或者将正常工作的范例代码与你的代码进行比较，你可以在[这里](https://github.com/JoeyDeVries/LearnOpenGL)找到在线的GitHub代码仓库。

目前，`CMakeLists.txt`文件能够正常生成Visual Studio的工程文件和make文件，它能够在Windows和Linux上运行。但是它在Apple的macOS和其它的IDE上还没有进行非常完全的测试，所以如果出现问题你可以留言或者帮忙通过Pull Request来更新一下`CMakeLists.txt`文件让它支持不同的系统。

我非常感谢Zwookie在制作Linux的CMake脚本时提供的巨大帮助。感谢Zwookie对CMakeLists的更新，现在它能够在Windows和Linux上生成工程文件了。

你也可以查看Polytonic的[Glitter](https://github.com/Polytonic/Glitter)，它是一个非常简单的样板工程，它提供了已经预配置好的相关依赖项。