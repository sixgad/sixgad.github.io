tags: linux shell
date: 2022年11月11日
title: ssh,rsync,sftp使用代理
private: false

# ssh,rsync,sftp使用代理

本文摘自超哥blog，https://mkmerich.com/2022-09-16/ssh,rsync,sftp%E4%BD%BF%E7%94%A8%E4%BB%A3%E7%90%86.html

**前提**

首先rsync, ssh, sftp都必须使用socks代理，如果只有http代理，那么需要先把http代理转为socks代理。下面讲方法：

网上有很多开源软件，可以把http代理转化为socks代理，本文利用python-proxy, 地址在： https://github.com/qwj/python-proxy

并非所有的http代理都能连通通ssh, 必须支持https。其次ssh服务需要运行在443端口，因为有些http代理处于某些考虑不支持底层代理方式

```shell
$pip install pproxy
$pproxy -l socks5://:8888  -r  http://my-http-proxy-ip:1080 # 这样就把我再1080端口的一个http代理转为本机ip端口8888的一个socks5代理
```

**ssh 使用代理**

```shell
ssh -p 443  root@my-ssh-host -o ProxyCommand="connect-proxy -S 127.0.0.1:8888 %h %p" 
```

`connect-proxy` 是一个linux命令，如果没有则去安装吧，具体自己google一下。

如果不想输入-o后面一长串，可以配置`~/.ssh/config`：

```shell
# 本人在centos7验证可以
Host foobar.example.com
    ProxyCommand          connect-proxy -S 127.0.0.1:8888 %h %p
    User root   # 这样ssh登录的时候可以不用指定登录名字， 可以直接用  ssh host
    ServerAliveInterval   10
    Port 443  # ssh 目标IP，写了这一行就不用在命令行规定端口了
```

然后：`ssh root@foobar.example.com`

还能配置免密登录，使用key，请参考连接，这里面各种用法都讲清楚了

https://stackoverflow.com/questions/19161960/connect-with-ssh-through-a-proxy, 强烈推荐仔细阅读

**rsync使用代理**

```shell
rsync -Pavzr  -e "ssh -o -p 443 'ProxyCommand connect-proxy -S 127.0.0.1:8888 %h %p'"   /mnt/src     root@xxxx:/mnt/mydir
```

看起来原理很简单，就是指定使用某个ssh命令。

如果你按照本文`ssh 使用代理一节`配置了 `~/.ssh/config`的话，那么可以简写成如下的样子：

```shell
rsync -Pavzr   /mnt/src     root@foobar.example.com:/mydata
```

**sftp使用代理**

```shell
scp -P 443 -o "ProxyCommand connect-proxy -S 127.0.0.1:8888 %h %p"  linuxUser@111.111.11.11:/root/youtube   /mnt/local/dir
```

同样如果配置了 `~/.ssh/config`的话，无需额外参数：

```shell
scp   linuxUser@111.111.11.11:/root/youtube   /mnt/local/dir
```

**scp使用代理**

首先我建议的方案是按照本文`ssh使用代理`一节配置 `~/.ssh/config`。这样会让命令十分简单：

```shell
scp  root@foobar.example.com:/root/youtube   /mnt/local/dir
```

否则用如下命令

```shell
scp -P 443 -o "ProxyCommand connect-proxy -S 127.0.0.1:8888 %h %p"  linuxUser@xxx.xxx.xxx.xxx:/root/youtube   /mnt/local/dir
```

**总结**

总之使用ssh协议的命令只需要修改 `~/.ssh/config` 规定好目标端口，代理，用户，甚至秘钥， rsync, ssh, sfpt, scp命令可以无需做任何修改，不需要额外参数。