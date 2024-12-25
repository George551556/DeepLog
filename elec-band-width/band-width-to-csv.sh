#!/bin/bash
# 使用sysdig获取进程信息，并通过awk处理成CSV格式
sudo sysdig -c topprocs_net | awk 'BEGIN{print "Bytes,Process,PID"} $3 == 722{print $1","$2","$3}'
