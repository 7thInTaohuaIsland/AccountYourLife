import sys
import os
import shutil
from PyQt5 import QtWidgets
from datetime import datetime
from SAK.FileIO import readDictFromJson
from UI.MainWindow import MainWindow
from DataAnalyzer import DataAnalyzer

def backup_user_data(root_dir):
    # 定义源文件和目标目录
    source_file = os.path.join(root_dir, 'UserData', 'userData.json')
    backup_dir = os.path.join(root_dir, 'UserData', 'backup')

    # 确保备份目录存在
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

        # 获取当前日期
    current_date = datetime.now().strftime('%Y%m%d')

    # 查找现有的备份文件
    existing_backups = 0
    for f in os.listdir(backup_dir):
        if current_date in f:
            existing_backups+=1

    # 计算下一个编号
    next_number = existing_backups + 1
    next_number_str = f'{next_number:03d}'

    # 构造新的备份文件名
    new_backup_file = os.path.join(backup_dir, f'userData_{current_date}{next_number_str}.json')
    # 复制文件
    shutil.copy2(source_file, new_backup_file)

    # 删除超过20个备份的最早文件
    if len(os.listdir(backup_dir)) >= 20:
        earliest_backup_file = os.path.join(backup_dir, f'{current_date}001.json')
        if os.path.exists(earliest_backup_file):
            os.remove(earliest_backup_file)
            print(f'Deleted the earliest backup: {earliest_backup_file}')

    fileList = os.listdir(backup_dir)
    while(len(fileList) >=20):
        earliest_backup_file = fileList[0]
        earliest_backup_file = os.path.join(backup_dir, fileList[0])
        if os.path.exists(earliest_backup_file):
            os.remove(earliest_backup_file)
            print(f'Deleted the earliest backup: {earliest_backup_file}')
        fileList = os.listdir(backup_dir)

    print(f'Backup created: {new_backup_file}')

def readLocalFile():
    '''
    从本地读取存储的数据
    :return: configDict,userData,memoryData
    '''
    #获取当前工作目录
    currentWorkingDirectory = os.getcwd()
    #备份userData
    backup_user_data(currentWorkingDirectory)
    fileConfig = os.path.join(currentWorkingDirectory, "UserData/config.json")
    configDict = readDictFromJson(fileConfig)
    fileUserData = os.path.join(currentWorkingDirectory, "UserData/userData.json")
    userData = readDictFromJson(fileUserData)
    fileMemoryData = os.path.join(currentWorkingDirectory, "UserData/memory.json")
    memoryData = readDictFromJson(fileMemoryData)
    return configDict,userData,memoryData

def init():
    '''
    初始化所需要的类实例
    :return:传递参数, [configDict,userData,memoryData,dataAnalyzer]
    '''
    #加载本地数据
    configDict,userData,memoryData = readLocalFile()
    dataAnalyzer = DataAnalyzer(userData,configDict)
    return [configDict,userData,memoryData,dataAnalyzer]

if __name__ == '__main__':
    argList = init()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(argList)
    window.show_window()
    sys.exit(app.exec_())
