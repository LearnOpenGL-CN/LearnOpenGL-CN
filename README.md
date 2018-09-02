# LearnOpenGL中文化工程

[![Build Status](https://travis-ci.org/LearnOpenGL-CN/LearnOpenGL-CN.svg?branch=new-theme)](https://travis-ci.org/LearnOpenGL-CN/LearnOpenGL-CN)

learnopengl.com系列教程的中文翻译，目前正在校对及翻译中。

**英文原版**：[learnopengl.com](https://learnopengl.com/)

**目前状态**：

- 原文大部分代码都有改变（使用的新的库），需要从头开始重新校对（Krasjet正在处理中，最重要的配置部分已经更新完毕）
- 5-2节之后都没有按照新版的格式来排版，而且错误极多，也没有统一译名，需要进行整体的修改（Krasjet正在处理中，可能比较漫长）
- 从头校对整体修改之后的文章（志愿者希望）
- PBL 章节和 In Practice 章节下还有几篇教程没有翻译（志愿者希望）

## 阅读地址

目前Host在GitHub上，可以[点击这里](https://learnopengl-cn.github.io/)进行阅读。

旧版本的Host在Read The Docs内（不定时更新），可以[点击这里](http://learnopengl-cn.readthedocs.io/)进行阅读。

## 认领翻译

由于我们的志愿者来自五湖四海，为了避免冲突。请志愿者们先Clone这个Repository 。同步到本地后找到要翻译的文章，创建一个如下所示的只包含作者、翻译者和原文链接信息的Markdown文件：

```
原文     | [英文标题](原文地址)
      ---|---
作者     | JoeyDeVries
翻译     | [翻译]
校对     | 暂无
```

译文的文件命名统一规范为：

```
<两位数的章序列> <章名称>/<两位数节序列> 节名称.md
```

如果有小节的话：

```
<两位数的章序列> <章名称>/<两位数节序列> 节名称/<两位数小节序列> 小节名称.md
```

例如：

```
01 Getting started/01 OpenGL.md
或
05 Advanced Lighting/03 Shadows/02 Point Shadows.md
```

**翻译之前请先阅读[样式指南](https://github.com/LearnOpenGL-CN/LearnOpenGL-CN/blob/new-theme/styleguide.md)**

之后请联系我们，将您加入LearnOpenGL-CN组织，然后提交并Push您的翻译。或者您也可以Fork这个工程在本地编辑之后发送Pull Request。

## 样式指南

在文档的写作过程中，请遵守我们的[样式指南](https://github.com/LearnOpenGL-CN/LearnOpenGL-CN/blob/new-theme/styleguide.md)方便之后的校对以及修改工作。

## 构建

首先请安装Python，2和3都可以，之后初始化环境：

```bash
$ pip install mkdocs
$ python setup.py install
```

初始化以后，每次构建只需要输入以下指令即可，构建后的文件在`site`文件夹内：

```bash
$ mkdocs build
```

如果只是想测试的话，请输入以下指令：

```bash
$ mkdocs serve
```

部署的网页可以通过`127.0.0.1:8000`来访问。

## 建议

如果您发现教程有任何错误的话，欢迎Fork这个工程并发送Pull Request到 `new-theme` 分支。如果您不想修改的话，可以点击页面上方的 `Issues` 按钮提交一个Issue，我们看到后会及时更正。如果是对教程的内容有问题，请先查看原文，如果不是翻译错误的话，请直接在原网站评论区向作者（JoeyDeVries）反馈。

## 联系方式

QQ群：383745868