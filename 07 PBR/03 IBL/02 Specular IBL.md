
原文     | [Specular IBL](https://learnopengl.com/PBR/IBL/Specular-IBL)
      ---|---
作者     | JoeyDeVries
翻译     | [slllllala](https://github.com/dsfdeeeg)
校对     | 暂无











$$
L_o(p,\omega_o) = \int\limits_{\Omega} (k_d\frac{c}{\pi} + k_s\frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

```c++
vec3 radiance = texture(_cubemapEnvironment, w_i).rgb; 
```


\(\Omega\)
\(\omega_i\)
\(k_S\)
![](../../img/07/03/01/ibl_hemisphere_sample.png)

!!! important

	辐射方程也取决于位置\(p\)，我们假设它位于发光贴图的中心。这确实意味着所有漫射间接光必须来自单一环境贴图，这可能破坏真实感（特别是在室内）。渲染引擎通过

[wave engine](https://www.indiedb.com/features/using-image-based-lighting-ibl)
























