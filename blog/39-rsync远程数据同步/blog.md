tags: linux
date: 2022年11月11日
title: rsync远程数据同步
private: false

# rsync远程数据同步

**从目标主机123.1.2.3拉取文件夹**

> rsync -avuP root@123.1.2.3:/root/targetdir ./
>
> #注：如果以“/”结尾/root/targetdir/，拉取的机器不会创建targetdir文件夹

**从目标主机123.1.2.3拉取文件**

> rsync -avuP root@123.1.2.3:/root/targetfile.txt ./

**免密**

> sshpass -p "pwd***" rsync -avuP root@123.1.2.3:/root/targetfile.txt ./

**并发同步的思路**

> sshpass -p "pwd***" ssh root@123.1.2.3 "cd /root/targetdir && find -L . " |  xargs  -L 1 -I% -P5  sshpass -p "pwdpwdpwd"  rsync -avuP "root@123.1.2.3:/root/targetdir/%" ./ 
>
> #修改-P后的数字

**软链接情况处理**

> rsync -asvurPKL

**同步完成后，删除目标文件**

> ```
> --remove-source-files
> ```

**排除后缀为part的文件，不参与同步**

> ```
> --exclude='*.part'
> ```