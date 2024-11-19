import io
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLCDNumber, QSizePolicy, QGroupBox
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # 用于日期处理
from PyQt5.QtGui import QPixmap
import datetime


class AnalysisWidget(QWidget):
    def __init__(self):
        super(AnalysisWidget, self).__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        '''控件1 layout 数字统计信息区域'''
        layout1 = QVBoxLayout()
        # 使用 QLCDNumber 显示数字统计信息
        self.lcd_expenditure = QLCDNumber(self)
        self.lcd_income = QLCDNumber(self)
        self.lcd_balance = QLCDNumber(self)

        # 设置 QLCDNumber 的显示模式为十进制（默认）
        # 还可以设置为十六进制（QLCDNumber.Hex）或二进制（QLCDNumber.Bin）
        self.lcd_expenditure.setDigitCount(10)  # 设置显示的位数，根据需要调整
        self.lcd_income.setDigitCount(10)
        self.lcd_balance.setDigitCount(10)
        # 设置初始值
        self.lcd_expenditure.display(0.00)
        self.lcd_income.display(0.00)
        self.lcd_balance.display(0.00)
        self.lcd_expenditure.setMinimumSize(150, 150)
        self.lcd_income.setMinimumSize(150, 150)
        self.lcd_balance.setMinimumSize(150, 150)
        self.lcd_expenditure.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.lcd_income.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.lcd_balance.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        # 创建布局和组框
        layout_expenditure = QVBoxLayout()
        layout_expenditure.addWidget(self.lcd_expenditure)
        group_expenditure = QGroupBox("本月总支出（元）")
        # 使用QSizePolicy.Preferred允许组框根据其内容自动调整大小
        group_expenditure.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # 第二个参数Fixed是为了防止组框在垂直方向上无限扩展
        group_expenditure.setLayout(layout_expenditure)

        layout_income = QVBoxLayout()
        layout_income.addWidget(self.lcd_income)
        group_income = QGroupBox("本月总收入（元）")
        group_income.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        group_income.setLayout(layout_income)

        layout_balance = QVBoxLayout()
        layout_balance.addWidget(self.lcd_balance)
        group_balance = QGroupBox("本月结余（元）")
        group_balance.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        group_balance.setLayout(layout_balance)

        # 将组框添加到主布局中
        layout1.addWidget(group_expenditure)
        layout1.addWidget(group_income)
        layout1.addWidget(group_balance)

        '''控件2 QLabel 每日支出收入展示区域'''
        self.plot_label1 = QLabel()

        '''控件3 QLabel 消费类型展示区域'''
        self.plot_label2 = QLabel()
        self.plot_label3 = QLabel()
        self.plot_label4 = QLabel()
        self.plot_label5 = QLabel()
        self.plot_label2.setFixedHeight(400)
        self.plot_label3.setFixedHeight(400)
        self.plot_label4.setFixedHeight(400)
        self.plot_label5.setFixedHeight(400)
        # 设置标签的大小策略为扩展，以便它们可以填满可用空间
        for label in [self.plot_label1, self.plot_label2, self.plot_label3, self.plot_label4, self.plot_label5]:
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        '''整合控件'''
        main_layout.addLayout(layout1)
        main_layout.addWidget(self.plot_label1)
        layout2 = QVBoxLayout()
        layout2.addWidget(self.plot_label2)
        layout2.addWidget(self.plot_label3)
        layout3 = QVBoxLayout()
        layout3.addWidget(self.plot_label4)
        layout3.addWidget(self.plot_label5)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)

        # 设置窗口的主布局
        self.setLayout(main_layout)

    def update_text_edit(self, dataAnalyzer, path):
        sum_income, sum_outcome, sum_balance = dataAnalyzer.getSummary(path)
        formatted_outcome = f"{sum_outcome:.2f}"
        formatted_income = f"{sum_income:.2f}"
        formatted_balance = f"{sum_balance:.2f}"

        self.lcd_expenditure.display(formatted_outcome)
        self.lcd_income.display(formatted_income)
        self.lcd_balance.display(formatted_balance)

    def __showImageInQlable(self, fig, label):
        # 将图表保存到字节流中
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)  # 重置指针到字节流的开始

        # 将字节流转换为 QPixmap 并显示在 QLabel 中
        qimg = QPixmap()
        qimg.loadFromData(buf.read())
        label.setPixmap(qimg)
        label.setAlignment(Qt.AlignCenter)

    def update_histogram(self, dataAnalyzer, path):
        # 创建一个 Matplotlib 图表
        IOdict = dataAnalyzer.getIncomeAndOutcomeByday(path)
        if not IOdict:
            fig, axes = plt.subplots(3, 1)
            self.__showImageInQlable(fig, self.plot_label1)
            return
        date_list = []
        income_list = []
        outcome_list = []
        summary_list = []
        summary = 0
        for key, value in IOdict.items():
            date_list.append(key)
            income_list.append(value["income"])
            outcome_list.append(value["outcome"])
            summary += value["summary"]
            summary_list.append(round(summary, 2))

        date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_list]
        # 计算等间隔的时间点
        num_lines = 5
        interval_indices = np.linspace(0, len(date_objects) - 1, num_lines, dtype=int)

        fig, axes = plt.subplots(3, 1)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为SimHei
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
        fig.suptitle("每日收支")
        # 第一个子图
        axes[0].plot(date_objects, income_list, label='收入', color='skyblue')
        axes[0].legend()
        axes[0].xaxis.set_visible(False)  # 隐藏横坐标
        # 添加数据标签
        for i, (x, y) in enumerate(zip(date_objects, income_list)):
            if i in interval_indices:
                axes[0].text(x, y, f'{y}', ha='right', va='bottom')  # 在数据点右侧下方显示标签
        # 添加竖线
        for index in interval_indices:
            axes[0].axvline(x=date_objects[index], color='gray', linestyle='--')

        # 第二个子图
        axes[1].plot(date_objects, outcome_list, label='支出', color='gold')
        axes[1].legend()
        axes[1].xaxis.set_visible(False)  # 隐藏横坐标
        # 添加数据标签
        for i, (x, y) in enumerate(zip(date_objects, outcome_list)):
            if i in interval_indices:
                axes[1].text(x, y, f'{y}', ha='right', va='bottom')  # 在数据点右侧下方显示标签
        # 添加竖线
        for index in interval_indices:
            axes[1].axvline(x=date_objects[index], color='gray', linestyle='--')

        # 第三个子图
        axes[2].plot(date_objects, summary_list, label='结余', color='darkorange')
        # 旋转日期标签以避免重叠（Matplotlib 通常会自动处理日期的旋转）
        axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置日期格式
        axes[2].xaxis.set_major_locator(mdates.DayLocator())  # 设置日期定位器
        axes[2].legend()
        # 添加数据标签（注意：对于汇总图，你可能想要调整标签的位置以避免重叠）
        for i, (x, y) in enumerate(zip(date_objects, summary_list)):
            # 这里我们稍微调整标签的位置以避免与数据点重叠
            if i in interval_indices:
                axes[2].text(x, y + 5, f'{y}', ha='center', va='bottom')  # 在数据点上方显示标签，并稍微偏移
        # 添加竖线
        for index in interval_indices:
            axes[2].axvline(x=date_objects[index], color='gray', linestyle='--')

        fig.autofmt_xdate()  # 自动旋转日期标签并调整子图布局以避免重叠
        # 调整布局并显示图形
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 调整布局以避免标题或标签被裁剪
        self.__showImageInQlable(fig, self.plot_label1)

    def update_pie_chart(self, dataAnalyzer, path):
        res_dict = dataAnalyzer.getAmountByType(path)
        if not res_dict:
            return
        cmap = plt.get_cmap('tab10')
        # 设置Matplotlib以使用中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为SimHei
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
        title_list = ["支出分布", "收入分布", "详细支出分布", "详细收入分布"]
        label_list = [self.plot_label2, self.plot_label3, self.plot_label4, self.plot_label5]
        index_label = 0
        for IOtype, value0 in res_dict.items():
            labels = []
            sizes = []
            colors = []
            explode = []
            color_index = 0
            fig, ax = plt.subplots()
            for main_area, value1 in value0.items():
                sum_main_area = value1["sum"]
                if sum_main_area != 0:
                    labels.append(main_area)
                    sizes.append(sum_main_area)
                    color = cmap(color_index)
                    color_index += 1
                    colors.append(color)
                    explode.append(0)
            # 绘制饼图
            fig.clear()  # 清除旧的图形
            plt.title(title_list[index_label], pad=2)
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=False, startangle=140)
            self.__showImageInQlable(fig, label_list[index_label])
            index_label += 1
        for IOtype, value0 in res_dict.items():
            labels = []
            sizes = []
            colors = []
            explode = []
            color_index = 0
            fig, ax = plt.subplots()
            for main_area, value1 in value0.items():
                for area, value2 in value1.items():
                    if area == "sum":
                        continue
                    amount_area = value2
                    if amount_area != 0:
                        labels.append(area)
                        sizes.append(amount_area)
                        color = cmap(color_index)
                        color_index += 1
                        colors.append(color)
                        explode.append(0)
            # 绘制饼图
            fig.clear()  # 清除旧的图形
            plt.title(title_list[index_label], pad=2)
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=False, startangle=140)
            self.__showImageInQlable(fig, label_list[index_label])
            index_label += 1

    def data_update(self, dataAnalyzer, path):
        for label in [self.plot_label1, self.plot_label2, self.plot_label3]:
            label.clear()
        self.update_histogram(dataAnalyzer, path)
        self.update_pie_chart(dataAnalyzer, path)
        self.update_text_edit(dataAnalyzer, path)
