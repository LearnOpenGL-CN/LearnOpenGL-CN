
原文     | [Diffuse irradiance](https://learnopengl.com/PBR/IBL/Diffuse-irradiance)
      ---|---
作者     | JoeyDeVries
翻译     | [slllllala](https://github.com/dsfdeeeg)
校对     | 暂无

IBL<def>基于图像的光照</def>(image based lighting)是一组照明物体的技术，而不是如前一个教程中的直接分析光，而是将周围环境视为一个大光源。这通常通过操纵立方体环境贴图（取自现实世界或从3D场景生成）来完成，这样我们就可以直接在我们的光照方程中使用它：将每个立方体贴图像素视为一个光发射器。通过这种方式，我们可以有效地捕捉环境的全局照明和一般感觉，使物体更好地融入其环境。

由于基于图像的照明算法会捕获某些（全局）环境光照，因此其输入被认为是更精确的环境光照形式，甚至是一种全局照明的粗略近似。 这使得IBL对PBR很有意义，因为当我们考虑环境照明时，对象在物理上看起来更加精确。 这使得IBL对PBR很有意义，因为当我们考虑环境光照时，对象在物理上看起来更加精确。

为了将IBL引入我们的PBR系统，让我们再次快速研究一下反射方程：

$$
L_o(p,\omega_o) = \int\limits_{\Omega} (k_d\frac{c}{\pi} + k_s\frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

如前所述，我们的主要目标是求解半球\(\Omega\)上所有入射光方向的积分。求前一个教程中的积分很容易，因为事先我们已经知道了影响积分的精确的几个光照方向\(\omega_i\)。然而，这次来自周围环境的每个入射光方向\(\omega_i\)可能具有一些辐射(radiance)，使得解决积分变得不那么简单。这为解决积分提供了两个主要要求：

- 给定任何方向向量\(\omega_i\)，我们需要一些方法来获得场景辐射(radiance)。
- 求解积分需要快速和实时。

现在，第一个要求相对容易。我们已经提到过它，表示环境或场景的辐照度(irradiance)的一种方式是以（处理过的）环境立方体贴图的形式。给定这样的立方体贴图，我们可以将立方体贴图的每个纹素(texel )作为一个独立发光源。用任意方向向量\(\omega_i\)对该立方体图进行采样，我们能获得该方向的场景辐射(radiance)。

在给定任何方向向量\(\omega_i\)的情况下获得场景辐射(radiance)就像下面这样简单：

```c++
vec3 radiance = texture(_cubemapEnvironment, w_i).rgb; 
```

但，求解积分需要我们不仅从一个方向采样环境贴图，而是在半球\(\Omega\)上对所有可能的方向\(\omega_i\)进行采样，这对于每个片段着色器调用来说太昂贵了。为了以更有效的方式求解积分，我们需要预处理或预先计算其大部分计算。为此，我们将不得不深入研究反射方程：

$$
L_o(p,\omega_o) = \int\limits_{\Omega} (k_d\frac{c}{\pi} + k_s\frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

仔细研究反射方程，我们发现**BRDF**的漫反射\(k_D\)和镜面\(k_S\)项是相互独立的，我们可以将积分分成两部分：

$$
L_o(p,\omega_o) = \int\limits_{\Omega} k_d\frac{c}{\pi} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i + \int\limits_{\Omega} k_s\frac{DFG}{4(\omega_o \cdot n (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

通过将积分分成两部分，我们可以单独关注漫反射和镜面反射;本教程的重点是漫反射积分。

仔细观察漫反射积分，我们发现漫反lambert项是一个常数项（颜色\(c\)，折射率\(k_D\)和\(π\)在积分上是常数），并且不依赖于任何积分变量。鉴于此，我们可以将常数项移出漫反射积分：

$$
L_o(p,\omega_o) = \int\limits_{\Omega} k_d\frac{c}{\pi} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

这给了我们一个仅取决于\(\omega_i\)的积分（假设\(p\)位于环境贴图的中心）。根据这些知识，我们就可以计算或预先计算一个新的立方体贴图，它通过<def>卷积</def>在每个采样方向（或纹素）\(\omega_o\)中存储漫反射积分的结果。

卷积是考虑到数据集中的所有其他条目，对数据集中的每个条目应用一些计算; 数据集是场景的辐射度或环境贴图。 因此，对于立方体贴图中的每个样本方向，我们都会考虑半球\(\Omega\)上的所有其他样本方向。

为了对环境贴图进行卷积，我们通过对半球Ω上的大量方向\(\omega_i\)进行离散采样并对其平均值进行平均来解决每个输出样本方向\(\omega_o\)的积分。 我们建立样本方向\(\omega_i\)的半球\(\Omega\)朝向我们正在卷积的输出样本方向\(\omega_o\)。
