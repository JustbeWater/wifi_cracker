# WIFI 连接工具
## 介绍  
> + 本工具用于暴力破解WIFI，通过选择WIFI名称和合适的密码本，重复尝试连接对应WIFI，以获得正确密码。
> + 当前仅支持 WPA2 PSK一种加密方式， 仅支持一张网卡，仅支持中文
> + 请备好合适的密码本，如需要密码本生成器，可以看看我的另一个项目[密码本生成器](https://github.com/JustbeWater/password_producer)  
## 使用环境
+ 需要下载 pywifi 库，有需要可以下载 charset 库，用于检测密码本文本编码，减少读出乱码的情况（国内下载速度慢的可以加上[ ]中的参数，选择国内镜像下载会快一些）
```
pip install pywifi charset [-i https://pypi.tuna.tsinghua.edu.cn/simple]
```
+ 虚拟机
    1. 需要购买通过 USB 接口连接电脑的无线网卡（wireless network card)，如 kali 就购买 kali 的免驱动无线网卡， windows 就买 windows 的免驱动无线网卡。如果网卡没有驱动，则需要去网卡对应型号的官网下载并手动安装  
    2. Linux 虚拟机还需要下载 wpa_supplicant 组件
    ```
    sudo apt install wpasupplicant
    ```
    3. 将无线网卡连接到虚拟机（每次开启虚拟机都应该执行此步操作）。以 VMware 为例，在上方菜单栏，“虚拟机 - 可移动设备 - xxx Wireless_Device - 连接（断开与主机的连接）”。
## 使用方法  
+ 命令行方法
```
python wifi.py
```
+ 打包成 .exe 程序运行
```
pyinstaller --windowed --onefile --icon=你的图片文件 wifi.py
```
+ 从该项目的 release 中下载（仅提供windows版本）
## 更多
+ 使用说明和注意事项在工具窗口顶部菜单栏的帮助一栏可见

## 免责声明
+ 本项目、本工具仅供学术交流和学习实验使用，请勿用于违法行为
+ 本项目不承担因该工具引发事件的责任