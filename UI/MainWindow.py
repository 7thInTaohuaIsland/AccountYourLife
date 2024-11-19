# main_window.py
import os.path
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QTableWidget, QVBoxLayout, QWidget, \
    QTableWidgetItem, QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QListView, QHBoxLayout, QPushButton, \
    QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.Qt import QComboBox, QDateEdit

from SAK.FileIO import writeDictToJson

from UI.MyWidgets import TableWidgetClass, TreeWidgetClass
from UI.AnalysisWidget import AnalysisWidget


class MainWindow(QMainWindow):
    def __init__(self, argList):
        '''
        :param argList: [configDict(0),userData(1),memoryData(2),dataAnalyzer(3)]
        '''
        super().__init__()
        self.configDict = argList[0]
        self.userData = argList[1]
        self.memoryData = argList[2]
        self.dataAnalyzer = argList[3]
        self.initUI()

    def initUI(self):
        '''加载设置项和用户数据'''
        version_major = self.configDict["version"][0]
        version_minor = self.configDict["version"][1]
        version_revision = self.configDict["version"][2]
        self.setWindowTitle(
            self.configDict["windowName"] + " (version: {0}.{1:02d})".format(version_major, version_minor))
        if not self.userData:
            self.userData = {"新账本": {}}
        # 补全self.userData中不完整的月份
        for accountName, accountYears in self.userData.items():
            for year, accountMonths in accountYears.items():
                for month in self.configDict["Months"]:
                    if month not in accountMonths:
                        self.userData[accountName][year][month] = {}
                self.userData[accountName][year] = dict(sorted(self.userData[accountName][year].items(), key=lambda item: self.sort_months(item[0]))) #一年的账本按月份排序
        '''初始化界面'''
        '''#子控件1(class) tabelWidgetClass'''
        self.tableWidgetClass = TableWidgetClass(self)

        '''#子控件2(class) treeWidgetClass'''
        self.treeWidgetClass = TreeWidgetClass(self)

        '''#子控件3(widget) 添加删除按钮'''
        widget_button = QWidget()
        # 创建按钮布局和按钮
        button_layout = QHBoxLayout()
        # 添加一个可伸缩的空间，将按钮推到布局的右侧
        button_layout.addStretch()
        add_button = QPushButton("增加")
        add_button.clicked.connect(self.add_row)  # 假设你有一个add_row方法来处理增加行的逻辑
        button_layout.addWidget(add_button)
        delete_button = QPushButton("删除")
        delete_button.clicked.connect(self.delete_row)  # 假设你有一个delete_row方法来处理删除行的逻辑
        button_layout.addWidget(delete_button)
        widget_button.setLayout(button_layout)

        '''#子控件4 AnalysisWidget(widget)'''
        self.widget_Analysis = AnalysisWidget()
        analysis_layout = QHBoxLayout()
        self.widget_Analysis.update_histogram(self.dataAnalyzer,self.tableWidgetClass.curPath)
        self.widget_Analysis.update_pie_chart(self.dataAnalyzer,self.tableWidgetClass.curPath)
        self.widget_Analysis.update_text_edit(self.dataAnalyzer,self.tableWidgetClass.curPath)
        self.widget_Analysis.setLayout(analysis_layout)

        '''设置布局'''
        #整合子控件1，子控件3，子控件4
        splitterRight = QSplitter(Qt.Vertical, self)
        splitterRight.addWidget(self.widget_Analysis)
        splitterRight.addWidget(self.tableWidgetClass.tableWidget)
        splitterRight.addWidget(widget_button)
        splitterRight.setStretchFactor(0, 1)  # First widget stretch factor
        splitterRight.setStretchFactor(1, 10)  # Second widget (tree) stretch factor

        #整合子控件1
        splitterLeft = QSplitter(Qt.Vertical, self)
        splitterLeft.addWidget(self.treeWidgetClass.treeWidget)
        # 创建 QSplitter 并设置为水平方向
        splitterCenter = QSplitter(Qt.Horizontal, self)
        splitterCenter.addWidget(splitterLeft)
        splitterCenter.addWidget(splitterRight)
        splitterCenter.setStretchFactor(0, 3)  # First widget stretch factor
        splitterCenter.setStretchFactor(1, 8)  # Second widget (tree) stretch factor
        # 设置 QSplitter 为中央 widget
        self.setCentralWidget(splitterCenter)



        # self.treeWidgetClass_previousItem = self.treeWidgetClass.getCurrentItem()
        # self.right_layout.addLayout(self.table_widget_layout)
        #
        #
        #
        # self.right_layout.addLayout(button_layout)
        # # 将子 widget 添加到 QSplitter 中
        # splitter.addWidget(self.treeWidgetClass)
        # splitter.addWidget(right_container)
        #
        # # Set initial stretch factors (relative sizes) for the splitter
        # # Here, we set the table widget to take up 2/3 of the space, and the tree widget to take up 1/3
        # splitter.setStretchFactor(0, 4)  # First widget (table) stretch factor
        # splitter.setStretchFactor(1, 7)  # Second widget (tree) stretch factor

        # 连接信号与槽，需要协调处理各个widget，所以需要在MainWindow实现
        self.treeWidgetClass.treeWidget.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        self.treeWidgetClass.treeWidget.itemChanged.connect(self.on_item_changed)

        # # 获取主屏幕的几何信息
        # screen_geometry = QGuiApplication.primaryScreen().geometry()
        # screen_width = screen_geometry.width()
        # screen_height = screen_geometry.height()
        #
        # # 计算窗口大小，设置为显示器尺寸的2/3
        # window_width = int(screen_width * 9 / 10)
        # window_height = int(screen_height * 9 / 10)
        # # 设置 MainWindow 的大小
        # self.resize(window_width, window_height)
        self.showMaximized()
    def sort_months(self, month):
        # 提取月份名中的数字，并转换为整数
        return int(month.strip("月"))

    def on_tree_item_double_clicked(self, item, column):
        # 获取当前被双击的分支项
        current_item = item
        # 获取当前分支的路径
        path = []
        while current_item:
            path.insert(0, current_item.text(0))  # 在路径列表的开头插入当前项的文本
            current_item = current_item.parent()
        if len(path) == 3:
            # 判断当前是否需要保存数据
            if self.tableWidgetClass.isAnyItemChanged():
                self.ask_to_save()
            # 根据新的数据创建新的表格控件
            self.tableWidgetClass.loadTable(path)
            self.treeWidgetClass_previousItem = item
            self.widget_Analysis.data_update(self.dataAnalyzer,path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            treeItem = self.treeWidgetClass.treeWidget.currentItem()
            self.__saveDataToUserData(treeItem)
            # 在这里添加保存数据的代码
        else:
            super().keyPressEvent(event)

    def add_row(self):
        number_of_rows = self.tableWidgetClass.tableWidget.rowCount()
        self.tableWidgetClass.insertNewEmptyRow(number_of_rows)

    def delete_row(self):
        number_of_rows = self.tableWidgetClass.tableWidget.rowCount()
        self.tableWidgetClass.tableWidget.removeRow(number_of_rows - 1)
        self.tableWidgetClass.setItemChangedFlag(True)

    def ask_to_save(self):
        # 创建一个QMessageBox对象
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("该月份数据已被修改，是否保存？")
        msg_box.setInformativeText("")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        # 设置QMessageBox的标题
        msg_box.setWindowTitle("提示")
        # 执行消息框并获取用户的选择
        ret = msg_box.exec_()
        # 根据用户的选择执行操作
        if ret == QMessageBox.Yes:
            treeItem = self.treeWidgetClass_previousItem
            self.__saveDataToUserData(treeItem)
        else:
            pass

    def __saveDataToUserData(self, treeItem):
        # 获取当前分支的路径
        path = []
        while treeItem:
            path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
            treeItem = treeItem.parent()
        self.userData[path[0]][path[1]][path[2]] = {}
        rows = self.tableWidgetClass.tableWidget.rowCount()
        cols = self.tableWidgetClass.tableWidget.columnCount()
        cnt = 0
        for row in range(rows):
            self.userData[path[0]][path[1]][path[2]][cnt] = {}
            for col in range(cols):
                widget = self.tableWidgetClass.tableWidget.cellWidget(row, col)
                if isinstance(widget, QComboBox):
                    self.userData[path[0]][path[1]][path[2]][cnt][
                        self.configDict["headers"][col]] = widget.currentText()
                elif isinstance(widget, QDateEdit):
                    date = widget.date()  # 获取 QDate 对象
                    date_string = date.toString("yyyy-MM-dd")  # 转换为指定格式的字符串
                    self.userData[path[0]][path[1]][path[2]][cnt][
                        self.configDict["headers"][col]] = date_string
                else:
                    item = self.tableWidgetClass.tableWidget.item(row, col)
                    if item:
                        self.userData[path[0]][path[1]][path[2]][cnt][
                            self.configDict["headers"][col]] = item.text()
                    else:
                        self.userData[path[0]][path[1]][path[2]][cnt][
                            self.configDict["headers"][col]] = ""
            cnt += 1
        self.tableWidgetClass.setItemChangedFlag(False)
        self.dataAnalyzer.reloadData(self.userData)
        self.widget_Analysis.data_update(self.dataAnalyzer,path)

    def closeEvent(self, event):
        # 这里是当窗口关闭时要执行的行为
        if self.tableWidgetClass.isAnyItemChanged():
            reply = QMessageBox.question(self, 'Message',
                                         "Would you like to save the data on the current page?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                treeItem = self.treeWidgetClass_previousItem
                self.__saveDataToUserData(treeItem)
            else:
                pass

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 执行真正的关闭操作，比如保存数据等
            # 这里可以添加额外的关闭前行为

            currentWorkingDirectory = os.getcwd()
            fileConfig = os.path.join(currentWorkingDirectory, "UserData/userData.json")
            writeDictToJson(fileConfig, self.userData)

            treeItem = self.treeWidgetClass.getCurrentItem()
            path = []
            while treeItem:
                path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
                treeItem = treeItem.parent()
            fileMemory = os.path.join(currentWorkingDirectory, "UserData/memory.json")
            self.memoryData["lastPath"] = path
            writeDictToJson(fileMemory, self.memoryData)
            event.accept()  # 允许窗口关闭
        else:
            event.ignore()  # 阻止窗口关闭

    def on_item_changed(self, item, column):
        # 当树项被编辑时更新字典
        key = item.text(0)  # 假设我们使用树项的文本作为键
        value = self.userData[self.treeWidgetClass.treeNameBefore[0]]
        # 添加新键值对
        self.userData[key] = value
        # 删除旧键值对
        del self.userData[self.treeWidgetClass.treeNameBefore[0]]

    def on_tree_item_deleted(self):
        if len(self.treeWidgetClass.treeNameBefore) == 1:
            del self.userData[self.treeWidgetClass.treeNameBefore[0]]
        else:
            del self.userData[self.treeWidgetClass.treeNameBefore[0]][self.treeWidgetClass.treeNameBefore[1]]
        path = []
        treeItem = self.treeWidgetClass.treeWidget.currentItem()
        while treeItem:
            path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
            treeItem = treeItem.parent()
        self.tableWidgetClass.loadTable(path=[path[0], path[1], "1月"])

    def on_tree_item_add(self):
        accountName = self.treeWidgetClass.newItemPath[0]
        year = self.treeWidgetClass.newItemPath[1]
        if len(self.treeWidgetClass.newItemPath) == 2:
            self.userData[accountName] = {}
            self.userData[accountName][year] = {}
        else:
            self.userData[accountName][year] = {}
        for Month in self.configDict["Months"]:
            self.userData[self.treeWidgetClass.newItemPath[0]][self.treeWidgetClass.newItemPath[1]][Month] = {}
        self.userData[accountName][year] = dict(
            sorted(self.userData[accountName][year].items(), key=lambda item: self.sort_months(item[0])))

    def show_window(self):
        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show_window()
    sys.exit(app.exec_())
