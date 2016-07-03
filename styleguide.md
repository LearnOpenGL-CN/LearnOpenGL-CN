# 样式指南

这里是LearnOpenGL中文化工程的样式指南，在编写新的翻译或者校对之前请先阅读此文档，以确定你的翻译符合要求。

## 基础

- **对照原文，以原文为准**
- 必要时可以使用HTML代码
- 每一节前面加上

```
原文     | [英文标题](原文地址)
      ---|---
作者     | JoeyDeVries
翻译     | [翻译]
校对     | [校对]
```

- 在Markdown文件中如需插入图片或者代码，请与正文空一行以方便阅读及解析，例如：

```markdown
[text]

[img]

[text]
```

## 标点符号

- 一般情况下请使用中文的标点符号
- 当标注翻译的原文时，括号请使用英文的括号（英文与周围空太多会有点难看），但其它情况下请用中文的括号，如

	OpenGL规范严格规定了每个函数该如何执行，以及它们的输出值。至于内部具体每个函数是如何实现(Implement)的，将由OpenGL库的开发者自行决定（注：这里开发者是指编写OpenGL库的人）。因为OpenGL规范并没有规定实现的细节，具体的OpenGL库允许使用不同的实现，只要其功能和结果与规范相匹配（亦即，作为用户不会感受到功能上的差异）。

- 原文中的斜体一律用加粗表示（中文并不存在斜体），粗体也用粗体表示，注意不要自己违反原文添加粗体

## 代码

- 文本中常量/代码用``加注为代码
- 代码块不使用Tab标注，请用```式标注
- 代码的语言在标识出来，比如```c++
- 请记得翻译注释


## 标题

- 每一节标题使用`#`（h1）标题(到后面会有几节有很多小节的，太小的标题不明显)
	- 根据原文标题大小逐渐递增标题
	- 注意`#`后与标题前要加一个空格

## 专有名词

- 专有名词需要在第一次出现的之后用括号标注原文
	- 原文单词按照标题大写规则大写首字母
- 翻译
	- 首先，请与本工程中大部分的翻译保持一致
	- 如果工程中找不到已有的翻译，请参考本文档最下面的词汇表寻找翻译
	- 如果还是找不到，可以自己创造一个翻译，或者直接写英文
- “Additional resources”译作“附加资源”，“Exercises”译作“练习”，“Solution”译作“参考解答”

## 特殊元素

- 公式用[http://latex2png.com/](http://latex2png.com/)转换，文本中的公式Resolution为150，单独的公式为200
- 视频用Video标签添加

```html
<video src="url" controls="controls">
</video>
```

- 短的译注直接用中文括号插入文中标明译注即可，例如：

```
文本（译注：[text]）
```

- 如果有比较长的译注，请将以下标记插入文本的段落之后:

```
!!! note "译注"

	[text]
```

- 原文中的红色方框请用`!!! attention`标注，绿色方框请用`!!! important`标注，注意文本前有个Tab，格式如下：

红色方框：

```
!!! attention

	[text]
```

绿色方框：

```
!!! important

	[text]
```

## 专业词汇对照表

1. [微软术语搜索](https://www.microsoft.com/Language/zh-cn/Search.aspx)
2. [《游戏引擎架构》中英词汇索引表](http://www.cnblogs.com/miloyip/p/GameEngineArchitectureIndex.html) 
3. 摘抄自《OpenGL超级宝典第五版》：

英文词 | 对应翻译
---|---
Aliasing | 锯齿
Alpha | 透明度
Ambient Light|环境光
Antialiasing|抗锯齿
Aspect Ratio|纵横比
Bezier curve|贝塞尔曲线
Bitplane|位平面
Buffer|缓冲区
Cartesian|笛卡尔
Clip coordinates|裁剪坐标
Clipping|裁剪
Convex|凸
Culling|剔除
Destination color|目标颜色
Dithering|抖动
Double buffered|双缓冲
Extruded|拉伸
Eye coordinates|视觉坐标
Frustum|平头截体
Immediate mode|立即模式
Implementation|实现
Khronos|OpenGL维护小组
Literal|字面值
Matrix|矩阵
Mipmapping|Mip贴图
Modelview Matrix|模型视图矩阵
Normal|法线
Normalize|规范化
Orthographic|正交
Prespective|透视
Piexl|像素
Pixmap|像素图
Polygon|多边形
Primitive|图元
Projection|投影
Quadrilateral|四边形
Resterize|光栅化
Retained mode|保留模式
Render|渲染
Scintillation|闪烁
Shader|着色器
Source Color|源颜色
Specification|说明
Spline|样条
Stipple|点画
Tessellation|镶嵌
Texel|纹理单元
Texture|纹理
Transformation|变换
Translucence|半透明
Vector|向量
Vertex|顶点
Viewing Volume|可视区域
Viewport|视口
Wireframe|线框
pipeline | 渲染管线

[译注1]: http://learnopengl-cn.readthedocs.org "这里是很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长的译注"