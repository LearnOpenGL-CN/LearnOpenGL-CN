# 延迟渲染(Deferred Shading)

原文     | [Deferred Shading](http://learnopengl.com/#!Advanced-Lighting/Deferred-Shading)
      ---|---
作者     | JoeyDeVries
翻译     | Meow J
校对     | 未校对

我们现在一直使用的光照方式叫做正向渲染(Forward Rendering)或者正向着色法(Forward Shading)，它是我们渲染物体的一种非常直接的方式，在场景中我们根据所有光源照亮一个物体，之后再渲染下一个物体，以此类推。它非常容易理解，也很容易实现，但是同时它对程序性能的影响也很大，因为对于每一个需要渲染的物体，程序都要对每一个光源每一个需要渲染的片段进行迭代，这是**非常**多的！因为大部分片段着色器的输出都会被之后的输出覆盖，正向渲染还会在场景中因为高深的复杂度(多个物体重合在一个像素上)浪费大量的片段着色器运行时间。

**WIP**