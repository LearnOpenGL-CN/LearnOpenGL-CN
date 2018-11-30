
原文     | [Diffuse irradiance](https://learnopengl.com/PBR/IBL/Diffuse-irradiance)
      ---|---
作者     | JoeyDeVries
翻译     | [slllllala](https://github.com/dsfdeeeg)
校对     | 暂无

IBL<def>基于图像的光照</def>(image based lighting)是一组照明物体的技术，而不是如前一个教程中的直接分析光，而是将周围环境视为一个大光源。这通常通过操纵立方体环境贴图（取自现实世界或从3D场景生成）来完成，这样我们就可以直接在我们的光照方程中使用它：将每个立方体贴图像素视为一个光发射器。通过这种方式，我们可以有效地捕捉环境的全局光照和总体感觉，使物体更好地融入其环境。

由于基于图像的光照算法会捕获某些（全局）环境光照，因此其输入被认为是更精确的环境光照形式，甚至是一种全局光照的粗略近似。 这使得IBL对PBR很有意义，因为当我们考虑环境光照时，对象在物理上看起来更加精确。 这使得IBL对PBR很有意义，因为当我们考虑环境光照时，对象在物理上看起来更加精确。

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

仔细观察漫反射积分，我们发现漫反lambert项是一个常数项（颜色\(c\)，折射率\(k_D\)和\(\pi\)在积分上是常数），并且不依赖于任何积分变量。鉴于此，我们可以将常数项移出漫反射积分：

$$
L_o(p,\omega_o) = k_d\frac{c}{\pi} \int\limits_{\Omega} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

这给了我们一个仅取决于\(\omega_i\)的积分（假设\(p\)位于环境贴图的中心）。根据这些知识，我们就可以计算或预先计算一个新的立方体贴图，它通过<def>卷积</def>在每个采样方向（或纹素）\(\omega_o\)中存储漫反射积分的结果。

卷积是考虑到数据集中的所有其他条目，对数据集中的每个条目应用一些计算; 数据集是场景的辐射度或环境贴图。 因此，对于立方体贴图中的每个采样方向，我们都会考虑到半球\(\Omega\)上的所有其他采样方向。

为了对环境贴图进行卷积，我们通过对半球\(\Omega\)上的大量方向\(\omega_i\)进行离散采样并对其辐射(radiance)进行平均来求解每个输出采样方向\(\omega_o\)的积分。 我们建立采样方向\(\omega_i\)的半球\(\Omega\)朝向我们正在卷积的输出采样方向\(\omega_o\)。

![](../../img/07/03/01/ibl_hemisphere_sample.png)

为每个采样方向(\omega_o\)存储积分结果的预先计算立方体贴图，可以被认为是场景所有间接漫射光的预先计算总和沿着方向(\omega_o\)对齐击中的一些表面。 这样的立方体贴图被称为<def>发光贴图</def>(irradiance map)，因为卷积立方体贴图有效地允许我们从任何方向(\omega_o\)直接采样场景（预先计算的）辐照度(irradiance)。

!!! important

	辐射方程也取决于位置\(p\)，我们假设它位于发光贴图的中心。这确实意味着所有漫射间接光必须来自单一环境贴图，这可能破坏真实感（特别是在室内）。渲染引擎通过场景中放置<def>反射探针</def>(reflection probes)来解决此问题,为每个反射探针根据其周围环境计算此探针的发光贴图。这样，位置\(p\)处的辐照度irradiance（和辐射radiance）是离其最近的反射探针间的插值辐照度irradiance。目前，我们假设我们总是从环境贴图的中心对其采样，并在后面的教程中讨论反射探针。
      
下面的示例是立方体贴图环境贴图及其生成的发光贴图（由[wave engine](https://www.indiedb.com/features/using-image-based-lighting-ibl)提供），为每个方向(\omega_o\)平均场景辐射(radiance)。

![](../../img/07/03/01/ibl_irradiance.png)

通过将卷积结果存储在每个立方体贴图纹理像素中（在(\omega_o\)的方向上）, 发光贴图显的有点像环境的平均颜色或照明显示。从该环境贴图中采样任何方向将为我们提供该特定方向的场景辐照度(irradiance)。

## PBR and HDR

我们在[光照](../07 PBR/02 Lighting.md)教程中简要介绍了它：在PBR管线中将场景光照的高动态范围(HDR)考虑在内是非常重要的。由于PBR的大多输入基于真实物理属性和测量，因此将入射光值与其物理当量紧密匹配是有意义的。无论我们是对每种光源的辐射通量(radiant flux)进行教学性推测还是使用它们的[直接物理当量](https://en.wikipedia.org/wiki/Lumen_(unit))，简单灯泡和太阳之间的差异都是有意义的。如果不在[HDR](../05 Advanced Lighting/06 HDR.md)渲染环境中工作，则无法正确指定每个光源的相对强度。

因此，PBR和HDR密切相关，但这一切与基于图像的光照(IBL)有什么关系？ 我们在之前的教程中已经提到，在HDR中处理PBR相对容易。 然而，鉴于为了基于图像的光照(IBL)我们将环境的间接光强度基于环境立方体贴图的颜色值，我们需要某种方式将光的高动态范围(HDR)存储到环境贴图中。

迄今为止的环境贴图我们一直使用的是低动态范围（LDR）的立方体贴图（例如用作[天空盒](../04 Advanced OpenGL/06 Cubemaps.md))。 我们直接使用从各个面的图像获得的颜色值，范围介于0.0和1.0之间，并按这样处理它们。 虽然这可能适用于视觉输出，但当它们作为物理输入参数时，它就无法工作了。

### 辐射(radiance)HDR文件格式

输入辐射文件格式。 辐射文件格式（扩展名为.hdr）存储一个完整的立方体贴图，其中所有6个面都作为浮点数据，允许任何人指定0.0到1.0范围之外的颜色值，以使灯具有正确的颜色强度。文件格式还使用一个巧妙的技巧来存储每个浮点值，不使用32位值通道,而是使用8位通道,用颜色的alpha通道作为指数（这确实会导致精度损失）。这非常有效，但需要解析程序将每种颜色重新转换为它们的浮点值。

有很多辐射HDR环境地图可以从[sIBL archive](http://www.hdrlabs.com/sibl/archive.html)这样的来源免费获得，您可以在下面看到一个示例：

![](../../img/07/03/01/ibl_hdr_radiance.png)

这可能与您期望的完全不同，因为图像显示失真，并且未显示我们之前看到的环境贴图的6个单独立方体贴图面中的任何一个。此环境贴图是从球体投影到平面上，以便我们可以更轻松地将环境存储到称为全景贴图(equirectangular map)的单一图像中。这点需要说明一下，因为大多数视觉分辨率存储在水平视图方向，而较少保留在底部和顶部方向。在大多数情况下，这是一个不错的折衷方案，因为几乎任何渲染器都可以在水平观察方向上找到大多数有用的光照和环境。

### HDR and stb_image.h

加载辐射HDR图像(radiance HDR images)直接需要一些[文件格式](http://radsite.lbl.gov/radiance/refer/Notes/picture_format.html)的知识，这不是太困难，但仍然很繁琐。 幸运的是，流行的一个头文化库[stb_image.h](https://github.com/nothings/stb/blob/master/stb_image.h)支持将辐射HDR图像(radiance HDR images)直接加载为浮点值数组，完全符合我们的需要。 通过将`stb_image`添加到项目中，加载HDR图像现在非常简单如下：

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

`stb_image.h`自动将HDR值映射到浮点值列表：默认情况下，每个通道32位，每种颜色3个通道。 这就是我们需要的将全景(equirectangular)HDR环境贴图存储到2D浮点纹理中。

### 从全景(Equirectangular)到立方体贴图

可以直接使用全景贴图(equirectangular map)进行环境查找，但是这些操作可能相对昂贵，在这种情况下，直接用立方体贴图采样的性能更高。 因此，在本教程中，我们首先将全景图像(equirectangular image)转换为立方体贴图以进行进一步处理。 请注意，在此过程中，我们还将展示如何对全景贴图(equirectangular map)进行采样，就像它是一个3D环境贴图一样，在这种情况下，您可以自由选择您喜欢的任何解决方案。

要将一个全景图像(equirectangular image)转换为立方体贴图，我们需要渲染一个（单位）立方体，从内部投影全景贴图(equirectangular map)到立方体的所有面上，并将立方体面的6个图像作为立方体贴图面。 此立方体的顶点着色器只是按原样渲染立方体，并将其本地位置作为3D采样向量传递给片段着色器：

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

对于片段着色器，我们为立方体的每个部分着色，就像我们将全景贴图(equirectangular map)整齐地折叠到立方体的每一侧一样。 为了实现这一点，我们将立方体的当前位置进行插值作为片段的采样方向，然后使用此方向向量和一些三角法变换,把全景贴图(equirectangular map)当做立方体贴图进行采样。 我们直接将结果存储到立方体面的片段中，这应该是我们需要做的全部：

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

如果用给定的HDR全景贴图(HDR equirectangular map)在场景的中心渲染立方体，您将得到如下所示的内容：

![](../../img/07/03/01/ibl_equirectangular_projection.png)

这表明我们有效地将全景图像(equirectangular image)映射到立方体形状，但还不足以帮助我们将源HDR图像转换为立方体贴图纹理。 为了实现这一点，我们必须渲染相同的立方体6次，查看立方体的每个单独的面,使用[帧缓冲](../04 Advanced OpenGL/05 Framebuffers.md)对象记录其可视结果：

```c++
unsigned int captureFBO, captureRBO;
glGenFramebuffers(1, &captureFBO);
glGenRenderbuffers(1, &captureRBO);

glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
glBindRenderbuffer(GL_RENDERBUFFER, captureRBO);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 512, 512);
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, captureRBO);  
```

当然，我们还要生成相应的立方体贴图，为其6个面预先分配内存：

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

那么剩下要做的就是将全景(equirectangular)2D纹理捕捉到立方体贴图的面上。

我不会详细说明在前面的帧缓冲和点阴影教程中已经讨论过的代码细节，但它有效地归结为面向立方体每一面设置6个不同的视图矩阵，给定一个视角90度的投影矩阵。但可以有效地归结为设置6个不同的视图矩阵,面向立方体的6个面，给定一个视角90度的投影矩阵来捕捉整个面，并渲染一个立方体6次将结果存储在浮点帧缓冲中：

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

我们采用帧缓冲的颜色附件并为立方体贴图的每个面切换其纹理目标，直接将场景渲染到立方体贴图的一个面上。 一旦这个例程完成（我们只需做一次），立方体贴图`envCubemap`该是原始HDR图像的立方体环境贴图版本了。

让我们通过编写一个非常简单的天空盒着色器来测试立方体贴图，以显示我们周围的立方体贴图：

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

注意这里的`xyww`技巧确保渲染的立方体片段的深度值总是最终为1.0，即最大深度值，如[立方体贴图](../04 Advanced OpenGL/06 Cubemaps.md)教程中所述。 请注意，我们需要将深度比较功能更改为`GL_LEQUAL`：

```c++
glDepthFunc(GL_LEQUAL);  
```

片段着色器而后使用立方体的当前片段位置直接对立方体环境贴图进行采样：

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

我们使用立方体位置的插值顶点对环境贴图进行采样，这些位置直接对应于要采样的正确方向向量。 鉴于相机的平移组件被忽略，在立方体上渲染此着色器应该将此环境贴图作为非移动背景。 另外，请注意，当我们将环境贴图的HDR值直接输出到默认的LDR帧缓冲区时，我们需要正确地对颜色值进行色调映射。 此外，默认情况下，几乎所有HDR地图都处于线性色彩空间中，因此我们需要在写入默认帧缓冲区之前应用[Gamma校正](../05 Advanced Lighting/02 Gamma Correction.md)。

现在，在先前渲染的球体上渲染采样环境贴图应该如下所示：

![](../../img/07/03/01/ibl_hdr_environment_mapped.png)

好吧......我们花了很多时间设置到这里，但是我们成功地设法读取了HDR环境贴图，将其从全景(equirectangular)映射为立方体贴图，并将HDR立方体贴图渲染到场景中作为天空盒。 此外，我们设置了一个小型系统来渲染立方体贴图的所有6个面，我们在<def>卷积</def>环境贴图时将需要再次使用。 您可以在[此处](https://learnopengl.com/code_viewer_gh.php?code=src/6.pbr/2.1.1.ibl_irradiance_conversion/ibl_irradiance_conversion.cpp)找到整个转化过程的源代码。

## 立方体贴图卷积

如本教程开头所述，我们的主要目标是用立方体环境贴的图形式给定场景辐照度(irradiance )的情况下求解所有漫反射间接光照的积分。我们知道通过在方向\(\omega_i\)上采样HDR环境贴图，可以在特定方向上获得场景\(L(p,\omega_i)\)的辐射(radiance)。为了求解积分，我们必须为每个片段从半球\(\Omega\)内的所有可能方向采样场景辐射(radiance)。

然而，从计算上来说不可能从半球\(\Omega\)中的每个可能方向采样环境光照，可能的方向数量理论上是无限的。然而，我们可以通过采用有限数量的方向或采样来近似这个方向数量，从半球内均匀间隔或随机取得以获得相当精确的辐照度(irradiance)近似，从而有效地求解积分\(\int\)

然而，对于每个片段实时执行此操作仍然太昂贵，因为样本数量仍然需要非常大才能得到合适的结果，因此我们要<def>预先计算</def>它。由于半球的方向决定我们捕获辐照度的位置，我们可以预先计算围绕所有传出方向\(\omega_o\)的每个可能的半球方向的辐照度：

$$
L_o(p,\omega_o) = k_d\frac{c}{\pi} \int\limits_{\Omega} (\omega_i \cdot n)})L_i(p,\omega_i) n \cdot \omega_i  d\omega_i
$$

给定任何方向向量\(\omega_i\)，然后我们可以从方向\(\omega_i\)对预先计算的发光贴图(irradiance map)进行采样以获得总漫射辐照度(irradiance)。 为了确定片段表面上间接漫射(辐射)光的量，我们从围绕其表面法线的半球中获得总辐照度(irradiance)。 获得场景的辐照度(irradiance)就像这样简单

```c++
vec3 irradiance = texture(irradianceMap, N);
```

现在，为了生成发光贴图(irradiance map)，我们需要卷积将环境光照转换为立方体贴图。 假设对于每个片段，表面的半球沿着法向量\(N\)定向，对立方图进行卷积等于计算沿着\(N\)定向的半球\(\Omega\)中每个方向\(\omega_i\)的总平均辐射(radiance)。

![](../../img/07/03/01/ibl_hemisphere_sample_normal.png)

值得庆幸的是，本教程中所有繁琐的设置并非一无所获，因为我们现在可以直接获取转换后的立方体贴图，在片段着色器中对其进行卷积，并使用向所有6个面部方向渲染的帧缓冲区将其结果捕获到新的立方体贴图中。 由于我们已经设置了将全景(equirectangular)环境贴图转换为立方体贴图，我们可以采用完全相同的方法，但使用不同的片段着色器：

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

`environmentMap`是从全景(equirectangular)HDR环境贴图转换而来的HDR立方体贴图。

有许多方法可以对环境贴图进行卷积，但是对于本教程，我们将为每个立方体贴图纹素在沿着采样向量的半球\(\Omega\)生成固定数量的采样向量，并平均结果。 固定量的采样向量将均匀地分布在半球内部。 注意，积分是连续函数并且在给定定量采样向量的情况下离散地采样其函数将获得积分的近似值。 我们使用的采样向量越多，我们能更好的近似积分。

反射率方程的积分\(\int\)围绕相当难以处理的立体角\(d\omega\)旋转。 我们将在其等效球面坐标\(\theta\)和\(\phi\)上积分，而不是在立体角\(d\omega\)上积分。

![](../../img/07/03/01/ibl_spherical_integrate.png)

我们使用\(0\)到\(2\pi\)之间的极方位角\(\phi\)围绕半球环进行采样，并使用\(0\)到\(\frac{1}{2}\pi\)之间的天顶角\(\theta\)来对半球的增加环进行采样。 这将为我们提供新的反射积分：

$$
L_o(p,\phi_o, \theta_o) = k_d\frac{c}{\pi} \int_{\phi = 0}^{2\pi} \int_{\theta = 0}^{\frac{1}{2}\pi} L_i(p,\phi_i, \theta_i) \cos(\theta) \sin(\theta)  d\phi d\theta
$$

求解积分需要我们在半球\(\Omega\)内采集固定数量的离散样本并对其结果求平均值。 这将积分转换为以下离散版本，基于分别在每个球坐标上给定\(n1\)和\(n2\)个离散样本的[黎曼和](https://en.wikipedia.org/wiki/Riemann_sum)：

$$
L_o(p,\phi_o, \theta_o) = k_d\frac{c}{\pi} \frac{1}{n1 n2} \sum_{\phi = 0}^{n1} \sum_{\theta = 0}^{n2} L_i(p,\phi_i, \theta_i) \cos(\theta) \sin(\theta)  d\phi d\theta
$$

当我们离散地对两个球面值进行采样时，每个采样将近似或平均半球上的区域，如上图所示。 注意（由于球形的一般性质），当采样区域朝向中心顶部会聚时，半球的离散样本区域越小，天顶角\(\theta\)越高。 为了弥补较小的区域，我们通过使用\(\sin \theta\)来缩放区域来权衡其贡献，增加\(\sin\)。

为每个片段调用在给定积分球面坐标下对半球进行离散采样转换为以下代码：

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

我们指定一个固定的`sampleDelta` 增量来遍历半球; 减小或增加采样增量将分别增加或减少准确度。

在两个循环内，我们采用球面坐标将它们转换为3D笛卡尔采样向量，将采样从切线转换为世界空间，并使用此采样向量直接对HDR环境贴图进行采样。 我们将每个采样结果添加到`irradiance`，最后我们除以采样的总数，得到平均采样辐照度。 请注意，我们将采样的颜色值按`cos(theta)`缩放，因为较大的角度较弱，而通过`sin(theta)`处理较高半球区域的较小样本区域。

现在剩下要做的是设置OpenGL渲染代码，以便我们可以卷积早期获得的`envCubemap`。 首先我们创建辐照度立方体贴图（同样，我们只需要在渲染循环之前执行一次）：

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

由于辐照度图均匀地平均所有周围辐射，因此它不具有大量高频细节，因此我们可以以低分辨率（32x32）存储贴图，并让OpenGL的线性过滤完成大部分工作。 接下来，我们将捕获帧缓冲区重新缩放到新的分辨率：

```c++
glBindFramebuffer(GL_FRAMEBUFFER, captureFBO);
glBindRenderbuffer(GL_RENDERBUFFER, captureRBO);
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 32, 32);
```

使用卷积着色器，我们用与捕获环境立方体贴图类似的方式卷积环境贴图：

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

现在，在这个例程之后，我们应该有一个预先计算的辐照度图，我们可以直接用于基于漫反射图像的光照。 为了查看我们是否成功地对环境贴图进行了卷积，让我们将环境贴图替换为辐照度贴图作为天空盒的环境采样器：

![](../../img/07/03/01/ibl_irradiance_map_background.png)

如果它看起来像环境贴图的模糊版本，那么您已经成功地对环境贴图进行了卷积处理。

## PBR和间接辐照度光照(indirect irradiance lighting)

发光贴图(irradiance map)表示从所有周围间接光累积的反射积分的漫射部分。 鉴于光不是来自任何直接光源，而是来自周围环境，我们将漫反射和镜面间接光照视为环境光照，取代了我们之前设定的常数项。

首先，务必将预先计算的发光贴图(irradiance map)添加为立方体采样器：

```c++
uniform samplerCube irradianceMap;
```

给定保留所有场景的间接漫射光的发光贴图(irradiance map)，获取影响片段的辐照度(irradiance)就像给定表面法线的单一纹理采样一样简单：

```c++
// vec3 ambient = vec3(0.03);
vec3 ambient = texture(irradianceMap, N).rgb;
```

然而，由于间接光照包含漫反射和镜面反射部分，正如我们从反射方程的分割版本中看到的那样，我们需要相应地对漫反射部分进行加权。 与我们在前一个教程中所做的类似，我们使用菲涅耳方程来确定表面的间接反射率，我们从中得出折射率或漫射率：

```c++
vec3 kS = fresnelSchlick(max(dot(N, V), 0.0), F0);
vec3 kD = 1.0 - kS;
vec3 irradiance = texture(irradianceMap, N).rgb;
vec3 diffuse    = irradiance * albedo;
vec3 ambient    = (kD * diffuse) * ao; 
```

由于环境光来自半球内围绕法线N的所有方向，因此没有单个中间向量来确定菲涅耳响应。 为了模拟菲涅耳，我们从法线和视图矢量之间的角度计算菲涅耳。 然而，早些时候我们使用微表面中途矢量，受表面粗糙度的影响，作为菲涅耳方程的输入。 由于我们目前没有考虑任何粗糙度，因此表面的反射率总是会相对较高。 间接光遵循直射光的相同属性，因此我们期望较粗糙的表面在表面边缘上反射较弱。 由于我们没有考虑表面的粗糙度，间接的菲涅耳反射强度在粗糙的非金属表面上看起来（为了演示目的略微夸大）：

![](../../img/07/03/01/lighting_fresnel_no_roughness.png)

我们可以通过在[Sébastien Lagarde](https://seblagarde.wordpress.com/2011/08/17/hello-world/)描述的Fresnel-Schlick方程中注入粗糙度项来缓解这个问题：

```c++
vec3 fresnelSchlickRoughness(float cosTheta, vec3 F0, float roughness)
{
    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - cosTheta, 5.0);
}
```

通过在计算菲涅耳响应时考虑表面的粗糙度，环境代码最终为：

```c++
vec3 kS = fresnelSchlickRoughness(max(dot(N, V), 0.0), F0, roughness); 
vec3 kD = 1.0 - kS;
vec3 irradiance = texture(irradianceMap, N).rgb;
vec3 diffuse    = irradiance * albedo;
vec3 ambient    = (kD * diffuse) * ao; 
```

如您所见，基于实际图像的光照计算非常简单，只需要一个立方体贴图纹理查找; 大部分工作是将环境地图预先计算或卷积成发光贴图(irradiance map)。

如果我们从[光照](../07 PBR/02 Lighting.md)教程中获取初始场景，其中每个球体具有垂直增加的金属和水平增加的粗糙度值并添加基于漫反射光照的光照，它看起来有点像这样：

![](../../img/07/03/01/ibl_irradiance_result.png)

它仍然看起来有点奇怪，因为更多的金属球体需要某种形式的反射才能正确地开始看起来像金属表面（因为金属表面不会反射漫射光），此刻目前只是来自点光源（几乎没有）。 尽管如此，您已经可以告诉球体在环境中确实感觉到更多（特别是如果您在环境地图之间切换），因为表面响应会相应地响应环境的环境光照。

您可以在[此处](https://learnopengl.com/code_viewer_gh.php?code=src/6.pbr/2.1.2.ibl_irradiance/ibl_irradiance.cpp)找到所讨论主题的完整源代码。 在[下一个](../07 PBR/03 IBL/02 Specular IBL.md)教程中，我们将添加反射积分的间接镜面反射部分，此时我们将真正看到PBR的力量。

## 延伸阅读
- [Coding Labs: Physically based rendering](http://www.codinglabs.net/article_physically_based_rendering.aspx):介绍PBR和怎样及为何生成发光贴图(irradiance map)。
- [The Mathematics of Shading](http://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/mathematics-of-shading):ScratchAPixel网站对本教程中描述的几个数学知识的简要介绍，特别是关于极坐标和积分。
