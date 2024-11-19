import sys
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QWidget, QMenu, QAction
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QDateEdit, QApplication
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QDialog, QHBoxLayout, \
    QLineEdit, QPushButton, QLabel
from PyQt5.Qt import QHeaderView, QComboBox
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtCore import Qt, QDate, QPoint, QModelIndex, pyqtSlot, pyqtSignal
from SAK.GeneralTools import TimeTools,detect_type
from UI.delegate import NumberDelegate
from datetime import datetime
import copy

class EditItemDialog(QDialog):
    def __init__(self, parent=None, name=""):
        super().__init__(parent)
        self.setWindowTitle('编辑账本名称')

        # 布局
        layout = QVBoxLayout(self)

        # 标签和QLineEdit
        self.label = QLabel('账本名称:', self)
        layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(name)
        layout.addWidget(self.line_edit)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton('确认', self)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton('取消', self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 初始化对话框大小
        self.resize(300, 100)


class TableWidgetClass(QWidget):
    def __init__(self,parent):
        super(TableWidgetClass, self).__init__(parent)
        self.configDict = self.parent().configDict
        self.userData = self.parent().userData
        self.memoryData = self.parent().memoryData
        self.combo_boxes = {}
        self.date_edits = {}
        self.initUI()
        self.__itemChanged = False
        self.sortRevers = False

    def initUI(self):
        self.tableWidget = QTableWidget(0, 6, self)  # 4 rows, 3 columns
        self.tableWidget.setHorizontalHeaderLabels(self.configDict["headers"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate the table with some data
        # 将userData中的符合memoryData的项加载到tabelWidget中，否则加载第一组数据
        try:
            # path = self.memoryData["lastPath"]
            path = self.memoryData["lastPath"]
            if (len(path) == 3):
                useDefaultPath = False
            else:
                useDefaultPath = True
        except:
            useDefaultPath = True
        for accountName, accountBook in self.userData.items():
            for year, dataDictYear in accountBook.items():
                for month, dataDictMonth in dataDictYear.items():
                    if useDefaultPath:
                        path = [accountName, year, month]
                        self.loadTable([accountName, year, month])
                        break
                    else:
                        if accountName == path[0] and year == path[1] and month == path[2]:
                            self.loadTable([accountName, year, month])
                            break

        self.tableWidget.resizeColumnsToContents()
        # #给tabelWidget分配一个layout
        # self.layout = QVBoxLayout()
        # self.layout.addWidget(self.tableWidget)
        # self.setLayout(self.layout)

        # 连接信号与槽，当单元格内容改变时触发
        self.tableWidget.itemChanged.connect(self.on_item_changed)
        # 设置自定义委托给特定的列（例如，第一列）
        delegate = NumberDelegate(self)
        self.tableWidget.setItemDelegateForColumn(4, delegate)
        # 设置表头点击事件
        header = self.tableWidget.horizontalHeader()
        header.sectionClicked.connect(self.sort_table_by_header)

    def loadTable(self, path):
        self.curPath = path
        [accountName, year, month] = path
        accountDictMonth = self.userData[accountName][year][month]
        #对accountDictMonth按日期升序排序
        accountDictMonth = {k: accountDictMonth[k] for k in sorted(accountDictMonth.keys())}
        key_name = self.configDict["headers"][0]
        items = list(accountDictMonth.items())
        accountDictMonth = dict(sorted(items, key=lambda item:item[1][key_name]))
        self.__loadSepecificTable(accountDictMonth, path)

    def __loadSepecificTable(self,accountDictMonth, path):
        #清空tableWidget及对应的变量
        while (self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
        self.combo_boxes = {}
        self.date_edits = {}
        currentRow = 0
        for key, accountDictDay in accountDictMonth.items():
            addRowFlag = 1
            self.__addRow(currentRow, addRowFlag, accountDictDay, path)
            currentRow += 1
        self.__itemChanged = False
    @pyqtSlot(int)
    def sort_table_by_header(self, logicalIndex):
        key_name = self.configDict["headers"][logicalIndex]
        items = list(self.userData[self.curPath[0]][self.curPath[1]][self.curPath[2]].items())
        if (logicalIndex!=4):
            self.userData[self.curPath[0]][self.curPath[1]][self.curPath[2]] = dict(
                sorted(items, key=lambda item:item[1][key_name],reverse=self.sortRevers))
        else:
            self.userData[self.curPath[0]][self.curPath[1]][self.curPath[2]] = dict(
                sorted(items, key=lambda item: (float)(item[1][key_name]),reverse=self.sortRevers))
        accountDictMonth = self.userData[self.curPath[0]][self.curPath[1]][self.curPath[2]]
        self.__loadSepecificTable(accountDictMonth, self.curPath)
        self.sortRevers = not self.sortRevers

    def __addRow(self, rowPosition, flagAddRow, accountDict: dict, path):
        '''
        将accountDict中的信息添加到tableWidget中
        :param rowPosition:
        :param flagAddRow: 1-add; other-replace
        :param accountDict:
        :param path:
        :return:
        '''
        configDict = self.configDict
        if (flagAddRow == 1):
            self.tableWidget.insertRow(rowPosition)
        # 设置日期
        try:
            dateStr = accountDict[configDict["headers"][0]]
            if not TimeTools().is_valid_date(dateStr):
                dateStr = TimeTools().getDate()
        except:
            dateStr = TimeTools().getDate()
        dateStr = TimeTools().replace_date_if_not_match(dateStr, path[1], path[2])
        dateEdit = QDateEdit(QDate.currentDate(), self)
        dateEdit.setCalendarPopup(True)
        # 定义日期格式字符串，与你的日期字符串格式相匹配
        date_format = "yyyy-MM-dd"
        # 使用 QDate.fromString 方法将字符串转换为 QDate 对象
        date_object = QDate.fromString(dateStr, date_format)
        dateEdit.setDate(date_object)
        # 连接dateChanged信号到槽函数
        dateEdit.dateChanged.connect(self.on_date_changed)
        self.date_edits[(rowPosition, 0)] = dateEdit
        self.tableWidget.setCellWidget(rowPosition, 0, dateEdit)

        # 设置收支类型
        box1 = QComboBox()
        for ioType, mainAreas in configDict["options"].items():
            box1.addItem(ioType)
        try:
            tempStr1 = accountDict[configDict["headers"][1]]
            if tempStr1 not in configDict["options"]:
                tempStr1 = next(iter(configDict["options"]))
        except:
            tempStr1 = next(iter(configDict["options"]))
        box1.setCurrentText(tempStr1)
        self.tableWidget.setCellWidget(rowPosition, 1, box1)
        # 将QComboBox存储到字典中，以便稍后访问
        self.combo_boxes[(rowPosition, 1)] = box1
        # 连接每个QComboBox的currentIndexChanged信号到槽函数
        box1.currentIndexChanged.connect(self.on_combo_box_changed)

        # 设置主要领域
        box2 = QComboBox()
        for mainArea, Areas in configDict["options"][tempStr1].items():
            box2.addItem(mainArea)
        try:
            tempStr2 = accountDict[configDict["headers"][2]]
            if tempStr2 not in configDict["options"][tempStr1]:
                tempStr2 = next(iter(configDict["options"][tempStr1]))
        except:
            tempStr2 = next(iter(configDict["options"][tempStr1]))
        box2.setCurrentText(tempStr2)
        self.tableWidget.setCellWidget(rowPosition, 2, box2)
        # 将QComboBox存储到字典中，以便稍后访问
        self.combo_boxes[(rowPosition, 2)] = box2
        # 连接每个QComboBox的currentIndexChanged信号到槽函数
        box2.currentIndexChanged.connect(self.on_combo_box_changed)

        # 设置具体项目
        box3 = QComboBox()
        for Area in configDict["options"][tempStr1][tempStr2]:
            box3.addItem(Area)
        try:
            tempStr3 = accountDict[configDict["headers"][3]]
            if tempStr3 not in configDict["options"][tempStr1][tempStr2]:
                tempStr3 = configDict["options"][tempStr1][tempStr2][0]
        except:
            tempStr3 = configDict["options"][tempStr1][tempStr2][0]
        box3.setCurrentText(tempStr3)
        self.tableWidget.setCellWidget(rowPosition, 3, box3)
        # 将QComboBox存储到字典中，以便稍后访问
        self.combo_boxes[(rowPosition, 3)] = box3
        # 连接每个QComboBox的currentIndexChanged信号到槽函数
        box3.currentIndexChanged.connect(self.on_combo_box_changed)

        try:
            tempStr4 = accountDict[configDict["headers"][4]]
        except:
            tempStr4 = "0.00"
        item = QTableWidgetItem(tempStr4)
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(rowPosition, 4, item)

        try:
            tempStr5 = accountDict[configDict["headers"][5]]
        except:
            tempStr5 = ""
        item = QTableWidgetItem(tempStr5)
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(rowPosition, 5, item)
        self.__itemChanged = True

    def insertNewEmptyRow(self, rowPosition):
        accountDict = {"备注": "新建行"}
        flagAddRow = 1
        self.__addRow(rowPosition, flagAddRow, accountDict, self.curPath)
        self.__itemChanged = True

    def on_combo_box_changed(self, index):
        # 获取触发信号的QComboBox
        sender = self.sender()
        # 查找QComboBox在字典中的键（行号和列号）
        for key, combo in self.combo_boxes.items():
            if combo == sender:
                row, col = key
                selected_text = combo.currentText()
                if col == 1:
                    combo1 = self.combo_boxes[(row, 2)]  # mainArea
                    # 暂时断开信号与槽的连接
                    try:
                        combo1.currentIndexChanged.disconnect(self.on_combo_box_changed)
                    except TypeError:
                        # 如果信号已经断开或者未连接，忽略错误
                        pass
                    combo1.clear()
                    for mainArea, Areas in self.configDict["options"][selected_text].items():
                        combo1.addItem(mainArea)
                    # 重新连接信号与槽
                    combo1.currentIndexChanged.connect(self.on_combo_box_changed)
                    tempStr1 = next(iter(self.configDict["options"][selected_text]))

                    combo2 = self.combo_boxes[(row, 3)]  # Area
                    # 暂时断开信号与槽的连接
                    try:
                        combo2.currentIndexChanged.disconnect(self.on_combo_box_changed)
                    except TypeError:
                        # 如果信号已经断开或者未连接，忽略错误
                        pass
                    combo2.clear()
                    for Area in self.configDict["options"][selected_text][tempStr1]:
                        combo2.addItem(Area)
                    # 重新连接信号与槽
                    combo2.currentIndexChanged.connect(self.on_combo_box_changed)
                elif col == 2:
                    combo1 = self.combo_boxes[(row, 1)]
                    tempStr1 = combo1.currentText()
                    combo2 = self.combo_boxes[(row, 3)]
                    # 暂时断开信号与槽的连接
                    try:
                        combo2.currentIndexChanged.disconnect(self.on_combo_box_changed)
                    except TypeError:
                        # 如果信号已经断开或者未连接，忽略错误
                        pass
                    combo2.clear()
                    for Area in self.configDict["options"][tempStr1][selected_text]:
                        combo2.addItem(Area)
                    # 重新连接信号与槽
                    combo2.currentIndexChanged.connect(self.on_combo_box_changed)
                break
        self.__itemChanged = True

    @pyqtSlot(QDate)
    def on_date_changed(self, date):
        # 获取发出信号的QDateEdit控件
        sender = self.sender()
        # 找到对应的固定日期
        for key, dateEdit in self.date_edits.items():
            if dateEdit == sender:
                dateStr = date.toString("yyyy-MM-dd")
                newDateStr = TimeTools().replace_date_if_not_match(dateStr, self.curPath[1], self.curPath[2])
                # 尝试将新字符串转换回 QDate 对象
                # 如果转换失败，可以显示一个错误消息或者采取其他措施
                newDate = QDate.fromString(newDateStr, "yyyy-MM-dd")
                dateEdit.setDate(newDate)
                break
        self.__itemChanged = True

    def on_item_changed(self, item):
        self.__itemChanged = True

    def isAnyItemChanged(self):
        return self.__itemChanged

    def setItemChangedFlag(self, input: bool):
        self.__itemChanged = input


class TreeWidgetClass(QWidget):
    deleteItemSignal = pyqtSignal()
    addItemSignal = pyqtSignal()

    def __init__(self,parent):
        super(TreeWidgetClass, self).__init__(parent)
        self.configDict = self.parent().configDict
        self.userData = self.parent().userData
        self.memoryData = self.parent().memoryData
        self.initUI()

    def initUI(self):
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabel('账本')
        self.loadTree(self.userData)
        try:
            path = self.memoryData["lastPath"]
        except:
            path = None
        self.set_current_item_by_path(path)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置上下文菜单策略
        self.treeWidget.customContextMenuRequested.connect(self.on_context_menu)
        try:
            self.treeNameBefore = self.treeWidget.currentItem().text(0)
        except:
            self.treeNameBefore = ""

    def flush(self, userDataDict: dict):
        self.loadTree(userDataDict)

    def loadTree(self, userDataDict: dict):
        self.treeWidget.clear()
        for accountBookName, accountBook in userDataDict.items():
            root = QTreeWidgetItem(self.treeWidget, [accountBookName])
            for year, accountBookYear in accountBook.items():
                child = QTreeWidgetItem(root, [year])
                for month, accountBookMonth in accountBookYear.items():
                    child1 = QTreeWidgetItem(child, [month])

    def getCurrentItem(self):
        return self.treeWidget.currentItem()

    def on_context_menu(self, point):
        path = []
        treeItem = self.treeWidget.currentItem()
        while treeItem:
            path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
            treeItem = treeItem.parent()
        if len(path) == 1:
            # 获取点击位置的树项（注意：point 已经是相对于 viewport 的坐标）
            # 在某些情况下，您可能需要使用 self.tree.viewport().mapFromGlobal(point) 来转换坐标
            # 但对于 customContextMenuRequested 来说，这通常不是必需的
            item = self.treeWidget.itemAt(point)
            if not item:
                return

            # 创建上下文菜单
            menu = QMenu()
            action_edit = QAction('Edit', self)
            action_delete = QAction('Delete', self)
            action_add = QAction('Add', self)

            # 连接动作到槽函数（这里需要定义这些槽函数）
            action_edit.triggered.connect(lambda: self.edit_item(item))
            action_delete.triggered.connect(lambda: self.delete_item(item))
            action_add.triggered.connect(lambda: self.add_item(item))

            # 添加动作到菜单
            menu.addAction(action_edit)
            menu.addAction(action_delete)
            menu.addAction(action_add)

            # 显示菜单（直接使用 point，因为它是相对于 viewport 的坐标）
            menu.exec_(self.treeWidget.viewport().mapToGlobal(point))  # 通常不需要 mapToGlobal，因为 point 已经是合适的坐标
            # 或者更简单地（因为 customContextMenuRequested 提供的 point 通常是屏幕坐标）：
            # menu.exec_(point)
        elif len(path) == 2:
            item = self.treeWidget.itemAt(point)
            if not item:
                return
            menu = QMenu()
            action_delete = QAction('Delete', self)
            action_add = QAction('Add', self)
            # 连接动作到槽函数（这里需要定义这些槽函数）
            action_delete.triggered.connect(lambda: self.delete_item(item))
            action_add.triggered.connect(lambda: self.add_item(item))
            # 添加动作到菜单
            menu.addAction(action_delete)
            menu.addAction(action_add)
            menu.exec_(self.treeWidget.viewport().mapToGlobal(point))  # 通常不需要 mapToGlobal，因为 point 已经是合适的坐标


    def edit_item(self, item):
        # 实现编辑逻辑（例如，启动编辑模式）
        # 创建并显示编辑对话框
        path = []
        treeItem = self.treeWidget.currentItem()
        while treeItem:
            path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
            treeItem = treeItem.parent()
        self.treeNameBefore = [path[0]]
        dialog = EditItemDialog(self, path[0])
        if dialog.exec_() == QDialog.Accepted:
            # 用户点击了确认按钮
            new_name = dialog.line_edit.text()
            # 更新树项的名称（这里只是示例，实际可能需要更新数据模型）
            item.setText(0, new_name)
            # 如果需要，也可以更新item的name属性
            # item.name = new_name  # 这取决于您如何管理这些属性

    def delete_item(self, item):
        # 实现删除逻辑
        parent = item.parent()
        if parent:
            # 处理顶级项的删除（通常不会删除根节点，但这里为了示例可以删除）
            if (parent.childCount() <= 1):
                QMessageBox.warning(self, '警告', '年份应该至少有一个')
            else:
                self.treeNameBefore = [parent.text(0), item.text(0)]
                parent.removeChild(item)
                self.deleteItemSignal.emit()
        else:
            # 处理顶级项的删除（通常不会删除根节点，但这里为了示例可以删除）
            if (self.treeWidget.topLevelItemCount() <= 1):
                QMessageBox.warning(self, '警告', '账本数目应该至少有一个')
            else:
                self.treeNameBefore = [item.text(0)]
                self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
                self.deleteItemSignal.emit()


    def add_item(self, item):
        path = []
        treeItem = self.treeWidget.currentItem()
        while treeItem:
            path.insert(0, treeItem.text(0))  # 在路径列表的开头插入当前项的文本
            treeItem = treeItem.parent()
        if len(path)==1:
            newAccountName = self.configDict["newAccountName"]
            cnt=0
            while self.ifItemAlreadyExists(newAccountName):
                cnt += 1
                newAccountName = self.configDict["newAccountName"] + "{0}".format(cnt)
            new_root = QTreeWidgetItem(self.treeWidget, [newAccountName])
            for month in self.configDict["Months"]:
                QTreeWidgetItem(new_root,[month])
            self.newItemPath = [newAccountName, TimeTools().getYear()]
            self.addItemSignal.emit()
        elif len(path)==2:
            dialog = YearInputDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # 用户点击了确定按钮，获取输入的年份
                year = dialog.year
                branch_item = self.treeWidget.currentItem().parent()
                if self.ifItemAlreadyExists(f"{year}年",branch_item):
                    QMessageBox.warning(self, '警告', '该年份在账本中已存在')
                else:
                    # 你可以根据需要添加更多的子项或逻辑
                    year_item = QTreeWidgetItem(branch_item, [f"{year}年"])
                    for month in self.configDict["Months"]:
                        QTreeWidgetItem(year_item, [month])
                    self.newItemPath = [path[0], year_item.text(0),1]
                    self.addItemSignal.emit()

    def ifItemAlreadyExists(self, rootName, parent=None):
        # 如果未指定父项，则从顶级项开始搜索
        if parent is None:
            parent = self.treeWidget.invisibleRootItem()

            # 遍历当前父项下的所有子项
        for index in range(parent.childCount()):
            child_item = parent.child(index)
            # 检查当前子项的文本是否与指定的名称匹配
            if child_item.text(0) == rootName:
                return True
                # 递归检查子项的子项
            if self.ifItemAlreadyExists(rootName, child_item):
                return True

                # 如果没有找到匹配的项，则返回False
        return False

    def set_current_item_by_path(self,path = None):
        """
        根据路径设置 QTreeWidget 的当前项。

        :param tree_widget: QTreeWidget 实例
        :param path: 路径列表，每个元素是树中的一个项文本，从顶层项开始
        :return: 若找到路径，则返回最终设置的项；若未找到，则返回 None
        """
        if (path):
            useDefaultPath = False
        else:
            useDefaultPath = True
            return None
        current_item = None
        # 从顶层项开始遍历
        for top_level_index in range(self.treeWidget.topLevelItemCount()):
            top_level_item = self.treeWidget.topLevelItem(top_level_index)
            if useDefaultPath:
                current_item = top_level_item
                break
            else:
                if top_level_item.text(0) == path[0]:  # 假设项文本在第一列
                    current_item = top_level_item
                    break
        # 如果找到了顶层项，继续遍历子项
        if current_item:
            for item_text in path[1:]:  # 跳过顶层项文本，继续处理剩余路径
                found = False
                for child_index in range(current_item.childCount()):
                    child_item = current_item.child(child_index)
                    if useDefaultPath:
                        current_item = child_item
                        found = True
                        break
                    else:
                        if child_item.text(0) == item_text:  # 假设项文本在第一列
                            current_item = child_item
                            found = True
                            break
                if not found:
                    # 如果没有找到匹配的子项，则路径无效
                    print(f"Path not found: {path}")
                    return None
        else:
            # 如果没有找到匹配的顶层项，则路径无效
            print(f"Top-level item not found: {path[0]}")
            return None
        # 设置当前项
        self.treeWidget.setCurrentItem(current_item)
        return current_item

class YearInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入年份")

        # 布局和控件
        layout = QVBoxLayout(self)

        # 使用 QDateEdit 来选择年份（可以设置为只选择年份）
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy")  # 只显示年份
        # 直接设置当前年份
        current_date = QDate.currentDate()  # 获取当前日期
        self.date_edit.setDate(QDate(current_date.year(), 1, 1))
        # 注意：虽然月日设置为1月1日，但因为显示格式只包括年份，所以用户看不到这些
        layout.addWidget(self.date_edit)
        # 确定和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 存储年份的属性
        self.year = None

    def accept(self):
        # 在用户点击确定按钮时获取年份
        date = self.date_edit.date()
        self.year = date.toString("yyyy")
        super().accept()
