#春物游戏renpy移植项目(WIP)

基于 https://github.com/CommitteeOfZero/sc3ntist 反编译的脚本制作(有改动)  
目前已经转换了部分语句，但是有些指令的功能仍然不完善
人物立绘部分还有很多工作要做，比如嘴动系统很垃圾

##接下来要做的
- 修整代码  
- 实现表相关功能 
    LabelTable  
    ~~DataAccess(放弃实现)~~   
    JumpTable
    
- 编写完善人物系统  
- 转换其余重要指令  
- 编写对话卡功能  
- 编写废人计数器功能  
- patch功能，便于手写动画或者特效(完成) 

##项目目录说明
- assets/ : 放代码中需要使用的资源  
- chara_lay_tool/ : 提取春物的人物立绘图片  
- generate_special_script/ : 生成特殊的renpy脚本  
- parser/ : 脚本转换器，将反编译的脚本转换成renpy脚本  
- YouthRomanticComedy/ : renpy游戏工程文件夹  

##想参与开发的事项
- 项目中的资源文件由于太大所以排除在外了，下载地址链接：https://pan.baidu.com/s/1ehwUZEXfl2C8vhF4GJPraQ 密码：4d8i  
- 资源文件解压至/YouthRomanticComedy/game/即可 
- 由于本人比较菜而且懒，代码可读性差，所以看不懂代码比较正常，问哇就好了  
- 用到的脚本文件可以在项目文件里下载  