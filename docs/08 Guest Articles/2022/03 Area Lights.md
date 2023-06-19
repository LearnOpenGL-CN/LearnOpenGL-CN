# 区域光

 原文 | [Area Lights](https://learnopengl.com/Guest-Articles/2022/Area-Lights) 
 ---- | ------------------------------------------------------------ 
 作者 | [Alexander Christensen](https://www.linkedin.com/in/alexanderchr/) 
 翻译 | [XDzZyq](https://github.com/XDzzzzzZyq)                      
 校对 | 暂无                                                         

![article_image](../../../img/08/03/03/01article_image.png)

<center>有纹理的矩形区域光[1]</center>

# 前言

光线无处不在。同样，合适的灯光在渲染中也十分重要。

目前为止我们已经在第三章中[【投光物】](https://learnopengl-cn.github.io/02%20Lighting/05%20Light%20casters/)这一节学习了三种截然不同的灯光类型：<def>平行光、点光和聚光</def>。但是在现实生活中的光源通常具有一定范围和面积，而以上三种光源要么是来自一点，要么光线在空间中各个位置相同（平行光）。

很显然我们无法通过以上三种光源去实现一种具有面积的光源。假设我们需要一个矩形光源，如果仅用点光或聚光实现，则需要成千上万的微小光源阵列在这个矩形区域中。又即使我们成功创建了这些光源，很明显，为了追求实时渲染的性能要求，渲染结果肯定不尽如人意（如果相机非常接近矩形光源，我们甚至可能还需要更密的灯光）。除此之外又可能出现的照明过度，所以为了能量守恒，每个光源的亮度又需要尽可能的小。很明显这种实现方式是不合理的。因此我们需要一种新的灯光类型：<def>区域光</def>。

这种具有区域的光源在离线渲染中，通过蒙特卡洛采样，使用光线追踪可以相对简单粗暴地解决这个问题。但是本篇教程主要面向实时渲染领域，上述离线渲染的实现方式在本文中不会被提及。

本篇教程描述了一种使用<def>线性变换余弦分布集</def>(Linearly Transformed Cosines)的方法从任意凸多面体中渲染区域光。该方法最初由Eric Heitz、Jonathan Dupuy、Stephen Hill和David Neubelt在SIGGRAPH2016年发表。后续人们又对该方法进行了拓展，除了矩形或多面体外又支持了圆形光源。

在本文中，我们将主要研究矩形区域光的具体实现方法。

## 前置知识

区域光渲染是基于<def>物理渲染</def>(PBR)的，因此建议在开始学习前先熟悉其核心概念，以获得最佳学习体验。此外这个方法涉及到非常多的数学知识，建议先熟悉几个数学概念：积分、线性代数、三角函数、立体角角度测量和球面分布函数。不过如果你仅仅是想实现区域光，那么你完全可以直接复制文中【整体实现】所给出的代码。实现区域光所需要的理论知识比较深奥，刨根问底可能是值得的，但是不完全理解其原理不会影响应用。研究人员已经为帮我们完成了复杂的推导过程，感谢他们让我们的渲染看起来很酷！ :) 

你可能还注意到封面图像有一个带纹理的光源。不过本文不会详细介绍如何实现这一点，尽管可能会在未来的章节中提及。所以让我们开始吧！

!!! important
	文末参考文献中有相关论文和实现原理

假设我们有一个场景，并在场景中的某个位置放置一个矩形。我们希望这个矩形表示一个光源并发射光线。除此之外还有物理渲染中的BRDF函数，它描述了场景中表面如何散射光线（或者出射光和每条入射光间的比例）。 

在渲染的时候，我们需要解决BRDF的积分，积分范围是自发光多面体（区域光源）在单位半球面围绕着着色点形成的立体角，以计算出射<def>辐照度</def>(Irradiance)。这个出射辐照度将反射回摄像机，从而完成渲染。

在论文中描述了如何将线性变换作用于球面分布函数，从而构造一系列可以拟合不同材质和摄像机视角下BRDF特性的球面分布函数。这些特性在Eric Heitz的PPT[3]中有很好的表现。但由于本教程主要面向程序的实现，所以不会在这里画太多篇幅讲解理论推导。这些经过不同矩阵变换出的分布函数被统称为"线性变换余弦分布集"(Linearly Transformed Cosines)，之所以是“余弦”是因为所有的分布函数是来自一个变换后的受约余弦分布函数，同时具有近似的BRDF的重要特性。"受约"指的是余弦分布函数（或Lambertian分布）仅考虑正半球面。这很重要，因为单位球面固体角度测量值在区间[0, 4π]内，而光源可能永远不会照亮水平面以下的区域；因此我们将余弦分布函数约束到正半球面（上半球）（以入射着色点的表面法线为中心）。

在物理渲染(PBR)中我们学到，GGX微表面模型中的BRDF分布函数具有复杂的形状。比如在接近入射角度处的各向异性拉伸、偏斜度和不同程度的材质粗糙度等特性。正是由于这些特性，BRDF能够产生写实的渲染效果。所以如果我们能够设计一个线性变换，通过矩阵乘法将这些特性添加到受约余弦分布中，那么我们就可以获得媲美BRDF的效果。论文[1]中描述了如何实现这一点。余弦分布是一个非常好的选择，因为我们对其积分有一个闭合形式（Closed-Form）的表示：
$$
D_o(ω_o)=\frac1π\cosθ_o
$$
总结一下，我们的目标是：构建一个三乘三线性变换矩阵并将其应用在受约余弦分布函数上，从而近似某一条件下BRDF分布函数。然后在区域光所在的立体角上进行计算并获得渲染结果。

在线性代数中，我们可以在两个矩阵中应用乘法，同样也可以进行逆运算：
$$
A×B=C~~~~~~~~~~⇔~~~~~~~~~~C×B^{−1}=A
$$
如果我们为了得到了BRDF将矩阵M应用于余弦分布，那么我们可以逆运算，从而优雅地解决立体角的球面积分。下面的示意图展示了这个思想。正如论文作者建议的那样，我们可以将其视为变换回初始的余弦空间。

![inverse_transformation](../../../img/08/03/03/02inverse_transformation.png)

<center>反向变换回余弦空间，使用逆线性变换矩阵[2]</center>

# 构建变换矩阵

线性变换矩阵M需要能够表示BRDF的特性，比如在不同观察角度和材质粗糙度上矩阵M需要进行参数化。如下图：

![matrix_construction](../../../img/08/03/03/03matrix_construction.png)

<center>通过矩阵连乘构建线性变换，从而获得想要的BRDF特性[2]</center>

<def>粗糙度</def>(roughness)直接从材质的粗糙度纹理中获取，<def>各向异性</def>(anisotropy)和<def>偏斜度</def>(skewness)来自于摄像机和表面法线的夹角，从而实现逼真的渲染效果。如上图所示，我们可以根据需求和要表示的特定BRDF模型选择任意程度的变换。在本教程中，我们将使用一个矩阵来近似GGX微表面模型。如前文所述，我们需要为每个粗糙度和观察角度的组合计算一个矩阵M。不仅如此，我们还需要对矩阵进行多次采样，从而最小化与目标BRDF的误差。显然，这对于实时渲染来说是不可行的，因此需要预先计算在不同粗糙度/观察角度下的矩阵M。由于矩阵M及其逆矩阵都是稀疏矩阵，只有5个非零值，我们可以通过归一化来将逆矩阵存储在一个4维向量中。这在实践中效果很好，并且可以将矩阵信息以2D纹理的形式传入到shader中去查表。本教程中我们选择一个64x64的纹理来节省显存。

# 计算积分

前文我们提到，计算区域光时我们需要在区域光所在立体角内积分<def>辐射度</def>(Radiance)，但是在实际操作中我们仅需要沿多面体光源的边缘进行积分。这个积分的等价转换过程十分神奇，不过由于教程篇幅的原因我仅引用一句ppt中的原话，希望读者进一步的了解：

<center>“其中一种理解方法是斯托克斯定理(Stoke’s theorem)的应用，你可能在其他领域遇到过，比如流体模拟。”</center>

<def>斯托克斯定理</def>讲的是：在向量场中，场中一个闭合曲线上的线积分等于其所围面积中<def>散度</def>(Curl)的<def>通量</def>(Flux)之和[11]。同理在对区域光光源的积分中，给定光源中任意两个顶点v1和v2，我们需要对下式进行积分求和：

$$
\arccos(v_1⋅v_2)\frac{v_1×v_2}{\|v_1×v_2\|}⋅n
$$


对于具有N个顶点的整个区域光光源来说，我们可以根据上式将全部边缘求和来准确地计算出该区域光所构成的立体角：


$$
∫_Ω≈\frac1{2π}∑_i\frac1N[\arccos(v_1⋅v_2)\frac{v_1×v_2}{\|v_1×v_2\|}⋅n]
$$

!!! note "译注"

	具体公式推导可以参考文末延伸阅读中的中文笔记[14]

下图中，向量v1和v2是从着色点到多面体光源的顶点的方向向量，“acos(v1·v2)”是投影到位于着色点附近的单位球体上的多面体弧长（以弧度为单位），向量u为归一化叉积所产生的垂直于v1和v2的单位向量。我们用着色点的法向量和向量u，将光源投影到与着色点相切的平面上，该平面的法向量为n。

![edge_area_integral](../../../img/08/03/03/04edge_area_integral.png)

<center>应用斯托克斯定理，通过边缘积分来计算转换后的光源积分[2]</center>

除此之外，根据PPT[2]中所描述的，计算反余弦函数时造成的精度丢失会导致明显的瑕疵。论文中的解决方法是通过一个三次函数来近似反余弦函数。不过本教程中所采用的拟合函数跟ppt[2]所写的有所不同，这个版本的拟合效果更好。关于边缘积分的代码请参考如下：

```glsl
float IntegrateEdge(vec3 v1, vec3 v2, vec3 N) {
    float x = dot(v1, v2);
    float y = abs(x);
    float a = 0.8543985 + (0.4965155 + 0.0145206*y)*y;
    float b = 3.4175940 + (4.1616724 + y)*y;
    float v = a / b;
    float theta_sintheta = (x > 0.0) ? v : 0.5*inversesqrt(max(1.0 - x*x, 1e-7)) - v;
    return dot(cross(v1, v2)*theta_sintheta, N);
}
```

## 将多面体裁剪到正半球面

上述的<fun>IntegrateEdge</fun>函数虽然是一个很好的解决方案，但有待提升。为了获得正确的辐照度，我们需要将变换后的余弦分布约束到上半球。这个过程也可以被称为“水平面裁剪”，涉及到很多分支。如下图：

![horizon_clipping](../../../img/08/03/03/05horizon_clipping.png)

如果光源多面体在水平面（相对于物体表面）以下，或者部分在水平面以下，这个多面体则需要被修正（裁剪）到上半球面。理论上来说，修正方法是将存在问题的每条边的较低的顶点上移，使其不再位于水平面以下。如果一条边完全位于水平面以下，则需要将其整体上移。最后以上判断条件下，计算所得到的边缘积分将小于修正前的值（甚至等于零），从而减少出射辐照度。但是，如果我们需要对所有边的每个顶点进行上述判断，shader中会增加许多分支语句（if-else）进而影响渲染性能。因此我们需要从公式入手，继续修改边缘积分的公式：删除与表面法向量的点积（从而不投影到平面上）。修正后的公式如下：


$$
\arccos(v_1⋅v_2)\frac{v_1×v_2}{\|v_1×v_2\|}
$$


需要注意的是，现在积分的结果是一个向量（与法向量点乘的前一步），我们可以将其视为向量形式因子或向量辐照度。我们将其称为向量F，向量F有一个比较明显的特性：向量F的模长为该光源在F方向上的辐照度的大小[2]。此外，我们假想释放辐照度大小为||F||的光源来自一个球体（Proxy Sphere），通过向量F我们可以得出该圆面相对余弦分布函数的张角和倾斜度。公式如下：


$$
\vec F=\arccos(v_1⋅v_2)\frac{v_1×v_2}{\|v_1×v_2\|}\\
辐照度大小=\|\vec F\|\\
张角=\arcsin\sqrt{\|\vec F\|}\\
倾斜度=n\cdot \frac{\vec F}{\|\vec F\|}
$$


![edge_area_integral](../../../img/08/03/03/051edge_area_integral.png)

通过构造<def>假想球体</def>(Proxy Sphere)我们可以完美解决上半球面修正的问题。不仅如此，通过预计算修正后的辐照度和修正前的比例与其张角和倾斜度的关系，我们可以得到第二张纹理LUT。在渲染过程中通过查表可以直接获得这一比例关系，从而高效地近似计算正半球修正。更多细节详见[1] [2]。

!!! important
	向量F的模长表示着色点接受的总辐照度，从面积A传输到面积B。这一点类似于我们将多面体光源的辐照度转换为多面体在经过半球面上立体角所的辐照度的过程。不过物体表面接收的辐照度受正半球修正和光源倾斜度的影响，这个比例关系被存储在了一个64×64的LUT中，横纵坐标分别为假想球体的张角和倾斜度。上文中之所以用“向量辐照度”作为向量F的名词，是因为作者想强调入射光的能量。对于向量F更完备的表述详见[13]

# 整体实现

恭喜大家已经完成了漫长的理论环节！如果没有完全理解也没关系，如下的代码直接复制粘贴也可以快速让你实现区域光。（如果你想继续挑战理论推导，可以看一看文末的参考资料）。接下来我们来整点有意思的。第一步是载入前文提到的那两个LUT，作为2D纹理存储在GPU里。在载入的过程中确保开启双线性插值以保证平滑采样，然后约束以保证读取的时候不会超过LUT的范围。

```c++
#include "ltc_matrix.hpp" // 包含了float数组 LTC1 和 LTC2

unsigned int loadMTexture(float* matrixTable) {
    unsigned int texture = 0;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_FLOAT, matrixTable);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glBindTexture(GL_TEXTURE_2D, 0);
    return texture;
}

unsigned int m1 = loadMTexture(LTC1);
unsigned int m2 = loadMTexture(LTC2);
```

上述函数所需要的逆变换矩阵作者已经很友好地为我们预先计算了它们，可以在[这里](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/ltc_matrix.hpp)找到C++头文件，或者你也可以通过从[4]下载源代码来生成它们。我们还可以将它们作为DXT10压缩图像（.dds）加载。教程作者选择了C++头文件，因为大多数图像加载库不支持DXT10压缩（文件头没有标准化！）。虽然在学习时使用头文件存储数据很方便，但在发布游戏时最好使用.dds图像。

第一个LUT纹理包含如前文所述的逆转换矩阵，而第二个LUT纹理包含Fresnel90、水平剪裁因子和几何衰减的Smith系数（总共3个值）。我们在渲染时将这两个纹理绑定到Shader中：

```c++
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, m1);
glActiveTexture(GL_TEXTURE1);
glBindTexture(GL_TEXTURE_2D, m2);
```

除此之外我们还需要创建一个<def>顶点缓冲</def>(Vertex Buffer)来存储多面体光源的多面体。为了简化和技术演示，场景最好只有一个水平的地面组成，灯光的话最好是矩形。具体的C++实现代码详见[这里](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/1.area_light/area_lights.cpp)。

## Shader

<def>片元着色器</def>(Fragment Shader)是重中之重。在这里，我们采样LUT来构造逆矩阵，并检索几何衰减系数。我们还需要在物体表面的切空间中构造了正交变换矩阵，并计算边缘积分。所以我们需要一些参数输入和常规渲染的必要环节，比如材料和光源的信息。完整的代码如下所示：

```glsl
#version 330 core

out vec4 fragColor;

in vec3 worldPosition;
in vec3 worldNormal;
in vec2 texcoord;

struct Light {
    float intensity;
    vec3 color;
    vec3 points[4];
    bool twoSided;
};

uniform Light areaLight;
uniform vec3 areaLightTranslate;

struct Material {
    sampler2D diffuse; // 纹理映射
    vec4 albedoRoughness; // (x,y,z) = 颜色, w = 粗糙度
};
uniform Material material;

uniform vec3 viewPosition;
uniform sampler2D LTC1; // 用于构建逆变换矩阵M
uniform sampler2D LTC2; // GGX预积分, 菲涅尔, 0(unused), 几何衰减

const float LUT_SIZE = 64.0; // LUT大小
const float LUT_SCALE = (LUT_SIZE - 1.0)/LUT_SIZE;
const float LUT_BIAS = 0.5/LUT_SIZE;
```

变量<fun>areaLightTranslate</fun>是作者用来移动光源的参数，作为演示并不一定需要。然后那些常量是采样LUT的时候需要的。其余的部分相比你已经很熟悉了。

!!! important
	LUT是图形学经常遇到的概念，它是Look-Up Table的简称，而且大多数情况以纹理贴图的形式在shader中发挥作用。结构体<var>Material</var>仅包含三通道的颜色信息和一通道的粗糙度信息。如果你采用延迟渲染，这种压缩方式非常有用。虽然颜色信息在本案例中未被使用，且物体的粗糙度是个定值，在大多数PBR渲染管线中粗糙度可以是表面纹理的形式。

接下来是准备索引LUT所用的参数，进而构建uv坐标然后构建变换矩阵：

```glsl
vec3 N = normalize(worldNormal);
vec3 V = normalize(viewPosition - worldPosition);
vec3 P = worldPosition;
float dotNV = clamp(dot(N, V), 0.0f, 1.0f);

// 通过粗糙度和sqrt(1-cos_theta)采样M_texture
vec2 uv = vec2(material.albedoRoughness.w, sqrt(1.0f - dotNV));
uv = uv*LUT_SCALE + LUT_BIAS;

// 获得inverse_M的四个参数
vec4 t1 = texture(LTC1, uv);

// 获得用于计算菲涅尔的两个参数
vec4 t2 = texture(LTC2, uv);

mat3 Minv = mat3(
    vec3(t1.x, 0, t1.y),
    vec3(   0, 1,    0),
    vec3(t1.z, 0, t1.w)
);
```

为了计算立体角，我们一共需要两个函数：一个用来计算单个边缘的积分，另一个是多次调用该函数并对结果求和，然后执行正半球修正。边缘积分函数是其中最短的，正如本教程前面所示，唯一的区别是我们现在不执行点积，而只返回叉积乘以弧长。另一个函数相当长，下面有完整的代码和一些描述计算的注释。

```glsl
vec3 IntegrateEdge(vec3 v1, vec3 v2, vec3 N) {
    float x = dot(v1, v2);
    float y = abs(x);
    float a = 0.8543985 + (0.4965155 + 0.0145206*y)*y;
    float b = 3.4175940 + (4.1616724 + y)*y;
    float v = a / b;
    float theta_sintheta = (x > 0.0) ? v : 0.5*inversesqrt(max(1.0 - x*x, 1e-7)) - v;
    return cross(v1, v2)*theta_sintheta;
}
```

```glsl
vec3 LTC_Evaluate(vec3 N, vec3 V, vec3 P, mat3 Minv, vec3 points[4], bool twoSided) {
    // 构建TBN矩阵的三个基向量
    vec3 T1, T2;
    T1 = normalize(V - N * dot(V, N));
    T2 = cross(N, T1);

    // 依据TBN矩阵旋转光源
    Minv = Minv * transpose(mat3(T1, T2, N));

    // 多边形四个顶点
    vec3 L[4];

    // 通过逆变换矩阵将顶点变换于 受约余弦分布 中
    L[0] = Minv * (points[0] - P);
    L[1] = Minv * (points[1] - P);
    L[2] = Minv * (points[2] - P);
    L[3] = Minv * (points[3] - P);

    // use tabulated horizon-clipped sphere
    // 判断着色点是否位于光源之后
    vec3 dir = points[0] - P; // LTC 空间
    vec3 lightNormal = cross(points[1] - points[0], points[3] - points[0]);
    bool behind = (dot(dir, lightNormal) < 0.0);

    // 投影至单位球面上
    L[0] = normalize(L[0]);
    L[1] = normalize(L[1]);
    L[2] = normalize(L[2]);
    L[3] = normalize(L[3]);

    // 边缘积分
    vec3 vsum = vec3(0.0);
    vsum += IntegrateEdgeVec(L[0], L[1]);
    vsum += IntegrateEdgeVec(L[1], L[2]);
    vsum += IntegrateEdgeVec(L[2], L[3]);
    vsum += IntegrateEdgeVec(L[3], L[0]);

    // 计算正半球修正所需要的的参数
    float len = length(vsum);

    float z = vsum.z/len;
    if (behind)
        z = -z;

    vec2 uv = vec2(z*0.5f + 0.5f, len); // range [0, 1]
    uv = uv*LUT_SCALE + LUT_BIAS;

    // 通过参数获得几何衰减系数
    float scale = texture(LTC2, uv).w;

    float sum = len*scale;
    if (!behind && !twoSided)
        sum = 0.0;

    // 输出
    vec3 Lo_i = vec3(sum, sum, sum);
    return Lo_i;
}
```

确实有些长，不过如果你理解了原理的话其实挺合理的。除此之外还有一点没提到的是变量<var>twoSided</var>，通过传入这个参数来控制开启/关闭区域光的双向照明。完整的代码在[这里](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/1.area_light/7.area_light.fs)

## 结果

[这里](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/1.area_light/area_lights.cpp)是C++代码，这份代码加上前文提供的shader和头文件即可运行。作者还额外增加了一些功能：

- 按住R/Shift+R以减小/增加材料粗糙度。
- 按住I/Shift+I以降低/增加光强度。
- 使用箭头键移动光源。
- 使用B启用/禁用双面照明。
- 使用WASD键移动相机，通过鼠标旋转相机。还支持使用鼠标滚轮进行缩放。

作者还增加了地面贴图让场景看起来更真实。如果编译成功你大概率可以看到如下结果：

![program_example](../../../img/08/03/03/06program_example.png)

# 评估性能

结果看起来不错，不过也许你更想知道：

- 如果添加更多灯光会如何
- 渲染性能如何

显然，根据图形硬件的不同，这两个问题可能会有不同的答案。但总的来说测试起来很简单：我们给shader传入一个数组来表示几个区域光，我们可以使用[OpenGL队列](https://www.khronos.org/opengl/wiki/Query_Object)来进行基准测试。这是一个有趣的案例因为区域光需要大量的计算——比其它类型的光源要多得多。比如对于点光源的测试，我们可以窗前100-200个并且采用向前渲染仍然具有可接受的帧率，但这对于区域光源来说是不可行的。因此如果你想发布一款游戏，通过性能评估来规划照明占用的性能十分重要。OpenGL队列的常规设置如下所示：

```c++
GLuint timeQuery;
glGenQueries(1, &timeQuery);

GLuint64 totalQueryTimeNs = 0;
GLuint64 numQueries = 0;

while (!glfwWindowShouldClose(window))
{
    [...]

    glBeginQuery(GL_TIME_ELAPSED, timeQuery);
    renderPlane();
    glEndQuery(GL_TIME_ELAPSED);

    GLuint64 elapsed = 0; // will be in nanoseconds
    glGetQueryObjectui64v(timeQuery, GL_QUERY_RESULT, &elapsed);
    numQueries++;
    totalQueryTimeNs += elapsed;
}

double measuredAverageNs = (double)totalQueryTimeNs / (double)numQueries;
double measuredAverageMs = measuredAverageNs * 1.0e-6;
std::cout << "Total average time(ms) = " << measuredAverageMs << '\n';
```

上述测试方式比较初级，没有考虑异常值或方差。不过重要是统计结果从纳秒变成了毫秒。

片元着色器将使用循环在遍历所有光源。但是我们可以重复利用其中的一些数据，比如我们不需要对每个光源执行LUT纹理查找。着色器的更改部分现在看起来如下：

```glsl
struct AreaLight
{
    float intensity;
    vec3 color;
    vec3 points[4];
    bool twoSided;
};
uniform AreaLight areaLights[16];
uniform int numAreaLights;

// [...]

void main() {
    // [...]
    for (int i = 0; i < numAreaLights; i++)
    {
        // Evaluate LTC shading
        vec3 diffuse = LTC_Evaluate(N, V, P, mat3(1), areaLights[i].points, areaLights[i].twoSided);
        vec3 specular = LTC_Evaluate(N, V, P, Minv, areaLights[i].points, areaLights[i].twoSided);

        // GGX BRDF shadowing and Fresnel
        specular *= mSpecular*t2.x + (1.0f - mSpecular) * t2.y;

        // Add contribution
        result += areaLights[i].color * areaLights[i].intensity * (specular + mDiffuse * diffuse);
    }

    fragColor = vec4(ToSRGB(result), 1.0f);
}
```

!!! important
	我们必须在OpenGL中指定一个固定长度的统一数组，即使实际情况中灯光数量不会那么多。因此，我们将<var>numAreaLights</var>设置为一个等于或小于最大允许光源数量的数字，在以上例子中为16。

!!! note "译注"
	如果有使用不定长数组的去修，可以使用Shader Storage Buffer SSBO 

根据你的需求，可以使用多种不同的方式搭建测试程序。程序的核心是创建一个区域光位置阵列，并将它们输入到shader中。如何实现这一点在[【多光源】](https://learnopengl-cn.github.io/02%20Lighting/06%20Multiple%20lights/)一节中进行了讲解。一下为作者所展示的基础性能测试结果：

| # area lights | Avg. rendering time (ms) |
| :-----------: | :----------------------: |
|       1       |         0.557326         |
|       2       |         0.897486         |
|       4       |         2.32212          |
|       8       |          3.9175          |
|      12       |         4.37243          |
|      16       |         3.95511          |
|      24       |         4.50246          |
|      32       |         5.67573          |

![multiple_benchmark](../../../img/08/03/03/07multiple_benchmark.png)

![multiple_lights](../../../img/08/03/03/08multiple_lights.png)

[这里](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/2.multiple_area_lights/multiple_area_lights.cpp)是测试用的源码，当然还有[修改后的shader](https://learnopengl.com/code_viewer_gh.php?code=src/8.guest/2022/7.area_lights/2.multiple_area_lights/7.multi_area_light.fs)

### 小节

虽然这个演示不是很精美，但不妨碍从中得出一些结论：

- 灯光是伪随机放置在纹理平面周围的。
- 这些测试是在2015年的“NVIDIA GeForce GTX 850M”笔记本电脑GPU上进行的。你可能会有更好的测试结果。
- 这些灯光是使用向前渲染的。
- 在执行这些基准测试时，我经历了很多变数。还有很多因素需要考虑，比如驱动的影响，程序在执行什么操作等等。上面的图表显示了总体趋势，渲染时间随灯光数量大致呈线性的增长。
- 在渲染函数前后添加<fun>glBeginQuery(GL_TIME_ELAPSED)</fun>和<fun>glEndQuery(GL_TIME_ELAPSED)</fun>来记录测试数据。查询记录的结果可以用<fun>glGetQueryObjectui64v</fun>获得，并从纳秒转换为毫秒以计算平均值。

这里特别有趣的关于正向渲染的要点：在这个演示场景中只有纹理平面（忽略显示光源的彩色平面）有<def>绘制调用</def>(Draw Call)。但如果有许多对象需要渲染，即计算每个光源、每个片片元、每个网格的亮度贡献，则这样的管线是非常低效的，因为深度测试会导致大量片元被覆盖。所以更好的实现方法是使用延迟渲染，这意味着无论绘制的对象数量如何，需要计算照明的片元紧跟屏幕大小有关。

如果继续沿用向前渲染，则可以调用一个<def>计算着色器</def>(Compute Shader)，该着色器将屏幕空间划分为小区块，并为每个区块分配一个区域光列表（即向前渲染plus），以进行进一步优化。不过这个管线的基础是我们需要为每个区域光定义一个最大衰减半径时。这已经在虚幻引擎中完成（请参见[矩形区域光](https://docs.unrealengine.com/5.0/en-US/rectangular-area-lights-in-unreal-engine/)）。

# 其他灯光类型

除了矩形和多面体光源，还可以实现其他类型的区域光源例如条形灯或柱面灯。尽管超出了本文的范围，但数学基础可以在[12]中找到。作者本人并没有尝试实现，因此无法谈论其渲染性能或实施细节。不过为了完整起见此处稍微提一嘴巴。除此之外作者还发现了一些包括圆形区域灯的演示。

# 总结

感谢您的阅读。作者和译者都希望你喜欢并从这一节学到了一些东西。对我自己来说，学习这项令人敬畏的技术是一种巨大的乐趣，如果邀功请赏的话，所有的功劳理应都归功于发现它的研究人员们。正如本节开头所提到的，人们后来对这项技术进行了扩展，包括其他类型的多边形光源。出于简洁的原因，本教程省略了这些内容以及关于纹理映射的部分。说不定它们可能会在未来的章节中被提及。

最后值得一提的是，在区域光中添加阴影是一个开放的研究领域。一些可能的想法涉及屏幕空间光线跟踪和算法降噪，例如[9]或[10]。虽然这些技术非常有趣，但有点超出了本系列教程的范围。如果你愿意，你当然可以进一步学习和了解。

## 延伸阅读

- [1]  *Real-Time Polygonal-Light Shading with Linearly Transformed Cosines*, ACM Siggraph '16, [LTC.pdf](https://drive.google.com/file/d/0BzvWIdpUpRx_d09ndGVjNVJzZjA/view?resourcekey=0-21tmiqk55JIZU8UoeJatXQ)
- [2]  *Real-Time Area Lighting: a Journey from Research to Production*, presentation slides by Stephen Hill: [s2016_ltc_rnd.pdf](https://advances.realtimerendering.com/s2016/s2016_ltc_rnd.pdf)
- [3]  *Real-Time Polygonal-Light Shading with Linearly Transformed Cosines*, presentationslides by Eric Heitz: [slides.pdf](https://drive.google.com/file/d/0BzvWIdpUpRx_Z2pZWWFtam5xTFE/view?resourcekey=0-K9rJBtyrgGtxfP3XHDUCyQ)
- [4]  Main reference github repo: https://github.com/selfshadow/ltc_code. Contains precomputed matrices, source code for WebGL examples, and source code for recomputing the matrices with different BRDF-models.
- [5]  *Lighting with Linearly Transformed Cosines*, blog post by Tom Grove further investigating the technique. [blog](https://tomgroveblog.wordpress.com/2016/04/30/ltcpost/)
- [6]  *Real-Time Polygonal-Light Shading with Linearly Transformed Cosines*, Supplemental video showcasing the technique: [Youtube](https://www.youtube.com/watch?v=ZLRgEN7AQgM&ab_channel=JonathanDupuy)
- [7]  *Adam - Unity*, award-winning real-time-rendered short film by the Unity Demo team using the technique: [Youtube](https://www.youtube.com/watch?v=GXI0l3yqBrA&ab_channel=Unity)
- [8]  Interactive WebGL-demo: [blog.selfshadow.com](https://blog.selfshadow.com/ltc/webgl/ltc_quad.html)
- [9]  *Combining Analytic Direct Illumination and Stochastic Shadows*, Eric Heitz et al.: [I3D2018 combining.pdf](https://research.nvidia.com/sites/default/files/pubs/2018-05_Combining-Analytic-Direct//I3D2018_combining.pdf)
- [10] *Fast Analytic Soft Shadows from Area Lights*, Aakash KT et al.: [111-120.pdf](https://diglib.eg.org/bitstream/handle/10.2312/sr20211295/111-120.pdf)
- [11] *Stoke's theorem*: [Wikipedia](https://en.wikipedia.org/wiki/Stokes'_theorem)
- [12] *Linear-Light Shading with Linearly Transformed Cosines*: [HAL archives](https://hal.archives-ouvertes.fr/hal-02155101/document)
- [13] Alan Watt and Mark Watt: *Advanced Animation and Rendering Techniques, Theory and Practice*, Addison Wesley, 1992
- [14] 实时范围光Area Light渲染及其数学原理推导，XDzZyq：[笔记](https://www.bilibili.com/read/cv24390369)