package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
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
	hash = make(map[string]int)
	for id, item := range allOpCategories {
		hash[item] = id
	}

	files, err := getCsvFiles()
	if err != nil {
		panic(err)
	}
	for _, item := range files {
		getStateDigit(item, 3)
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

// 根据传入的csv文件路径进行数据转换并写入同名的txt文件中，参数：（csv文件路径，目标数据列的位置）
func getStateDigit(filepath string, targetidx int) {
	sum := -1 //用于跳过第一行的表头
	file, err := os.Open(fmt.Sprintf("./%s", filepath))
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
	if msg != "" {
		toTXT(filepath, msg)
	}
	log.Println("total", sum, "ops. ")
}

// 以追加方式写入文件
func toTXT(filename string, content string) {
	for i := range filename {
		if filename[i] == '.' {
			filename = filename[:i]
			break
		}
	}
	// newFileNameFront := filepath.Base(filename)
	newFileName := "./" + filename + ".txt"
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
}
