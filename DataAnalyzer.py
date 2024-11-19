import copy
class DataAnalyzer:
    '''
    分析处理userData，得到分析数据
    '''

    def __init__(self, userData: dict, config: dict):
        self.reloadData(userData)
        self.config = config

    def reloadData(self, userData: dict):
        self.__userData = userData

    def getIncomeAndOutcomeByday(self, path):
        '''
        获取每天的收/支总和，包括收入总和，支出总和和结余总和
        :param path: [accountName, year, month]
        :return: IOdict=
                        {
                            "date1":
                            {
                                "income":[,,,]
                                "outcome:[,,,]
                                "summary":[,,,]
                            },
                            "date2":
                            {
                                "income":[,,,]
                                "outcome:[,,,]
                                "summary":[,,,]
                            }
                        }
                其中date已经按照升序排序
        '''
        IOdict = {}
        dataMonth = self.__userData[path[0]][path[1]][path[2]]
        for key, dataDay in dataMonth.items():
            date, IOtype, amount = self.__interpreteBasicInfo(dataDay)
            if date in IOdict:
                if (IOtype == 1):
                    IOdict[date]["income"] +=amount
                else:
                    IOdict[date]["outcome"] += amount
                IOdict[date]["summary"] +=IOtype*amount
            else:
                IOdict[date]={}
                if (IOtype == 1):
                    IOdict[date]["income"] = amount
                    IOdict[date]["outcome"] = 0
                else:
                    IOdict[date]["income"] = 0
                    IOdict[date]["outcome"] = amount
                IOdict[date]["summary"] = IOtype*amount
        IOdict = dict(sorted(IOdict.items(), key=lambda item: item[0]))
        return IOdict

    def __interpreteBasicInfo(self, dataDay: dict):
        date = dataDay[self.config["headers"][0]]
        IOtypes = list(self.config["options"].keys())
        if (dataDay[self.config["headers"][1]] == IOtypes[0]):
            IOtype = -1  # 支出
        else:
            IOtype = 1  # 收入
        amount = float(dataDay[self.config["headers"][4]])
        return date, IOtype, amount

    def getAmountByType(self, path):
        '''
        获取本月各个种类支出、收入的总和
        :param path: [accountName, year, month]
        :return:
        '''
        res_dict = copy.deepcopy(self.config["options"])
        for IOType,value0 in res_dict.items():
            for main_area, value1 in value0.items():
                tempdict={}
                for area in value1:
                    tempdict[area]=0
                res_dict[IOType][main_area] = tempdict.copy()
                res_dict[IOType][main_area]["sum"]=0
        dataMonth = self.__userData[path[0]][path[1]][path[2]]
        for key, dataDay in dataMonth.items():
            date, IOtype, amount = self.__interpreteBasicInfo(dataDay)
            main_area = dataDay["主要领域"]
            area = dataDay["具体项目"]
            IOtype_str = dataDay["收支类型"]
            res_dict[IOtype_str][main_area][area] +=amount
            res_dict[IOtype_str][main_area]["sum"] +=amount
        return res_dict

    def getSummary(self, path):
        IOdict = self.getIncomeAndOutcomeByday(path)
        sum_income = 0
        sum_outcome = 0
        sum = 0
        for key, value in IOdict.items():
            sum_income += value["income"]
            sum_outcome += value["outcome"]
            sum += value["summary"]
        return sum_income,sum_outcome,sum