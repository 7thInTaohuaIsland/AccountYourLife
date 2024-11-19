import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QStyledItemDelegate, QLineEdit, QVBoxLayout, \
    QWidget, QDialog
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import Qt, QModelIndex,QRegularExpression


class NumberDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(NumberDelegate, self).__init__(parent)
        self.regex = QRegularExpression("^[\\d]*(\\.\\d{0,3})?$")  # 匹配整数或最多3位小数的数字
        self.validator = QRegularExpressionValidator(self.regex, self)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(self.validator)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if isinstance(value, (int, float)):
            editor.setText(f"{value:.2f}")  # 初始化为两位小数  
        else:
            editor.setText("")

    def setModelData(self, editor, model, index):
        text = editor.text()
        if text:
            try:
                value = float(text)
                model.setData(index, f"{value:.2f}", Qt.EditRole)  # 确保保存为两位小数  
            except ValueError:
                # 处理非法输入，可以选择忽略或恢复旧值  
                pass  # 这里选择忽略非法输入  

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)  