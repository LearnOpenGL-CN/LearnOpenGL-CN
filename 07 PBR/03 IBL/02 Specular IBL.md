
原文     | [Specular IBL](https://learnopengl.com/PBR/IBL/Specular-IBL)
      ---|---
作者     | JoeyDeVries
翻译     | [slllllala](https://github.com/dsfdeeeg)
校对     | 暂无











$$
L_o(p,\omega_o) = \int\limits_{\Omega} (k_d\frac{c}{\pi} + k_s\frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)}) L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$



$$
L_o(p,\omega_o) = \int\limits_{\Omega} (k_s\frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)} L_i(p,\omega_i) n \cdot \omega_i  d\omega_i = \int\limits_{\Omega} f_r(p, \omega_i, \omega_o) L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$





$$
f_r(p, w_i, w_o) = \frac{DFG}{4(\omega_o \cdot n)(\omega_i \cdot n)}
$$



$$
L_o(p,\omega_o) = \int\limits_{\Omega} L_i(p,\omega_i) d\omega_i * \int\limits_{\Omega} f_r(p, \omega_i, \omega_o) n \cdot \omega_i d\omega_i
$$





![](../../img/07/03/02/ibl_prefilter_map.png)



```c++
vec3 N = normalize(w_o);
vec3 R = N;
vec3 V = R;
```




![](../../img/07/03/02/ibl_grazing_angles.png)




![](../../img/07/03/02/ibl_brdf_lut.png)




```c++
float lod             = getMipLevelFromRoughness(roughness);
vec3 prefilteredColor = textureCubeLod(PrefilteredEnvMap, refVec, lod);
vec2 envBRDF          = texture2D(BRDFIntegrationMap, vec2(NdotV, roughness)).xy;
vec3 indirectSpecular = prefilteredColor * (F * envBRDF.x + envBRDF.y) 
```



## 预过滤HDR环境贴图


\(\Omega\)
\(\omega_i\)
\(k_S\)


!!! important

	辐射方程也取决于位置\(p\)，我们假设它位于发光贴图的中心。这确实意味着所有漫射间接光必须来自单一环境贴图，这可能破坏真实感（特别是在室内）。渲染引擎通过

[wave engine](https://www.indiedb.com/features/using-image-based-lighting-ibl)
























