#!/bin/bash

realpath=$(realpath "$0")
curdir=$(dirname "$realpath")
# echo "当前目录：${curdir}"
cd ${curdir}

# # 使用sysdig获取进程产生错误信息数量，并通过awk处理成CSV格式
# sudo sysdig -c topprocs_errors | tr -d '\r' | awk 'BEGIN {print "Errors"} {print $1","$2","$3}' > ./auto-data/data-main.csv


# 使用sysdig获取进程产生错误信息数量，并通过awk处理成CSV格式
PROC_PID="1234"
sudo sysdig -c topprocs_errors "proc.pid=$PROC_PID" | tr -d '\r' | awk 'BEGIN {print "Errors"} {print $1","$2","$3}' > ./auto-data/data-main.csv
