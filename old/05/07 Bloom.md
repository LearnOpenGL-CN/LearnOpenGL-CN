本文作者JoeyDeVries，由Meow J翻译自[http://learnopengl.com](http://learnopengl.com/#!Advanced-Lighting/Bloom)

## 泛光(Bloom)

亮光源与被光照区域常常很难传达给观众，因为显示器的光强度范围是受限制的. 其中一个解决方案是让这些光源泛光(Glow)从而区分亮光源: 让光漏(bleed)出光源. 这有效让观众感觉到光源和光照区域非常的亮.

光的是通过一个后期处理效果叫做泛光(Bloom)来完成的. 泛光让所有光照地区一种在发光的效果.下面两个场景就是有泛光(右)与无泛光(左)的区别(图像来自于虚幻引擎(Unreal)):

![](http://learnopengl.com/img/advanced-lighting/bloom_example.png)

泛光提供了对于物体亮度显眼的视觉暗示，因为泛光能给我们物体真的是很亮的视觉效果. 如果我们能够很好的完成它(有一些游戏实现的很糟糕)，泛光将能很大程度的加强我们场景的光照效果，并且也能给我们很多特效.