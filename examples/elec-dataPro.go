package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

var hash map[string]int
var allOpCategories []string = []string{"com.fastbee.web.controller.system.SysDeptController.edit()", "com.fastbee.web.controller.monitor.SysUserOnlineController.forceLogout()",
	"com.fastbee.data.controller.GroupController.remove()", "com.fastbee.data.controller.GroupController.add()", "com.fastbee.data.controller.GroupController.updateDeviceGroups()",
	"com.fastbee.data.controller.DeviceController.remove()", "com.fastbee.data.controller.media.SipDeviceController.remove()", "com.fastbee.web.controller.system.SysRoleController.remove()",
	"com.fastbee.web.controller.system.SysProfileController.updateProfile()", "com.fastbee.data.controller.ProductController.changeProductStatus()", "com.fastbee.data.controller.NewsController.remove()",
	"com.fastbee.web.controller.system.SysNoticeController.remove()", "com.fastbee.web.controller.system.SysUserController.remove()", "com.fastbee.web.controller.system.SysRoleController.edit()",
	"com.fastbee.web.controller.system.SysMenuController.edit()", "com.fastbee.data.controller.CategoryController.edit()", "com.fastbee.data.controller.ThingsModelController.add()",
	"com.fastbee.data.controller.DeviceController.add()", "com.fastbee.web.controller.system.SysNoticeController.add()", "com.fastbee.data.controller.CategoryController.add()", "com.fastbee.data.controller.CategoryController.remove()",
	"com.fastbee.web.controller.system.SysProfileController.avatar()", "com.fastbee.data.controller.ProductController.add()", "com.fastbee.data.controller.ThingsModelController.edit()",
	"com.fastbee.data.controller.SocialPlatformController.remove()", "com.fastbee.data.controller.NewsCategoryController.remove()", "com.fastbee.web.controller.system.SysUserController.edit()",
	"com.fastbee.data.controller.ProductController.remove()", "com.fastbee.data.controller.media.SipConfigController.removeByProductId()",
}

func main() {
	args := os.Args[1:]
	if len(args) < 2 || args[0] == "-h" {
		fmt.Println("*****使用说明*****")
		fmt.Println("参数1：待转换文件相对路径\n参数2：日志文件类型（1为物管平台操作日志，2为进程CPU使用率，3为****）")
		fmt.Println("模板：./elec-dataPro [ 参数1 ] [ 参数2 ]")
		fmt.Println("示例：./elec-dataPro ./IOT-manage.csv 1")
		return
	}

	if args[1] == "1" {
		hash = make(map[string]int)
		for id, item := range allOpCategories {
			hash[item] = id
		}
		getStateDigit(args[0], 3)
	} else if args[1] == "2" {
		getCPUusageStateDigit(args[0], 0)
	} else {
		fmt.Println("参数2 无效")
	}
}

// 获取当前目录下所有后缀为.csv的文件列表
func getCsvFiles() ([]string, error) {
	var csvFiles []string
	err := filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && strings.HasSuffix(info.Name(), ".csv") {
			csvFiles = append(csvFiles, path)
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return csvFiles, nil
}

// 用于转换CPU使用率并输出到同名文件，参数：（csv文件路径，目标数据列的位置）
func getCPUusageStateDigit(filepath string, targetidx int) {
	if !isGoodFormat(filepath) {
		log.Println(filepath, "错误的目标文件格式...")
		return
	}
	clrTXT_file(filepath) //先清空目标的txt文件
	sum := -1             //用于跳过第一行的表头
	file, err := os.Open(filepath)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	msg := ""
	for {
		line, err := reader.Read()
		if sum == -1 {
			sum++
			continue
		}
		if err == io.EOF {
			break
		} else if err != nil {
			panic(err)
		}
		if targetidx >= len(line) {
			panic("out of index...")
		}
		sum++
		//对浮点百分比数据转换为整数**********************
		dotId := 1
		for i := 0; i < len(line[targetidx]); i++ {
			if line[targetidx][i] == '.' {
				dotId = i
				break
			}
		}
		tmpDGT := line[targetidx][:dotId]
		tmp_1 := convertIn100(tmpDGT)
		//对浮点百分比数据转换为整数**********************
		msg += fmt.Sprintf("%v ", tmp_1)
		if sum%50 == 0 {
			toTXT(filepath, msg)
			msg = ""
		}
	}
	newFileName := toTXT(filepath, msg)
	log.Println("total", sum, "ops into file", newFileName)
}

// 主要用于物管平台操作日志的转换，根据传入的csv文件路径进行数据转换并写入同名的txt文件中，参数：（csv文件路径，目标数据列的位置）
func getStateDigit(filepath string, targetidx int) {
	if !isGoodFormat(filepath) {
		log.Println(filepath, "错误的目标文件格式...")
		return
	}
	clrTXT_file(filepath) //先清空目标的txt文件
	sum := -1             //用于跳过第一行的表头
	file, err := os.Open(filepath)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	reader := csv.NewReader(file)
	msg := ""
	for {
		line, err := reader.Read()
		if sum == -1 {
			sum++
			continue
		}
		if err == io.EOF {
			break
		} else if err != nil {
			panic(err)
		}
		if targetidx >= len(line) {
			panic("out of index...")
		}
		sum++
		_, ok := hash[line[targetidx]]
		if !ok {
			fmt.Printf("category [ %s ] not existing...\n", line[targetidx])
			return
		}
		msg += fmt.Sprintf("%d ", hash[line[targetidx]])
		if sum%50 == 0 {
			toTXT(filepath, msg)
			msg = ""
		}
	}
	newFileName := toTXT(filepath, msg)
	log.Println("total", sum, "ops into file", newFileName)
}

// 以追加方式写入文件，文件名为对传入的相对路径改变文件后缀，并返回新文件名
func toTXT(filename string, content string) string {
	dotIndex := 1
	for i := len(filename) - 1; i >= 0; i-- {
		if filename[i] == '.' {
			dotIndex = i
			break
		}
	}
	// newFileNameFront := filepath.Base(filename)
	newFileName := filename[:dotIndex] + ".txt"
	// 指定要写入的字符串

	// 以读写模式打开文件，如果文件不存在则创建，0644 是文件权限
	file, err := os.OpenFile(newFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatalf("failed to open file: %s", err)
	}
	defer file.Close() // 确保在函数返回前关闭文件

	// 将字符串写入文件
	_, err = file.WriteString(content)
	if err != nil {
		log.Fatalf("failed to write to file: %s", err)
	}

	// 刷新缓冲区，确保所有内容都写入磁盘
	err = file.Sync()
	if err != nil {
		log.Fatalf("failed to flush file: %s", err)
	}
	return newFileName
}

// 预先清空文件同名的txt文件的内容
func clrTXT_file(filename string) {
	//转换为同名的txt文件
	dotIndex := 1
	for i := len(filename) - 1; i >= 0; i-- {
		if filename[i] == '.' {
			dotIndex = i
			break
		}
	}
	// newFileNameFront := filepath.Base(filename)
	newFileName := filename[:dotIndex] + ".txt"
	// 尝试打开文件，如果文件不存在则直接返回
	file, err := os.OpenFile(newFileName, os.O_WRONLY, 0644)
	if err != nil {
		if os.IsNotExist(err) {
			// 文件不存在，不进行任何操作，直接返回
			return
		}
		// 处理其他打开文件时的错误
		panic(err)
	}
	defer file.Close()

	// 清空文件内容
	err = file.Truncate(0)
	if err != nil {
		// 处理截断文件时的错误
		panic(err)
	}
}

// 将传入的字符串数据不断除10，直到在100范围内
func convertIn100(dgt string) int {
	x, err := strconv.Atoi(dgt)
	if err != nil {
		panic(err)
	}
	for x > 100 {
		x = x / 10
	}
	return x
}

// 检查传入的文件名后缀是否为csv
func isGoodFormat(filename string) bool {
	id := -1
	for i := len(filename) - 1; i >= 0; i-- {
		if filename[i] == '.' {
			id = i
			break
		}
	}
	tail := filename[id+1:]
	return tail == "csv"
}
