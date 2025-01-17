#!/bin/bash

realpath=$(realpath "$0")
curdir=$(dirname "$realpath")
# echo "当前目录：${curdir}"
cd ${curdir}

# 使用sysdig获取进程信息，并通过awk处理成CSV格式
# sudo sysdig -c topprocs_net "proc.name = Socket"  | \
# awk '
# BEGIN {FS="\t"; OFS=","; print "Bytes"} # 使用制表符作为字段分隔符，并打印标题
# /^-+/ { next } # 忽略分隔线
# {
#     gsub(/\033\[[0-9;]*[A-Za-z]/, "", $0) # 移除 ANSI 转义序列
#     if ($1 ~ /[0-9]+\.[0-9]+/) { # 检查第一列是否为数字和点的组合，即CPU%
#         printf "%s%s%s\n", $1, $2, $3 # 使用printf确保不会在末尾添加多余的逗号，直接换行
#     }
# }
# ' > ./auto-data/data-main.csv

# 改为使用进程号过滤
PROC_PID="1234"
sudo sysdig -c topprocs_net "proc.pid=$PROC_PID"  | \
awk '
BEGIN {FS="\t"; OFS=","; print "Bytes"} # 使用制表符作为字段分隔符，并打印标题
/^-+/ { next } # 忽略分隔线
{
    gsub(/\033\[[0-9;]*[A-Za-z]/, "", $0) # 移除 ANSI 转义序列
    if ($1 ~ /[0-9]+\.[0-9]+/) { # 检查第一列是否为数字和点的组合，即CPU%
        printf "%s%s%s\n", $1, $2, $3 # 使用printf确保不会在末尾添加多余的逗号，直接换行
    }
}
' > ./auto-data/data-main.csv