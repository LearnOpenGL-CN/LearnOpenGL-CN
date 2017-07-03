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

- 在Markdown文件中如需插入图片或者代码，请与正文空**一行**以方便阅读及解析，每一个段落之间也应该空**一行**，例如：

```markdown
[text]

[text]

[img]

[text]
```

## 标点符号

- 一般情况下请使用中文的标点符号
- 引号请使用`「`和`」`
- 书名号请使用`『`和`』`
- 当标注翻译的原文时，括号请使用英文的括号（英文与周围空太多会有点难看），但其它情况下请用中文的括号，如

	OpenGL规范严格规定了每个函数该如何执行，以及它们的输出值。至于内部具体每个函数是如何实现(Implement)的，将由OpenGL库的开发者自行决定（注：这里开发者是指编写OpenGL库的人）。因为OpenGL规范并没有规定实现的细节，具体的OpenGL库允许使用不同的实现，只要其功能和结果与规范相匹配（亦即，作为用户不会感受到功能上的差异）。

## 代码

- 文本中常量/代码用``加注为代码
- 代码块不使用Tab标注，请用```式标注
- 代码的语言需要在代码一开始的标记处标识出来（一般都是C++），比如```c++
- 请记得翻译注释
- 注释与`//`间请加一个空格
- 原文的代码看起来像是加粗，如果真的是代码则用代码，如果不是则用加粗（比如原文中的VS的选项及文件夹）

## 图片

- 图片请尽量搬运到`docs/img`目录，之后在文中引用的时候地址填写`../img/filename.jpg`：

```markdown
![](../img/[小节]/[教程]/filename.jpg)
```

- 如果想要让图片放在页面一侧，可以使用HTML代码，注意HTML代码中要多一层`../`，**如果没有特殊效果的话请使用原本的Markdown图片**：

```html
<img alt="OpenGL Logo" src="../../img/opengl.jpg" class="right" />
```

- 如果图片有背景颜色的话请使用tools目录下的`ClearBG.py`清除为透明

其他的class名称还有：

- clean
- left
- right
- small
- medium
- large

## 标题

- 每一节标题使用`#`（h1）标题(到后面会有几节有很多小节的，太小的标题不明显)
	- 根据原文标题大小逐渐递增标题
	- 注意`#`后与标题前要加一个空格
- 标题不要添加翻译，对于名词的翻译请写在文中

## 链接

- 所有的引用链接请使用相对链接，地址为从当前文件目录转到引用文件的相对地址（文件名结尾为`.md`）

## 列表

- 列表请与其他元素之间空一行，否则解析会出错。

## 专有名词

- 专有名词需要在第一次出现的之后用括号标注原文
	- 原文单词按照标题大写规则**大写首字母**
- 翻译
	- 首先，请与本工程中大部分的翻译保持一致
	- 如果工程中找不到已有的翻译，请参考本文档最下面的词汇表寻找翻译
	- 如果还是找不到，可以自己创造一个翻译，或者直接写英文
- 「Additional resources」译作「附加资源」，「Exercises」译作「练习」，「Solution」译作「参考解答」

## 特殊元素

- 已经安装MathJax插件，如果想要添加数学公式的话直接使用代码就行了：

如果是行内的数学公式：

```
\(...\)
```

如果是独立的数学公式：

```
$$
...
$$
```

数学公式可以通过右击原文中的公式Show Math As->Tex Commands，复制弹出窗口内的代码获得。

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

- 原文中的红色方框请用`!!! attention`标注，绿色方框请用`!!! important`标注，注意文本前有**一个**Tab，格式如下：

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

- 如果方框中有代码块，请将代码复制进来之后前面加**两个**Tab，记得将代码块和正文中间空一行（空行，不用加任何空格和Tab）：

```
!!! important

	[text]

		[code]

	[text]
```

## 特殊词汇标记

- 定义：`<def>Definition</def>`
- 函数及类名：`<fun>Program logic</fun>`
- 变量：`<var>Variables</var>`
- 下划线：`<u>Underline</u>`
- **定义**在标记的时候仅仅标记中文翻译，**不要**标记括号中的原文，原则是只将最少的文字标记出来
- 函数和变量在标记的时候记得不要把中文翻译标记进去了
- 原文中的斜体如果译成中文一律用加粗表示（中文并不存在斜体），如果仍留为英文，请在单词两侧都添加空格与中文分开再改为斜体，粗体也用粗体表示，注意不要自己违反原文添加粗体

## 专业词汇对照表

1. [专有词汇翻译记录](https://github.com/LearnOpenGL-CN/LearnOpenGL-CN/blob/new-theme/glossary.md)
2. [微软术语搜索](https://www.microsoft.com/Language/zh-cn/Search.aspx)
3. [《游戏引擎架构》中英词汇索引表](http://www.cnblogs.com/miloyip/p/GameEngineArchitectureIndex.html) 
4. 摘抄自《OpenGL超级宝典第五版》：

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