# 模型

原文     | [Model](http://learnopengl.com/#!Model-Loading/Model)
      ---|---
作者     | JoeyDeVries
翻译     | [Django](http://bullteacher.com/)
校对     | [Geequlim](http://geequlim.com)

现在是时候着手启用Assimp，并开始创建实际的加载和转换代码了。本教程的目标是创建另一个类，这个类可以表达模型(Model)的全部。更确切的说，一个模型包含多个网格(Mesh)，一个网格可能带有多个对象。一个别墅，包含一个木制阳台，一个尖顶或许也有一个游泳池，它仍然被加载为一个单一模型。我们通过Assimp加载模型，把它们转变为多个`Mesh`对象，这些对象是是上一节教程里创建的。

闲话少说，我把Model类的结构呈现给你：

```c++
class Model 
{
    public:
        /*  成员函数   */
        Model(GLchar* path)
        {
            this->loadModel(path);
        }
        void Draw(Shader shader); 
    private:
        /*  模型数据  */
        vector<Mesh> meshes;
        string directory;
        
        /*  私有成员函数   */
        void loadModel(string path);
        void processNode(aiNode* node, const aiScene* scene);
        Mesh processMesh(aiMesh* mesh, const aiScene* scene);
        vector<Texture> loadMaterialTextures(aiMaterial* mat, aiTextureType type, string typeName);
};
```

`Model`类包含一个`Mesh`对象的向量，我们需要在构造函数中给出文件的位置。之后，在构造其中，它通过`loadModel`函数加载文件。私有方法都被设计为处理一部分的Assimp导入的常规动作，我们会简单讲讲它们。同样，我们储存文件路径的目录，这样稍后加载纹理的时候会用到。

函数`Draw`没有什么特别之处，基本上是循环每个网格，调用各自的Draw函数。


```c++
void Draw(Shader shader)
{
    for(GLuint i = 0; i < this->meshes.size(); i++)
        this->meshes[i].Draw(shader);
}
```

## 导入3D模型到OpenGL

为了导入一个模型，并把它转换为我们自己的数据结构，第一件需要做的事是包含合适的Assimp头文件，这样编译器就不会对我们抱怨了。


```c++
#include <assimp/Importer.hpp>
#include <assimp/scene.h>
#include <assimp/postprocess.h>
```

我们将要调用的第一个函数是`loadModel`,它被构造函数直接调用。在`loadModel`函数里面，我们使用Assimp加载模型到Assimp中被称为scene对象的数据结构。你可能还记得模型加载系列的第一个教程中，这是Assimp的数据结构的根对象。一旦我们有了场景对象，我们就能从已加载模型中获取所有所需数据了。

Assimp最大优点是，它简约的抽象了所加载所有不同格式文件的技术细节，用一行可以做到这一切：


```c++
Assimp::Importer importer;
const aiScene* scene = importer.ReadFile(path, aiProcess_Triangulate | aiProcess_FlipUVs);
```

我们先来声明一个`Importer`对象，它的名字空间是`Assimp`，然后调用它的`ReadFile`函数。这个函数需要一个文件路径，第二个参数是后处理（post-processing）选项。除了可以简单加载文件外，Assimp允许我们定义几个选项来强制Assimp去对导入数据做一些额外的计算或操作。通过设置`aiProcess_Triangulate`，我们告诉Assimp如果模型不是（全部）由三角形组成，应该转换所有的模型的原始几何形状为三角形。`aiProcess_FlipUVs`基于y轴翻转纹理坐标，在处理的时候是必须的（你可能记得，我们在纹理教程中，我们说过在OpenGL大多数图像会被沿着y轴反转，所以这个小小的后处理选项会为我们修正这个）。一少部分其他有用的选项如下：

* `aiProcess_GenNormals` : 如果模型没有包含法线向量，就为每个顶点创建法线。
* `aiProcess_SplitLargeMeshes` : 把大的网格分成几个小的的下级网格，当你渲染有一个最大数量顶点的限制时或者只能处理小块网格时很有用。
* `aiProcess_OptimizeMeshes` : 和上个选项相反，它把几个网格结合为一个更大的网格。以减少绘制函数调用的次数的方式来优化。

Assimp提供了后处理说明，你可以从这里找到所有内容。事实上通过Assimp加载一个模型超级简单。困难的是使用返回的场景对象把加载的数据变换到一个Mesh对象的数组。

完整的`loadModel`函数在这里列出：


```c++
void loadModel(string path)
{
    Assimp::Importer import;
    const aiScene* scene = import.ReadFile(path, aiProcess_Triangulate | aiProcess_FlipUVs); 
 
    if(!scene || scene->mFlags == AI_SCENE_FLAGS_INCOMPLETE || !scene->mRootNode) 
    {
        cout << "ERROR::ASSIMP::" << import.GetErrorString() << endl;
        return;
    }
    this->directory = path.substr(0, path.find_last_of('/'));
 
    this->processNode(scene->mRootNode, scene);
}
```

在我们加载了模型之后，我们检验是否场景和场景的根节点为空，查看这些标记中的一个来看看返回的数据是否完整。如果发生了任何一个错误，我们通过导入器（impoter）的`GetErrorString`函数返回错误报告。我们同样重新获取文件的目录路径。

如果没什么错误发生，我们希望处理所有的场景节点，所以我们传递第一个节点（根节点）到递归函数`processNode`。因为每个节点（可能）包含多个子节点，我们希望先处理父节点再处理子节点，以此类推。这符合递归结构，所以我们定义一个递归函数。递归函数就是一个做一些什么处理之后，用不同的参数调用它自身的函数，此种循环不会停止，直到一个特定条件发生。在我们的例子里，特定条件是所有的节点都被处理。

也许你记得，Assimp的结构，每个节点包含一个网格集合的索引，每个索引指向一个在场景对象中特定的网格位置。我们希望获取这些网格索引，获取每个网格，处理每个网格，然后对其他的节点的子节点做同样的处理。`processNode`函数的内容如下：


```c++
void processNode(aiNode* node, const aiScene* scene)
{
    // 添加当前节点中的所有Mesh
    for(GLuint i = 0; i < node->mNumMeshes; i++)
    {
        aiMesh* mesh = scene->mMeshes[node->mMeshes[i]]; 
        this->meshes.push_back(this->processMesh(mesh, scene)); 
    }
    // 递归处理该节点的子孙节点
    for(GLuint i = 0; i < node->mNumChildren; i++)
    {
        this->processNode(node->mChildren[i], scene);
    }
}
```

我们首先利用场景的`mMeshes`数组来检查每个节点的网格索引以获取相应的网格。被返回的网格被传递给`processMesh`函数，它返回一个网格对象，我们可以把它储存在`meshes`的list或vector（STL里的两种实现链表的数据结构）中。

一旦所有的网格都被处理，我们遍历所有子节点，同样调用processNode函数。一旦一个节点不再拥有任何子节点，函数就会停止执行。

!!! Important

    认真的读者会注意到，我们可能基本忘记处理任何的节点，简单循环出场景所有的网格，而不是用索引做这件复杂的事。我们这么做的原因是，使用这种节点的原始的想法是，在网格之间定义一个父-子关系。通过递归遍历这些关系，我们可以真正定义特定的网格作为其他网格的父（节点）。
    
    关于这个系统的一个有用的例子是，当你想要平移一个汽车网格需要确保把它的子（节点）比如，引擎网格，方向盘网格和轮胎网格都进行平移；使用父-子关系这样的系统很容易被创建出来。
    
    现在我们没用这种系统，但是无论何时你想要对你的网格数据进行额外的控制，这通常是一种坚持被推荐的做法。这些模型毕竟是那些定义了这些节点风格的关系的艺术家所创建的。

下一步是用上个教程创建的`Mesh`类开始真正处理Assimp的数据。

### 从Assimp到网格

把一个`aiMesh`对象转换为一个我们自己定义的网格对象并不难。我们所要做的全部是获取每个网格相关的属性并把这些属性储存到我们自己的对象。通常`processMesh`函数的结构会是这样：


```c++
Mesh processMesh(aiMesh* mesh, const aiScene* scene)
{
    vector<Vertex> vertices;
    vector<GLuint> indices;
    vector<Texture> textures;
 
    for(GLuint i = 0; i < mesh->mNumVertices; i++)
    {
        Vertex vertex;
        // 处理顶点坐标、法线和纹理坐标
        ...
        vertices.push_back(vertex);
    }
    // 处理顶点索引
    ...
    // 处理材质
    if(mesh->mMaterialIndex >= 0)
    {
        ...
    }
 
    return Mesh(vertices, indices, textures);
}
```

处理一个网格基本由三部分组成：获取所有顶点数据，获取网格的索引，获取相关材质数据。处理过的数据被储存在3个向量其中之一里面，一个Mesh被以这些数据创建，返回到函数的调用者。

获取顶点数据很简单：我们定义一个`Vertex`结构体，在每次遍历后我们把这个结构体添加到`Vertices`数组。我们为存在于网格中的众多顶点循环（通过`mesh->mNumVertices`获取）。在遍历的过程中，我们希望用所有相关数据填充这个结构体。每个顶点位置会像这样被处理：


```c++
glm::vec3 vector; 
vector.x = mesh->mVertices[i].x;
vector.y = mesh->mVertices[i].y;
vector.z = mesh->mVertices[i].z; 
vertex.Position = vector;
```

注意，为了传输Assimp的数据，我们定义一个`vec3`的宿主，我们需要它是因为Assimp维持它自己的数据类型，这些类型用于向量、材质、字符串等。这些数据类型转换到glm的数据类型时通常效果不佳。

!!! Important

    Assimp调用他们的顶点位置数组`mVertices`真有点违反直觉。

对应法线的步骤毫无疑问是这样的：


```c++
vector.x = mesh->mNormals[i].x;
vector.y = mesh->mNormals[i].y;
vector.z = mesh->mNormals[i].z;
vertex.Normal = vector;
```

纹理坐标也基本一样，但是Assimp允许一个模型的每个顶点有8个不同的纹理坐标，我们可能用不到，所以我们只关系第一组纹理坐标。我们也希望检查网格是否真的包含纹理坐标（可能并不总是如此）:


```c++
if(mesh->mTextureCoords[0]) // Does the mesh contain texture coordinates?
{
    glm::vec2 vec;
    vec.x = mesh->mTextureCoords[0][i].x; 
    vec.y = mesh->mTextureCoords[0][i].y;
    vertex.TexCoords = vec;
}
else
    vertex.TexCoords = glm::vec2(0.0f, 0.0f);
```

`Vertex`结构体现在完全被所需的顶点属性填充了，我们能把它添加到`vertices`向量的尾部。要对每个网格的顶点做相同的处理。

### 顶点

Assimp的接口定义每个网格有一个以面（faces）为单位的数组，每个面代表一个单独的图元，在我们的例子中（由于`aiProcess_Triangulate`选项）总是三角形，一个面包含索引，这些索引定义我们需要绘制的顶点以在那样的顺序提供给每个图元，所以如果我们遍历所有面，把所有面的索引储存到`indices`向量，我们需要这么做：


```c++
for(GLuint i = 0; i < mesh->mNumFaces; i++)
{
    aiFace face = mesh->mFaces[i];
    for(GLuint j = 0; j < face.mNumIndices; j++)
        indices.push_back(face.mIndices[j]);
}
```

所有外部循环结束后，我们现在有了一个完整点的顶点和索引数据来绘制网格，这要调用`glDrawElements`函数。可是，为了结束这个讨论，并向网格提供一些细节，我们同样希望处理网格的材质。

 

### 材质

如同节点，一个网格只有一个指向材质对象的索引，获取网格实际的材质，我们需要索引场景的`mMaterials`数组。网格的材质索引被设置在`mMaterialIndex`属性中，通过这个属性我们同样能够检验一个网格是否包含一个材质：

```c++
if(mesh->mMaterialIndex >= 0)
{
    aiMaterial* material = scene->mMaterials[mesh->mMaterialIndex];
    vector<Texture> diffuseMaps = this->loadMaterialTextures(material, 
                                        aiTextureType_DIFFUSE, "texture_diffuse");
    textures.insert(textures.end(), diffuseMaps.begin(), diffuseMaps.end());
    vector<Texture> specularMaps = this->loadMaterialTextures(material, 
                                        aiTextureType_SPECULAR, "texture_specular");
    textures.insert(textures.end(), specularMaps.begin(), specularMaps.end());
}
```

我么先从场景的`mMaterials`数组获取`aimaterial`对象，然后，我们希望加载网格的漫反射贴图和（或者）镜面贴图。一个材质储存了一个数组，这个数组为每个纹理类型提供纹理位置。不同的纹理类型都以`aiTextureType_`为前缀。我们使用一个帮助函数：`loadMaterialTextures`来从材质获取纹理。这个函数返回一个`Texture`结构体的向量，我们在之后储存在模型的`textures`坐标的后面。

`loadMaterialTextures`函数遍历所有给定纹理类型的纹理位置，获取纹理的文件位置，然后加载生成纹理，把信息储存到`Vertex`结构体。看起来像这样：


```c++
vector<Texture> loadMaterialTextures(aiMaterial* mat, aiTextureType type, string typeName)
{
    vector<Texture> textures;
    for(GLuint i = 0; i < mat->GetTextureCount(type); i++)
    {
        aiString str;
        mat->GetTexture(type, i, &str);
        Texture texture;
        texture.id = TextureFromFile(str.C_Str(), this->directory);
        texture.type = typeName;
        texture.path = str;
        textures.push_back(texture);
    }
    return textures;
}
```

我们先通过`GetTextureCount`函数检验材质中储存的纹理，以期得到我们希望得到的纹理类型。然后我们通过`GetTexture`函数获取每个纹理的文件位置，这个位置以`aiString`类型储存。然后我们使用另一个帮助函数，它被命名为：`TextureFromFile`加载一个纹理（使用SOIL），返回纹理的ID。你可以查看列在最后的完整的代码，如果你不知道这个函数应该怎样写出来的话。

!!! Important

    注意，我们假设纹理文件与模型是在相同的目录里。我们可以简单的链接纹理位置字符串和之前获取的目录字符串（在`loadModel`函数中得到的）来获得完整的纹理路径（这就是为什么`GetTexture`函数同样需要目录字符串）。
    
    有些在互联网上找到的模型使用绝对路径，它们的纹理位置就不会在每台机器上都有效了。例子里，你可能希望手工编辑这个文件来使用本地路径为纹理所使用（如果可能的话）。

这就是使用Assimp来导入一个模型的全部了。你可以在这里找到[Model类的代码](http://learnopengl.com/code_viewer.php?code=model_loading/model_unoptimized)。

# 重大优化

我们现在还没做完。因为我们还想做一个重大的优化（但是不是必须的）。大多数场景重用若干纹理，把它们应用到网格；还是思考那个别墅，它有个花岗岩的纹理作为墙面。这个纹理也可能应用到地板、天花板，楼梯，或者一张桌子、一个附近的小物件。加载纹理需要不少操作，当前的实现中一个新的纹理被加载和生成，来为每个网格使用，即使同样的纹理之前已经被加载了好几次。这会很快转变为你的模型加载实现的瓶颈。

所以我们打算添加一个小小的微调，把模型的代码改成，储存所有的已加载纹理到全局。无论在哪儿我们都要先检查这个纹理是否已经被加载过了。如果加载过了，我们就直接使用这个纹理并跳过整个加载流程来节省处理能力。为了对比纹理我们同样需要储存它们的路径：


```c++
struct Texture {
    GLuint id;
    string type;
    aiString path;  // We store the path of the texture to compare with other textures
};
```

然后我们把所有加载过的纹理储存到另一个向量中，它是作为一个私有变量声明在模型类的顶部：


```c++
vector<Texture> textures_loaded;
```

然后，在`loadMaterialTextures`函数中，我们希望把纹理路径和所有`texture_loaded`向量对比，看看是否当前纹理路径和其中任何一个是否相同，如果是，我们跳过纹理加载/生成部分，简单的使用已加载纹理结构体作为网格纹理。这个函数如下所示：


```c++
vector<Texture> loadMaterialTextures(aiMaterial* mat, aiTextureType type, string typeName)
{
    vector<Texture> textures;
    for(GLuint i = 0; i < mat->GetTextureCount(type); i++)
    {
        aiString str;
        mat->GetTexture(type, i, &str);
        GLboolean skip = false;
        for(GLuint j = 0; j < textures_loaded.size(); j++)
        {
            if(textures_loaded[j].path == str)
            {
                textures.push_back(textures_loaded[j]);
                skip = true; 
                break;
            }
        }
        if(!skip)
        {   // 如果纹理没有被加载过，加载之
            Texture texture;
            texture.id = TextureFromFile(str.C_Str(), this->directory);
            texture.type = typeName;
            texture.path = str;
            textures.push_back(texture);
            this->textures_loaded.push_back(texture);  // 添加到纹理列表 textures
        }
    }
    return textures;
}
```

所以现在我们不仅有了一个通用模型加载系统，同时我们也得到了一个能使加载对象更快的优化版本。

!!! Attention

    有些版本的Assimp当使用调试版或/和使用你的IDE的调试模式时，模型加载模型实在慢，所以确保在当你加载得很慢的时候用发布版再测试。

你可以从这里获得优化的[Model类的完整源代码](http://learnopengl.com/code_viewer.php?code=model&type=header)。

# 和箱子模型告别

现在给我们导入一个天才艺术家创建的模型看看效果，不是我这个天才做的（你不得不承认，这个箱子也许是你见过的最漂亮的立方体）。因为我不想过于自夸，所以我会时不时的给其他艺术家进入这个行列的机会，这次我们会加载Crytek的原版孤岛危机游戏中的纳米铠甲。这个模型被输出为obj和mtl文件，mtl包含模型的漫反射贴图，镜面贴图以及法线贴图（后面会讲）。你可以[下载这个模型](http://learnopengl.com/data/models/nanosuit.rar)，注意，所有的纹理和模型文件都应该放在同一个目录，以便载入纹理。

!!! Important
    
    你从这个站点下载的版本是修改过的版本，每个纹理文件路径已经修改改为本地相对目录，原来的资源是绝对目录。

现在在代码中，声明一个Model对象，把它模型的文件位置传递给它。模型应该自动加载（如果没有错误的话）在游戏循环中使用它的Draw函数绘制这个对象。没有更多的缓冲配置，属性指针和渲染命令，仅仅简单的一行。如果你创建几个简单的着色器，像素着色器只输出对象的漫反射贴图颜色，结果看上去会有点像这样：

![](../img/03/03/model_diffuse.png)

你可以从这里找到带有[顶点](http://learnopengl.com/code_viewer.php?code=model_loading/model&type=vertex)和[片段](http://learnopengl.com/code_viewer.php?code=model_loading/model&type=fragment)着色器的[完整的源码](http://learnopengl.com/code_viewer.php?code=model_loading/model_diffuse)。

因为我们之前学习过光照教程，可以更加富有创造性的引入两个点光源渲染方程，结合镜面贴图获得惊艳效果：

![](../img/03/03/model_lighting.png)

甚至我不得不承认这个相比之前用过的容器酷炫多了。使用Assimp，你可以载入无数在互联网上找到的模型。有相当多可以以多种文件格式下载免费3D模型的资源网站。一定注意，有些模型仍然不能很好的载入，纹理路径无效或者这种格式Assimp不能读取。

## 练习

你可以使用两个点光源重建上个场景吗？[方案](http://learnopengl.com/code_viewer.php?code=model_loading/model-exercise1)，[着色器](http://learnopengl.com/code_viewer.php?code=model_loading/model-exercise1-shaders)。
