# 1.切换到当前工作目录
realpath=$(realpath "$0")
curdir=$(dirname "$realpath")
# echo "当前目录：${curdir}"
cd ${curdir}

# 2.将数据文件复制一份作为备份文件作为要处理的源文件
cp ./auto-data/data-main.csv ./auto-data/data-main-backup.csv

# 3.进行数据转换
elec-dataPro ./auto-data/data-main-backup.csv 4

# 4.使用Deeplog进行推理并将结果保存到result.txt
echo "$(date +"%Y-%m-%d %H:%M:%S") 推理结果：" >> ./auto-data/result.txt
python_path="/home/karen/miniconda3/envs/deeplog/bin/python"
$python_path ./example.py ./auto-data/data-main-backup.txt >> ./auto-data/result.txt
echo "" >> ./auto-data/result.txt