tags: linux nas
date: 2022年11月22日
title: ubuntu nfs服务搭建&挂载
private: false

# ubuntu nfs服务搭建&挂载

NFS（NetworkFileSystem）即网络文件系统，是FreeBSD支持的文件系统中的一种，它允许网络中的计算机之间通过TCP/IP网络共享资源。在NFS的应用中，本地NFS的客户端应用可以透明地读写位于远端NFS服务器上的文件，就像访问本地文件一样。

## 服务端

**1.安装NFS服务**

```shell
apt install nfs-kernel-server 
```

**2.创建服务端要共享的目录**

> mkdir /root/nfs
>
> chmod -R 777 /root/nfs  #放开权限

**3.编辑/etc/exports文件，追加写入**

```shell
/root/nfs 2.*.*.1(rw,async,no_root_squash,no_subtree_check)
```

此配置理解为，某ip主机(客户端)可以挂载服务端/root/nfs目录

rw ：挂接此目录的客户端对该共享目录具有读写权限

sync ：资料同步写入内存和硬盘

no_root_squash ：root用户具有对根目录的完全管理访问权限。

no_subtree_check：不检查父目录的权限

**4.重启nfs server**

```shell
systemctl restart nfs-kernel-server.service
```

## 客户端

**1.安装 nfs-common**

```shell
apt install nfs-common
```

**2.将服务端目录/root/nfs挂载到到当前 /mnt 目录下**

```shell
mount -t nfs 服务端ip:/root/nfs /mnt
```

