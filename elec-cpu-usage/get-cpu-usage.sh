#!/bin/bash

# 使用sysdig命令获取Xorg的CPU使用情况，并使用awk转换为CSV格式
sudo sysdig -c topprocs_cpu "proc.name=Xorg" | \
awk '
BEGIN {FS="\t"; OFS=","; print "CPU%,Process,PID"} # 使用制表符作为字段分隔符，并打印标题
/^-+/ { next } # 忽略分隔线
{
    gsub(/\033\[[0-9;]*[A-Za-z]/, "", $0) # 移除 ANSI 转义序列
    if ($1 ~ /[0-9]+\.[0-9]+/) { # 检查第一列是否为数字和点的组合，即CPU%
        printf "%s%s%s\n", $1, $2, $3 # 使用printf确保不会在末尾添加多余的逗号，直接换行
    }
}
'