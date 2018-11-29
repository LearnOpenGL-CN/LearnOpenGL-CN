
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
L_o(p,\omega_o) = \int\limits_{\Omega} (k_d\frac{c}{\pi}) (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i + \int\limits_{\Omega} (k_s\frac{DFG}{4(\omega_o \cdot n) (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

通过将积分分成两部分，我们可以单独关注漫反射和镜面反射;本教程的重点是漫反射积分。

仔细观察漫反射积分，我们发现漫反lambert项是一个常数项（颜色\(c\)，折射率\(k_D\)和\(π\)在积分上是常数），并且不依赖于任何积分变量。鉴于此，我们可以将常数项移出漫反射积分：

$$
L_o(p,\omega_o) = k_d\frac{c}{\pi} \int\limits_{\Omega} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

这给了我们一个仅取决于\(\omega_i\)的积分（假设\(p\)位于环境贴图的中心）。根据这些知识，我们就可以计算或预先计算一个新的立方体贴图，它通过<def>卷积</def>在每个采样方向（或纹素）\(\omega_o\)中存储漫反射积分的结果。

卷积是考虑到数据集中的所有其他条目，对数据集中的每个条目应用一些计算; 数据集是场景的辐射度或环境贴图。 因此，对于立方体贴图中的每个采样方向，我们都会考虑到半球\(\Omega\)上的所有其他采样方向。

为了对环境贴图进行卷积，我们通过对半球\(\Omega\)上的大量方向\(\omega_i\)进行离散采样并对其辐射(radiance)进行平均来求解每个输出采样方向\(\omega_o\)的积分。 我们建立采样方向\(\omega_i\)的半球\(\Omega\)朝向我们正在卷积的输出采样方向\(\omega_o\)。

![](../img/07/03/01/ibl_hemisphere_sample.png)

为每个采样方向(\omega_o\)存储积分结果的预先计算立方体贴图，可以被认为是场景所有间接漫射光的预先计算总和沿着方向(\omega_o\)对齐击中的一些表面。 这样的立方体贴图被称为<def>发光贴图</def>(irradiance map)，因为卷积立方体贴图有效地允许我们从任何方向(\omega_o\)直接采样场景（预先计算的）辐照度(irradiance)。

!!! important

	辐射方程也取决于位置\(p\)，我们假设它位于发光贴图的中心。这确实意味着所有漫射间接光必须来自单一环境贴图，这可能破坏真实感（特别是在室内）。渲染引擎通过场景中放置<def>反射探针</def>(reflection probes)来解决此问题,为每个反射探针根据其周围环境计算此探针的发光贴图。这样，位置\(p\)处的辐照度irradiance（和辐射radiance）是离其最近的反射探针间的插值辐照度irradiance。目前，我们假设我们总是从环境贴图的中心对其采样，并在后面的教程中讨论反射探针。
      
下面的示例是立方体贴图环境贴图及其生成的发光贴图（由[wave engine](https://www.indiedb.com/features/using-image-based-lighting-ibl)提供），为每个方向(\omega_o\)平均场景辐射(radiance)。

![](../img/07/03/01/ibl_irradiance.png)

通过将卷积结果存储在每个立方体贴图纹理像素中（在(\omega_o\)的方向上）, 发光贴图显的有点像环境的平均颜色或照明显示。从该环境贴图中采样任何方向将为我们提供该特定方向的场景辐照度(irradiance)。

## PBR and HDR

我们在[光照](../07 PBR/02 Lighting.md)教程中简要介绍了它：在PBR管线中将场景光照的高动态范围(HDR)考虑在内是非常重要的。由于PBR的大多输入基于真实物理属性和测量，因此将入射光值与其物理当量紧密匹配是有意义的。无论我们是对每种光源的辐射通量(radiant flux)进行教学性推测还是使用它们的[直接物理当量](https://en.wikipedia.org/wiki/Lumen_(unit))，简单灯泡和太阳之间的差异都是有意义的。如果不在[HDR](../05 Advanced Lighting/06 HDR.md)渲染环境中工作，则无法正确指定每个光源的相对强度。

因此，PBR和HDR密切相关，但这一切与基于图像的照明(IBL)有什么关系？ 我们在之前的教程中已经提到，在HDR中处理PBR相对容易。 然而，鉴于为了基于图像的照明(IBL)我们将环境的间接光强度基于环境立方体贴图的颜色值，我们需要某种方式将光的高动态范围(HDR)存储到环境贴图中。

迄今为止的环境贴图我们一直使用的是低动态范围（LDR）的立方体贴图（例如用作[天空盒](../04 Advanced OpenGL/06 Cubemaps.md))。 我们直接使用从各个面的图像获得的颜色值，范围介于0.0和1.0之间，并按这样处理它们。 虽然这可能适用于视觉输出，但当它们作为物理输入参数时，它就无法工作了。

### 辐射(radiance)HDR文件格式

输入辐射文件格式。 辐射文件格式（扩展名为.hdr）存储一个完整的立方体贴图，其中所有6个面都作为浮点数据，允许任何人指定0.0到1.0范围之外的颜色值，以使灯具有正确的颜色强度。文件格式还使用一个巧妙的技巧来存储每个浮点值，不使用32位值通道,而是使用8位通道,用颜色的alpha通道作为指数（这确实会导致精度损失）。这非常有效，但需要解析程序将每种颜色重新转换为它们的浮点值。

有很多辐射HDR环境地图可以从[sIBL archive](http://www.hdrlabs.com/sibl/archive.html)这样的来源免费获得，您可以在下面看到一个示例：

![](../img/07/03/01/ibl_hdr_radiance.png)

这可能与您期望的完全不同，因为图像显示失真，并且未显示我们之前看到的环境贴图的6个单独立方体贴图面中的任何一个。此环境贴图是从球体投影到平面上，以便我们可以更轻松地将环境存储到称为全景贴图(equirectangular map)的单一图像中。这点需要说明一下，因为大多数视觉分辨率存储在水平视图方向，而较少保留在底部和顶部方向。在大多数情况下，这是一个不错的折衷方案，因为几乎任何渲染器都可以在水平观察方向上找到大多数有用的光照和环境。

### HDR and stb_image.h

加载辐射HDR图像(radiance HDR images)直接需要一些[文件格式](http://radsite.lbl.gov/radiance/refer/Notes/picture_format.html)的知识，这不是太困难，但仍然很繁琐。 幸运的是，流行的一个头文化库[stb_image.h](https://github.com/nothings/stb/blob/master/stb_image.h)支持将辐射HDR图像(radiance HDR images)直接加载为浮点值数组，完全符合我们的需要。 通过将stb_image添加到项目中，加载HDR图像现在非常简单如下：

```c++
#include "stb_image.h"
[...]

stbi_set_flip_vertically_on_load(true);
int width, height, nrComponents;
float *data = stbi_loadf("newport_loft.hdr", &width, &height, &nrComponents, 0);
unsigned int hdrTexture;
if (data)
{
    glGenTextures(1, &hdrTexture);
    glBindTexture(GL_TEXTURE_2D, hdrTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_FLOAT, data); 

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    stbi_image_free(data);
}
else
{
    std::cout << "Failed to load HDR image." << std::endl;
}  
```

stb_image.h自动将HDR值映射到浮点值列表：默认情况下，每个通道32位，每种颜色3个通道。 这就是我们需要的将全景(equirectangular)HDR环境贴图存储到2D浮点纹理中。

### 从全景图(Equirectangular)到立方体贴图



e
```c++
#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 localPos;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    localPos = aPos;  
    gl_Position =  projection * view * vec4(localPos, 1.0);
}
```


```c++
#version 330 core
out vec4 FragColor;
in vec3 localPos;

uniform sampler2D equirectangularMap;

const vec2 invAtan = vec2(0.1591, 0.3183);
vec2 SampleSphericalMap(vec3 v)
{
    vec2 uv = vec2(atan(v.z, v.x), asin(v.y));
    uv *= invAtan;
    uv += 0.5;
    return uv;
}

void main()
{		
    vec2 uv = SampleSphericalMap(normalize(localPos)); // make sure to normalize localPos
    vec3 color = texture(equirectangularMap, uv).rgb;
    
    FragColor = vec4(color, 1.0);
}
```


![](../img/07/03/01/ibl_equirectangular_projection.png)


```c++
unsigned int captureFBO, captureRBO;
glGenFramebuffers(1, &captureFBO);
glGenRenderbuffers(1, &captureRBO);

glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
glBindRenderbuffer(GL_RENDERBUFFER, captureRBO);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 512, 512);
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, captureRBO);  
```


```c++
unsigned int envCubemap;
glGenTextures(1, &envCubemap);
glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap);
for (unsigned int i = 0; i < 6; ++i)
{
    // note that we store each face with 16 bit floating point values
    glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB16F, 
                 512, 512, 0, GL_RGB, GL_FLOAT, nullptr);
}
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```


```c++
glm::mat4 captureProjection = glm::perspective(glm::radians(90.0f), 1.0f, 0.1f, 10.0f);
glm::mat4 captureViews[] = 
{
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3( 1.0f,  0.0f,  0.0f), glm::vec3(0.0f, -1.0f,  0.0f)),
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(-1.0f,  0.0f,  0.0f), glm::vec3(0.0f, -1.0f,  0.0f)),
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3( 0.0f,  1.0f,  0.0f), glm::vec3(0.0f,  0.0f,  1.0f)),
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3( 0.0f, -1.0f,  0.0f), glm::vec3(0.0f,  0.0f, -1.0f)),
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3( 0.0f,  0.0f,  1.0f), glm::vec3(0.0f, -1.0f,  0.0f)),
   glm::lookAt(glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3( 0.0f,  0.0f, -1.0f), glm::vec3(0.0f, -1.0f,  0.0f))
};

// convert HDR equirectangular environment map to cubemap equivalent
equirectangularToCubemapShader.use();
equirectangularToCubemapShader.setInt("equirectangularMap", 0);
equirectangularToCubemapShader.setMat4("projection", captureProjection);
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, hdrTexture);

glViewport(0, 0, 512, 512); // don't forget to configure the viewport to the capture dimensions.
glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
for (unsigned int i = 0; i < 6; ++i)
{
    equirectangularToCubemapShader.setMat4("view", captureViews[i]);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                           GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, envCubemap, 0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    renderCube(); // renders a 1x1 cube
}
glBindFramebuffer(GL_FRAMEBUFFER, 0);  
```


```c++
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 projection;
uniform mat4 view;

out vec3 localPos;

void main()
{
    localPos = aPos;

    mat4 rotView = mat4(mat3(view)); // remove translation from the view matrix
    vec4 clipPos = projection * rotView * vec4(localPos, 1.0);

    gl_Position = clipPos.xyww;
}
```

```c++
glDepthFunc(GL_LEQUAL);  
```

```c++
#version 330 core
out vec4 FragColor;

in vec3 localPos;
  
uniform samplerCube environmentMap;
  
void main()
{
    vec3 envColor = texture(environmentMap, localPos).rgb;
    
    envColor = envColor / (envColor + vec3(1.0));
    envColor = pow(envColor, vec3(1.0/2.2)); 
  
    FragColor = vec4(envColor, 1.0);
}
```


![](../img/07/03/01/ibl_hdr_environment_mapped.png)



## 立方体贴图卷积




$$
L_o(p,\omega_o) = k_d\frac{c}{\pi} \int\limits_{\Omega} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$


```c++
vec3 irradiance = texture(irradianceMap, N);
```


![](../img/07/03/01/ibl_hemisphere_sample_normal.png)


```c++
#version 330 core
out vec4 FragColor;
in vec3 localPos;

uniform samplerCube environmentMap;

const float PI = 3.14159265359;

void main()
{		
    // the sample direction equals the hemisphere's orientation 
    vec3 normal = normalize(localPos);
  
    vec3 irradiance = vec3(0.0);
  
    [...] // convolution code
  
    FragColor = vec4(irradiance, 1.0);
}
```


![](../img/07/03/01/ibl_spherical_integrate.png)


$$
L_o(p,\phi_o, \theta_o) = k_d\frac{c}{\pi} \int_{\phi = 0}^{2\pi} \int_{\theta = 0}^{\frac{1}{2}\pi} L_i(p,\phi_i, \theta_i) \cos(\theta) \sin(\theta)  d\phi d\theta
$$


$$
L_o(p,\phi_o, \theta_o) = k_d\frac{c}{\pi} \frac{1}{n1 n2} \sum_{\phi = 0}^{n1} \sum_{\theta = 0}^{n2} L_i(p,\phi_i, \theta_i) \cos(\theta) \sin(\theta)  d\phi d\theta
$$


```c++
vec3 irradiance = vec3(0.0);  

vec3 up    = vec3(0.0, 1.0, 0.0);
vec3 right = cross(up, normal);
up         = cross(normal, right);

float sampleDelta = 0.025;
float nrSamples = 0.0; 
for(float phi = 0.0; phi < 2.0 * PI; phi += sampleDelta)
{
    for(float theta = 0.0; theta < 0.5 * PI; theta += sampleDelta)
    {
        // spherical to cartesian (in tangent space)
        vec3 tangentSample = vec3(sin(theta) * cos(phi),  sin(theta) * sin(phi), cos(theta));
        // tangent space to world
        vec3 sampleVec = tangentSample.x * right + tangentSample.y * up + tangentSample.z * N; 

        irradiance += texture(environmentMap, sampleVec).rgb * cos(theta) * sin(theta);
        nrSamples++;
    }
}
irradiance = PI * irradiance * (1.0 / float(nrSamples));
```


```c++
unsigned int irradianceMap;
glGenTextures(1, &irradianceMap);
glBindTexture(GL_TEXTURE_CUBE_MAP, irradianceMap);
for (unsigned int i = 0; i < 6; ++i)
{
    glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB16F, 32, 32, 0, 
                 GL_RGB, GL_FLOAT, nullptr);
}
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```

```c++
glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
glBindRenderbuffer(GL_RENDERBUFFER, captureRBO);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 32, 32);
```



```c++
irradianceShader.use();
irradianceShader.setInt("environmentMap", 0);
irradianceShader.setMat4("projection", captureProjection);
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap);

glViewport(0, 0, 32, 32); // don't forget to configure the viewport to the capture dimensions.
glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
for (unsigned int i = 0; i < 6; ++i)
{
    irradianceShader.setMat4("view", captureViews[i]);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                           GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, irradianceMap, 0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    renderCube();
}
glBindFramebuffer(GL_FRAMEBUFFER, 0);  
```





![](../img/07/03/01/ibl_irradiance_map_background.png)



## PBR和间接辐照度照明(indirect irradiance lighting)



```c++
uniform samplerCube irradianceMap;
```



```c++
// vec3 ambient = vec3(0.03);
vec3 ambient = texture(irradianceMap, N).rgb;
```


```c++
vec3 kS = fresnelSchlick(max(dot(N, V), 0.0), F0);
vec3 kD = 1.0 - kS;
vec3 irradiance = texture(irradianceMap, N).rgb;
vec3 diffuse    = irradiance * albedo;
vec3 ambient    = (kD * diffuse) * ao; 
```


![](../img/07/03/01/lighting_fresnel_no_roughness.png)




```c++
vec3 fresnelSchlickRoughness(float cosTheta, vec3 F0, float roughness)
{
    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - cosTheta, 5.0);
}
```


```c++
vec3 kS = fresnelSchlickRoughness(max(dot(N, V), 0.0), F0, roughness); 
vec3 kD = 1.0 - kS;
vec3 irradiance = texture(irradianceMap, N).rgb;
vec3 diffuse    = irradiance * albedo;
vec3 ambient    = (kD * diffuse) * ao; 
```



![](../img/07/03/01/ibl_irradiance_result.png)




## 延伸阅读
- [Coding Labs: Physically based rendering](http://www.codinglabs.net/article_physically_based_rendering.aspx):介绍PBR和怎样及为何生成发光贴图(irradiance map)。
- [The Mathematics of Shading](http://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/mathematics-of-shading):ScratchAPixel网站对本教程中描述的几个数学知识的简要介绍，特别是关于极坐标和积分。
