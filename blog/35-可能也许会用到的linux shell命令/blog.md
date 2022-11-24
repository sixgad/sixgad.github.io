tags: linux shell
date: 2022年11月9日
title: 可能也许会用到的linux shell命令
private: false

# 可能也许会用到的linux shell命令

嗯，，，shell到用时方恨少。



**统计当前文件夹下有几种文件类型**

```shell
find . -type f | sed -n 's/..*\.//p' | sort | uniq -c
```



**统计当前文件夹下所有json文件行数**

```shell
awk 'END{print NR}' *.json
```



**进阶：结合xargs，统计22年10月所有json文件行数**

```shell
ls -al | grep '202210'| awk '{print $9}'  | xargs -I {} awk 'END{print NR}' {} | awk '{sum+=$1} END{print "sum="sum}'
```



**批量kill程序**

```shell
ps aux | grep -v grep | grep programname | awk '{print $2}' | xargs kill
```



**显示当前文件夹下size最大的前十个文件**

```shell
ls -lSh  | head -n 10
```

or

```shell
du -h ./ | sort -hr | head -n 10
```



**显示当前文件夹下时间最新的前十个文件**

```shell
ls -lt | head -n 10
#倒序 
ls -rlt | head -n 10
```

