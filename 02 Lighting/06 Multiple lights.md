##多光源（Multiple lights）

本文作者JoeyDeVries，由Geequlim翻译自[http://learnopengl.com](http://learnopengl.com/#!Lighting/Multiple-lights)

我们在前面的教程中已经学习了许多关于OpenGL 光照的知识，其中包括冯氏照明（Phong shading）、光照材质（Materials）、光照图（Lighting maps）以及各种投光物。本教程将结合上述所学的知识，创建一个包含六个光源的场景。我们将模拟一个类似阳光的平行光（Directional light）和4个定点光（Point lights）以及一个手电筒(Flashlight).

要在场景中使用多光源我们需要封装一些GLSL函数用来计算光照。如果我们对每个光源都去些一遍光照计算的代码，这将是一件令人恶心的事情，并且这些放在main函数中的代码将难以理解，所以我们将一些操作封装为函数。

GLSL中的函数与C语言的非常相似，它需要一个函数名、一个返回值类型。并且在调用前必须提前声明。接下来我们将为下面的每一种光照来写一个函数。

当我们在场景中使用多个光源时一般使用以下途径：创建一个代表输出颜色的向量。每一个光源都对输出颜色贡献一些颜色。因此，场景中的每个光源将进行独立运算，并且运算结果都对最终的输出颜色有一定影响。下面是使用这种方式进行多光源运算的一般结构：

```c++
out vec4 color;

void main()
{
  // 定义输出颜色
  vec3 output;
  // 将平行光的运算结果颜色添加到输出颜色
  output += someFunctionToCalculateDirectionalLight();
  // 同样，将定点光的运算结果颜色添加到输出颜色
  for(int i = 0; i < nr_of_point_lights; i++)
  	output += someFunctionToCalculatePointLight();
  // 添加其他光源的计算结果颜色（如投射光）
  output += someFunctionToCalculateSpotLight();

  color = vec4(output, 1.0);
}  
```

即使对每一种光源的运算实现不同，但此算法的结构一般是与上述出入不大的。我们将定义几个用于计算各个光源的函数，并将这些函数的结算结果（返回颜色）添加到输出颜色向量中。例如，靠近被照射物体的光源计算结果将返回比远离背照射物体的光源更明亮的颜色。

###平行光（Directional light）

我们要在片段着色器中定义一个函数用来计算平行光在对应的照射点上的光照颜色，这个函数需要几个参数并返回一个计算平行光照结果的颜色。

首先我们需要设置一系列用于表示平行光的变量，正如上一节中所讲过的，我们可以将这些变量定义在一个叫做**DirLight**的结构体中，并定义一个这个结构体类型的uniform变量。

```c++
struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};  
uniform DirLight dirLight;
```
之后我们可以将 *dirLight*这个uniform变量作为下面这个函数原型的参数。

```c++
vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir);  
```

!!! Important

        和C/C++一样，我们调用一个函数的前提是这个函数在调用前已经被声明过（此例中我们是在main函数中调用）。通常情况下我们都将函数定义在main函数之后，为了能在main函数中调用这些函数，我们就必须在main函数之前声明这些函数的原型，这就和我们写C语言是一样的。
        
你已经知道，这个函数需要一个**DirLight**和两个其他的向量作为参数来计算光照。如果你看过之前的教程的话，你会觉得下面的函数定义得一点也不意外：

```c++
vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);
    // 计算漫反射强度
    float diff = max(dot(normal, lightDir), 0.0);
    // 计算镜面反射强度
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // 合并各个光照分量
    vec3 ambient  = light.ambient  * vec3(texture(material.diffuse, TexCoords));
    vec3 diffuse  = light.diffuse  * diff * vec3(texture(material.diffuse, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    return (ambient + diffuse + specular);
}  
```

我们从之前的教程中复制了代码，并用两个向量来作为函数参数来计算出平行光的光照颜色向量，该结果是一个由该平行光的环境反射、漫反射和镜面反射的各个分量组成的一个向量。

###定点光（Point light）

和计算平行光一样，我们同样需要定义一个函数用于计算定点光照。同样的，我们定义一个包含定点光源所需属性的结构体：

```c++
struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;  

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};  
#define NR_POINT_LIGHTS 4  
uniform PointLight pointLights[NR_POINT_LIGHTS];
```

如你所见，我们在GLSL中使用预处理器指令来定义定点光源的数目。之后我们使用这个**NR_POINT_LIGHTS**常量来创建一个**PointLight**结构体的数组。和C语言一样，GLSL也是用一对中括号来创建数组的。现在我们有了4个**PointLight**结构体对象了。

!!! Important

    我们同样可以简单粗暴地定义一个大号的结构体（而不是为每一种类型的光源定义一个结构体），它包含所有类型光源所需要属性变量。并且将这个结构体应用与所有的光照计算函数，在各个光照结算时忽略不需要的属性变量。然而，就我个人来说更喜欢分开定义，这样可以省下一些内存，因为定义一个大号的光源结构体在计算过程中会有用不到的变量。

```c++
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);  

```

这个函数将所有用得到的数据作为它的参数并使用一个vec3作为它的返回值类表示一个顶点光的结算结果。我们再一次聪明地从之前的教程中复制代码来把它定义成下面的样子：

```c++
// 计算定点光在确定位置的光照颜色
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // 计算漫反射强度
    float diff = max(dot(normal, lightDir), 0.0);
    // 计算镜面反射
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // 计算衰减
    float distance    = length(light.position - fragPos);
    float attenuation = 1.0f / (light.constant + light.linear * distance +
  			     light.quadratic * (distance * distance));
    // 将各个分量合并
    vec3 ambient  = light.ambient  * vec3(texture(material.diffuse, TexCoords));
    vec3 diffuse  = light.diffuse  * diff * vec3(texture(material.diffuse, TexCoords));
    vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}
```

有了这个函数我们就可以在main函数中调用它来代替写很多个计算点光源的代码了。通过循环调用此函数就能实现同样的效果，当然代码更简洁。

###把它们放到一起

我们现在定义了用于计算平行光和定点光的函数，现在我们把这些代码放到一起，写入文开始的一般结构中：

```c++
void main()
{
    // 一些属性
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    // 第一步，计算平行光照
    vec3 result = CalcDirLight(dirLight, norm, viewDir);
    // 第二步，计算顶点光照
    for(int i = 0; i < NR_POINT_LIGHTS; i++)
        result += CalcPointLight(pointLights[i], norm, FragPos, viewDir);
    // 第三部，计算 Spot light
    //result += CalcSpotLight(spotLight, norm, FragPos, viewDir);

    color = vec4(result, 1.0);
}
```

每一个光源的运算结果都添加到了输出颜色上，输出颜色包含了此场景中的所有光源的影响。
如果你想实现手电筒的光照效果，同样的把计算结果添加到输出颜色上。我在这里就把CalcSpotLight的实现留作个读者们的练习吧。

设置平行光结构体的uniform值和之前所讲过的方式没什么两样，但是你可能想知道如何设置场景中**PointLight**结构体的uniforms变量数组。我们之前并未讨论过如何做这件事。

庆幸的是，这并不是什么难题。设置uniform变量数组和设置单个uniform变量值是相似的，只需要用一个合适的下标就能够检索到数组中我们想要的uniform变量了。

```c++
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].constant"), 1.0f);
```

这样我们检索到pointLights数组中的第一个 PointLight 结构体元素，同时也可以获取到该结构体中的各个属性变量。不幸的是这一位置我们还需要手动
对这个四个光源的每一个属性都进行设置，这样手动设置这28个uniform变量是相当乏味的工作。你可以尝试去定义个光源类来为你设置这些uniform属性来减少你的工作，
但这依旧不能改变去设置每个uniform属性的事实。

别忘了，我们还需要为每个光源设置它们的位置。这里，我们定义一个glm::vec3类的数组来包含这些点光源的坐标：

```c++
glm::vec3 pointLightPositions[] = {
	glm::vec3( 0.7f,  0.2f,  2.0f),
	glm::vec3( 2.3f, -3.3f, -4.0f),
	glm::vec3(-4.0f,  2.0f, -12.0f),
	glm::vec3( 0.0f,  0.0f, -3.0f)
};  
```

同时我们还需要根据这些光源的位置在场景中绘制4个表示光源的立方体，这样的工作我们在之前的教程中已经做过了。

如果你在还是用了手电筒的话，将所有的光源结合起来看上去应该和下图差不多：

![](http://learnopengl.com/img/lighting/multiple_lights_combined.png)

你可以在此处获取本教程的[源代码](http://learnopengl.com/code_viewer.php?code=lighting/multiple_lights)，同时可以查看[顶点着色器](http://learnopengl.com/code_viewer.php?code=lighting/lighting_maps&type=vertex)和[片段着色器](http://learnopengl.com/code_viewer.php?code=lighting/multiple_lights&type=fragment)的代码。

上面的图片的光源都是使用默认的属性的效果，如果你尝试对光源属性做出各种修改尝试的话，会出现很多有意思的画面。很多艺术家和场景编辑器都提供大量的按钮或方式来修改光照以使用各种环境。使用最简单的光照属性的改变我们就足已创建有趣的视觉效果：

![](http://learnopengl.com/img/lighting/multiple_lights_atmospheres.png)

相信你现在已经对OpenGL的光照有很好的理解了。有了这些知识我们便可以创建丰富有趣的环境和氛围了。快试试改变所有的属性的值来创建你的光照环境吧！

###练习

* 创建一个表示手电筒光的结构体Spotlight并实现CalcSpotLight(...)函数：[解决方案](http://learnopengl.com/code_viewer.php?code=lighting/multiple_lights-exercise1)
* 你能通过调节不同的光照属性来重新创建一个不同的氛围吗？[解决方案](http://learnopengl.com/code_viewer.php?code=lighting/multiple_lights-exercise2)