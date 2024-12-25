#!/bin/bash
# 使用sysdig获取进程产生错误信息数量，并通过awk处理成CSV格式
sudo sysdig -c topprocs_errors | tr -d '\r' | grep firefox | awk 'BEGIN {print "Errors,Process,PID"} {print $1","$2","$3}'
