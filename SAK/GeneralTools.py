from datetime import datetime
import re

class TimeTools:
    def __init__(self):
        pass

    def getDate(self):
        # 获取当前日期和时间
        now = datetime.now()
        # 提取年份、月份和日期
        year = now.year
        month = now.month
        day = now.day
        # 将年份转换为两位数字格式（YY）
        year_yy = str(year)[:]
        # 格式化日期为 YY/MM/DD
        formatted_date = f"{year_yy}-{month:02d}-{day:02d}"
        return formatted_date

    def getYear(self):
        # 获取当前日期和时间
        now = datetime.now()
        # 提取年份、月份和日期
        year = now.year
        return year
    def is_valid_date(self, date_str):
        """
        判断输入的字符串是否符合YYYY-MM-DD的时间格式，并验证时间是否合法。

        :param date_str: 要判断的字符串
        :return: 如果字符串是有效的日期，则返回True；否则返回False
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def replace_date_if_not_match(self, date_str, year_str, month_str):
        # 解析日期字符
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # 如果日期格式不正确，抛出异常
            raise ValueError(f"Invalid date format: {date_str}")

            # 提取年份和月份
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # 将年份和月份字符串转换为整数和中文月份
        target_year = int(year_str.replace('年', ''))
        target_month_num = self.chinese_month_to_number(month_str.replace('月', ''))

        # 判断是否匹配
        if year != target_year or month != target_month_num:
            # 替换为指定的年份和月份的第一天
            target_date_str = f"{target_year:04d}-{target_month_num:02d}-{day:02d}"
            return target_date_str
        else:
            # 保持原日期格式（但这里其实不需要转换，因为已经是正确格式了）
            return date_str.replace("-", "-")  # 这里只是为了确保格式，实际上没改变

    def chinese_month_to_number(self, chinese_month):
        # 将中文月份转换为月份数字
        months = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        return int(months[int(chinese_month)])  # 注意这里int(chinese_month)是安全的，因为我们已经知道它是1到12的中文表示


def detect_type(value):
    # 尝试解析为日期
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')  # 示例日期格式：YYYY-MM-DD
    if date_pattern.match(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return 'date'
        except ValueError:
            pass

            # 尝试解析为数字
    if value.isdigit() or (value.replace('.', '', 1).isdigit() and '.' in value):  # 支持整数和小数
        return 'number'

        # 默认是字符串
    return 'string'