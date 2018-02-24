# 音效

原文    | [Audio](https://learnopengl.com/#!In-Practice/2D-Game/Audio)
-----   |  ----
作者    | JoeydeVries
翻译    | [包纸](https://github.com/ShirokoSama)
校对    | 暂无

!!! note

	本节暂未进行完全的重写，错误可能会很多。如果可能的话，请对照原文进行阅读。如果有报告本节的错误，将会延迟至重写之后进行处理。

无论我们将游戏音量调到多大，我们都不会听到来自游戏的任何音效。我们已经展示了这么多内容，但没有任何音频，游戏仍显得有些空洞。在本节教程中，我们将解决这个问题。

OpenGL不提供关于音频的任何支持。我们不得不手动将音频加载为字节格式，处理并将其转化为音频流，并适当地管理多个音频流以供我们的游戏使用。然而这有一些复杂，并且需要一些底层的音频工程知识。

如果你乐意，你可以手动加载来自多种扩展名的音频文件的音频流。然而，我们将使用被称为irrKlang的音频管理库。

## irrKlang

<img alt="GLM Logo" src="../../img/06/Breakout/09/irrklang.png" class="right" />

IrrKlang是一个可以播放WAV，MP3，OGG和FLAC文件的高级二维和三维（Windows，Mac OS X，Linux）声音引擎和音频库。它还有一些可以自由调整的音频效果，如混响、延迟和失真。

!!! important

    3D音频意味着音频源可以有一个3D位置，然后根据相机到音频源的位置衰减音量，使其在一个3D世界里显得自然（想想3D世界中的枪声，通常你可以从音效中听出它来自什么方向/位置）。

IrrKlang是一个易于使用的音频库，只需几行代码便可播放大多数音频文件，这使它成为我们Breakout游戏的完美选择。请注意，irrKlang有一个有一定限制的证书：允许你将irrKlang用于非商业目的，但是如果你想使用irrKlang商业版，就必须支付购买他们的专业版。由于Breakout和本教程系列是非商业性的，所以我们可以自由地使用他们的标准库。

你可以从他们的[下载页面](http://www.ambiera.com/irrklang/downloads.html)下载irrKlang，我们将使用1.5版本。由于irrKlang是非开源的代码，因此我们不得不使用irrKlang为我们提供的任何东西。幸运的是，他们有大量的预编译库文件，所以你们大多数人应该可以很好地使用它。

你需要引入了irrKlang的头文件，将他们的库文件（irrKlang.lib）添加到链接器设置中，并将他们的dll文件复制到适当的目录下（通常和.exe在同一目录下）。需要注意的是，如果你想要加载MP3文件，则还需要引入ikpMP3.dll文件。

## 添加音乐

为了这个游戏我特制了一个小小的音轨，让游戏更富有活力。在[这里](https://learnopengl.com/audio/in-practice/breakout/breakout.mp3)你可以找到我们将要用作游戏背景音乐的音轨。这个音轨会在游戏开始时播放并不断循环直到游戏结束。你可以随意用自己的音频替换它，或者用喜欢的方式使用它。

<audio src="https://learnopengl.com/audio/in-practice/breakout/breakout.mp3" controls="controls"></audio>

利用irrKlang库将其添加到Breakout游戏里非常简单。我们引入相应的头文件，创建<fun>irrKlang::ISoundEngine</fun>，用<fun>createIrrKlangDevice</fun>初始化它并使用这个引擎加载、播放音频：

```c++
#include <irrklang/irrKlang.h>
using namespace irrklang;

ISoundEngine *SoundEngine = createIrrKlangDevice();
  
void Game::Init()
{
    [...]
    SoundEngine->play2D("audio/breakout.mp3", GL_TRUE);
}
```

在这里，我们创建了一个<fun>SoundEngine</fun>，用于管理所有与音频相关的代码。一旦我们初始化了引擎，便可以调用<fun>play2D</fun>函数播放音频。第一个参数为文件名，第二个参数为是否循环播放。

这就是全部了！现在运行游戏会使你的耳机或扬声器迸发出声波。

## 添加音效

我们还没有结束，因为音乐本身并不能使游戏完全充满活力。我们希望在游戏发生一些有趣事件时播放音效，作为给玩家的额外反馈，如我们撞击砖块、获得道具时。下面你可以找到我们需要的所有音效（来自freesound.org）：

[bleep.mp3](https://learnopengl.com/audio/in-practice/breakout/bleep.mp3): 小球撞击非实心砖块时的音效

<audio src="https://learnopengl.com/audio/in-practice/breakout/bleep.mp3" controls="controls"></audio>

[solid.wav](https://learnopengl.com/audio/in-practice/breakout/solid.wav)：小球撞击实心砖块时的音效

<audio src="https://learnopengl.com/audio/in-practice/breakout/solid.wav" controls="controls"></audio>

[powerup.wav](https://learnopengl.com/audio/in-practice/breakout/powerup.wav): 获得道具时的音效

<audio src="https://learnopengl.com/audio/in-practice/breakout/powerup.wav" controls="controls"></audio>

[bleep.wav](https://learnopengl.com/audio/in-practice/breakout/bleep.wav): 小球在挡板上反弹时的音效

<audio src="https://learnopengl.com/audio/in-practice/breakout/bleep.wav" controls="controls"></audio>

无论在哪里发生碰撞，我们都会播放相应的音效。我不会详细阐述每一行的代码，并把更新后的代码放在了[这里](https://learnopengl.com/code_viewer.php?code=in-practice/breakout/game_audio)，你应该可以轻松地找到相应的添加音效的地方。

把这些集成在一起后我们的游戏显得更完整了，就像这样：

<video src="https://learnopengl.com/video/in-practice/breakout/audio.mp4" controls="controls"></video>

IrrKlang允许一些更精细的音频管理功能，如内存管理、声音特效和声音事件回调。看看他们的C++[教程](http://www.ambiera.com/irrklang/tutorials.html)并尝试一些功能吧。

