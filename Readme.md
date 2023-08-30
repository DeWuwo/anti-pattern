# 切面耦合模式检测工具使用说明

## 概况

本工具以静态代码工具enre-java为底层数据输入，扫描伴生移动操作系统基于原生AOSP代码的耦合切面及反模式

## 环境配置

#### java11以上

一、下载地址：https://www.oracle.com/java/technologies/javase-jdk17-downloads.html

二、解压移动文件

1、JDK压缩包所在目录解压：tar zxvf jdk-17.0.7-linux-x64.tar.gz  #解压得到jdk17.0.7文件夹 

2、进入local目录：cd /usr/local

3、创建文件夹jvm  ：sudo mkdir jvm  #提示输入的密码是管理员密码

4、回到第一步坐在目录；给文件夹授权：sudo chmod 777 *

5、移动解压得到文件至jvm：sudo mv jdk17.0.7 /usr/local/jvm/   #提示输入的密码是管理员密码。

三、配置环境变量（注意路径，每句话前后不能留空格） 

1、打开配置文件： /etc/profile 

2、在文档最后添加以下四行语句，保存，关闭

```shell
export JAVA_HOME=/usr/local/jvm/jdk17.0.7

export JRE_HOME=$JAVA_HOME/jre

export CLASSPATH=$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH

export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH
```

3、启用配置的环境变量：source  /etc/profile 

4、验证配置启用结果：java -version

#### python3.8以上

一、确认python环境

服务器默认安装python3.6 python3.7 以及python3.8版本，如未包含，安装过程如下

1、下载python安装压缩包

 [Index of /ftp/python/3.8.3/](https://www.python.org/ftp/python/3.8.3/) 

2、解压安装包：tar -zxvf Python-3.8.3.tgz

3、进入解压目录：cd Python-3.8.3

4、配置安装目录：./configure --prefix=/usr/local/python3

5、编译安装：sudo make install

6、建立软连接：

```shell
sudo ln -s /usr/local/python3/bin/python3.8 /usr/local/bin/python38 
sudo ln -s /usr/local/python3/bin/pip3.8 /usr/bin/pip3
```

7、测试配置结果：python38

二、安装库 GitPython

```
pip -i http://mirrors.heds.hihonor.com/pypi/web/simple install GitPython --trusted-host=mirrors.heds.hihonor.com     
```



## 使用方法

### 基本流程概况

1. 步骤一：获取原生代码仓(存放路径如：/user/TAOSP)，伴生代码仓(存放路径如：/user/TMagic)
2. 步骤二：使用enre-java工具分别扫描原生代码仓及伴生代码仓，在两个代码仓目录下分别生成输出结果文件（/user/TAOSP/base-enre_out/base-out.json   /user/TMagic/base-enre_out/base-out.json）（hidden、解耦仓、反射、/tests包过滤）
3. 步骤三：以步骤二结果为输入，使用enre-anti工具扫描原生代码仓及伴生代码仓获取最终结果

### 使用详情

#### 步骤一

基于git，clone待检测的伴生荣耀代码仓以及原生代码仓

#### 步骤二

基于enre-java生成静态代码依赖结果

#### 步骤三

###### 1.将Refacor工具放置于某目录下

enre-anti工具内部包含一个`refactoringMiner`工具，该工具单独一个目录文件夹存放，`refactoringMiner`工具包含/bin 以及 /lib目录两部分，放置于特定目录即可（如/user/Refactor最终包含/user/Refactor/lib  /user/Refactor/bin）

###### 2.调整步骤二输出结果存放路径

指定输出目录（如：/user/TRes），将步骤二结果存放至输出目录并重命名避免覆盖（如：/user/TRes/base-out_TAOSP.json  /user/TRes/base-out_TMagic.json）

###### 3.使用anti-pattern工具

进入`anti-pattern`工具代码根目录（如：/user/anti-pattern），运行工具

```powershell
python main.py -ra <aosp_code> -re <honor_code> -a <aosp_dep> -e <honor_dep> -ref <ref_path> -o <output>

// 以上述场景为例
python main.py -ra /user/TAOSP/frameworks/base -re /user/TMagic/frameworks/base -a /user/TRes/base-out_TAOSP.json -e /user/TRes/base-out_TMagic.json -ref /user/Refactor -o /user/TRes
```

- <aosp_code> `Aosp` 项目本地路径
- <honor_code>`Honor` 项目本地路径
- <aosp_dep> 基于`enre-java`工具扫描`aosp`原生项目路径的依赖结果
- <honor_dep>基于`enre-java`工具扫描`honor`伴生项目路径的依赖结果
- <ref_path>`refactoringMiner`工具的存放路径
- <out_path>输出路径

```
// 以上述场景为例，命令如下
python main.py -ra /user/TAOSP/frameworks/base -re /user/TMagic/frameworks/base -a /user/TRes/base-out_TAOSP.json -e /user/TRes/base-out_TMagic.json -ref /user/Refactor -o /user/TRes
```

