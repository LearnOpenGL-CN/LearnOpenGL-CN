
原文     | [Diffuse irradiance](https://learnopengl.com/PBR/IBL/Diffuse-irradiance)
      ---|---
作者     | JoeyDeVries
翻译     | [slllllala](https://github.com/dsfdeeeg)
校对     | 暂无

IBL<def>基于图像的光照(Image Based </def>(image based lighting)是一组照明物体的技术，而不是如前一个教程中的直接分析光，而是将周围环境视为一个大光源。这通常通过操纵立方体环境贴图（取自现实世界或从3D场景生成）来完成，这样我们就可以直接在我们的光照方程中使用它：将每个立方体贴图像素视为一个光发射器。通过这种方式，我们可以有效地捕捉环境的全局照明和一般感觉，使物体更好地融入其环境。

由于基于图像的照明算法会捕获某些（全局）环境光照，因此其输入被认为是更精确的环境光照形式，甚至是一种全局照明的粗略近似。 这使得IBL对PBR很有意义，因为当我们考虑环境照明时，对象在物理上看起来更加精确。 这使得IBL对PBR很有意义，因为当我们考虑环境光照时，对象在物理上看起来更加精确。

为了将IBL引入我们的PBR系统，让我们再次快速研究一下反射方程：

$$
L_o(p,\omega_o) = \int\limits_{\Omega} f_r(p,\omega_i,\omega_o) L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$
