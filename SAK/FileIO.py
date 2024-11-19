import os
import json
import shutil

def FNameSpilt(abs_file_name):
    '''
    :param abs_file_name: absolute path of the file
    :return: list->[path,name,suffix]
    '''
    path=os.path.split(abs_file_name)[0]
    fname=os.path.split(abs_file_name)[1]
    name=os.path.splitext(fname)[0]
    suffix=os.path.splitext(fname)[1]
    return [path,name,suffix]

def mkdir(path,rmtree=False):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        if rmtree:
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            pass
def readDictFromJson(path)->dict:
    if (os.path.exists(path)):
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    return config
def writeDictToJson(path,outputDict:dict):
    # 将字典写入JSON文件
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(outputDict, json_file, ensure_ascii=False, indent=4)