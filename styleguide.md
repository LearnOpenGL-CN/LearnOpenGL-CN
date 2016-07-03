# 校对指南(Styleguide)

- **对照原文**
- 使用中文的标点符号: 逗号、句号、双引号
- 使用英文的标点符号: 括号
- 文本中常量/代码用``加注为代码
- 代码块不使用Tab标注，改为用```式标注
- 每一节标题使用`#` (h1)标题(到后面会有几节有很多小节的，太小的标题不明显)
	- 根据原文标题大小逐渐递增标题
	- 注意"#"后标题前要空格
- 专有名词在对照表里找翻译，需要用括号标注原文
	- 原文单词按照标题大写规则大写首字母
	- 尽量大部分都翻译掉
- 在Markdown文件中如需插入图片或者代码，请与正文空一行

例:

```markdown
[text]

[img]

[text]
```

- 翻译注释
- 原文中的斜体一律用加粗表示(中文并不存在斜体)，粗体也用粗体表示，注意不要自己添加粗体
- 每一节前面加上

```
原文     | [英文标题](原文地址)
      ---|---
作者     | [作者]
翻译     | [翻译]
校对     | [校对]
```

- 公式用[http://latex2png.com/](http://latex2png.com/)转换，文本中的公式Resolution为150，单独的公式为200
- 视频用Video标签添加

```html
<video src="url" controls="controls">
</video>
```

- 如果有比较长的译注:

```
xxxx(([译注x])

[译注x]: http://learnopengl-cn.readthedocs.org "text"
```
效果会像这样([译注1])

- “Additional resources”译作“附加资源”，“Exercises”译作“练习”，“Solution”译作“参考解答”

**如果有不全的继续加**

##专业词汇对照表

1. [《游戏引擎架构》中英词汇索引表](http://www.cnblogs.com/miloyip/p/GameEngineArchitectureIndex.html)

2. 摘抄自《OpenGL超级宝典第五版》

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

[译注1]: http://learnopengl-cn.readthedocs.org "bakabaka我是译注"