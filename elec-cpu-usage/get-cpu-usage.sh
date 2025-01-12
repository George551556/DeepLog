#!/bin/bash

realpath=$(realpath "$0")
curdir=$(dirname "$realpath")
# echo "当前目录：${curdir}"
cd ${curdir}

# 使用sysdig命令获取Xorg的CPU使用情况，并使用awk转换为CSV格式
sudo sysdig -c topprocs_cpu "proc.name=redis-server" | \
awk '
BEGIN {FS="\t"; OFS=","; print "CPU%"} # 使用制表符作为字段分隔符，并打印标题
/^-+/ { next } # 忽略分隔线
{
    gsub(/\033\[[0-9;]*[A-Za-z]/, "", $0) # 移除 ANSI 转义序列
    if ($1 ~ /[0-9]+\.[0-9]+/) { # 检查第一列是否为数字和点的组合，即CPU%
        printf "%s%s%s\n", $1, $2, $3 # 使用printf确保不会在末尾添加多余的逗号，直接换行
    }
}
' > ./auto-data/data-main.csv