import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, \
    QLineEdit, QDateEdit, QDialog
from PyQt5.QtCore import Qt


class MyTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        # 初始化树形结构
        self.setHeaderLabels(["节点名称"])

    def add_branch(self, parent, name):
        # 在父节点下添加子节点
        item = QTreeWidgetItem(parent, [name])
        return item


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree with Year Input")

        # 创建树形结构
        self.tree = MyTree()
        self.setCentralWidget(self.tree)

        # 添加根节点（示例）
        root = self.tree.addTopLevelItem(QTreeWidgetItem(self.tree, ["根节点"]))

        # 添加一个按钮来触发添加分支的操作
        self.addButton = QPushButton("添加调出窗口分支", self)
        self.addButton.clicked.connect(self.add_item)
        self.setCornerWidget(self.addButton)  # 将按钮放在窗口的角落（可选）

    def add_item(self):
        # 创建一个对话框来输入年份
        dialog = YearInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 用户点击了确定按钮，获取输入的年份
            year = dialog.year
            # 在树中添加一个名为“调出窗口”的分支，并显示年份（这里简单地将年份作为分支的说明或子项）
            branch_item = self.tree.add_branch(self.tree.topLevelItem(0), "调出窗口")  # 假设添加到根节点下
            # 你可以根据需要添加更多的子项或逻辑
            year_item = QTreeWidgetItem(branch_item, [f"年份: {year}"])


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())