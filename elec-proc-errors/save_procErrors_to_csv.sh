#!/bin/bash

realpath=$(realpath "$0")
curdir=$(dirname "$realpath")
# echo "当前目录：${curdir}"
cd ${curdir}

# 使用sysdig获取进程产生错误信息数量，并通过awk处理成CSV格式
sudo sysdig -c topprocs_errors | tr -d '\r' | grep mysqld | awk 'BEGIN {print "Errors"} {print $1","$2","$3}' > ./auto-data/data-main.csv
