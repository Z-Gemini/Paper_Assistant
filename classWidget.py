
import os,shutil
from PyQt5.QtWidgets import QMenu,QAction,QTreeView,QLabel,QApplication,QFileDialog
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QThread,Qt,QUrl,QItemSelectionModel

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedSize(160, 160)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid white;")
        self.filename = ""
        self.selected = False
        self.createMenu()

    def mouseDoubleClickEvent(self, event):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.filename))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                self.selected = not self.selected
            elif modifiers == Qt.ShiftModifier:
                self.selected = True
            else:
                self.unselectAll()
                self.selected = True
            self.updateStyle()
        elif event.button() == Qt.RightButton:
            self.showMenu(event.globalPos())
        super().mousePressEvent(event)

    def unselectAll(self):
        for label in self.parent().findChildren(ImageLabel):
            label.selected = False
            label.updateStyle()

    def updateStyle(self):
        if self.selected:
            self.setStyleSheet("border: 2px solid blue;")
        else:
            self.setStyleSheet("border: 1px solid white;")

    def createMenu(self):
        self.menu = QMenu(self)
        deleteAction = QAction("Delete", self)
        deleteAction.triggered.connect(self.deleteSelected)
        self.menu.addAction(deleteAction)
        saveAction = QAction("Save Image as", self)
        saveAction.triggered.connect(self.saveSelected)
        self.menu.addAction(saveAction)

    def showMenu(self, pos):
        self.menu.popup(pos)

    def deleteSelected(self):
        for label in self.parent().findChildren(ImageLabel):
            if label.selected:
                filepath = label.filename
                if os.path.exists(filepath):
                    os.remove(filepath)
                    label.deleteLater()
                label.setParent(None)

    def saveSelected(self):
        for label in self.parent().findChildren(ImageLabel):
            if label.selected:
                filepath = label.filename
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Images (*.png *.jpg *.jpeg)", options=options)
                if fileName:
                    shutil.copyfile(filepath, fileName)

class MyTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                self.setSelectionMode(QTreeView.MultiSelection)
            elif modifiers == Qt.ShiftModifier:
                self.setSelectionMode(QTreeView.ContiguousSelection)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSelectionMode(QTreeView.ExtendedSelection)
        super().mouseReleaseEvent(event)

    def showContextMenu(self, pos):
        menu = QMenu()
        openAction = QAction("Open", self)
        openAction.triggered.connect(self.openSelected)	
        deleteAction = QAction("Delete", self)
        deleteAction.triggered.connect(self.deleteSelected)
        menu.addAction(openAction)
        menu.addAction(deleteAction)
        menu.exec_(self.mapToGlobal(pos))

    def deleteSelected(self):
        model = self.model()
        indexes = self.selectedIndexes()
        for index in indexes:
            model.remove(index)

    def openSelected(self):
        indexes = self.selectedIndexes()
        for index in indexes:
            path = self.model().filePath(index)
            if path:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            # 获取当前选中的模型索引
            currentIndex = self.currentIndex()
            # 如果当前选中的模型索引不为空，向上移动一行
            if currentIndex.isValid():
                self.selectionModel().setCurrentIndex(currentIndex.sibling(currentIndex.row() - 1, 0),
                                                      QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        elif event.key() == Qt.Key_Down:
            # 获取当前选中的模型索引
            currentIndex = self.currentIndex()
            # 如果当前选中的模型索引不为空，向下移动一行
            if currentIndex.isValid():
                self.selectionModel().setCurrentIndex(currentIndex.sibling(currentIndex.row() + 1, 0),
                                                      QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        elif event.key() == Qt.Key_Return:
            # 获取当前选中的模型索引
            currentIndex = self.currentIndex()
            # 如果当前选中的模型索引不为空，模拟鼠标左键点击事件
            if currentIndex.isValid():
                self.executeDelayed(self.clicked, (currentIndex,))
        elif event.key() == Qt.Key_Space:
            # 获取当前选中的模型索引
            currentIndex = self.currentIndex()
            # 如果当前选中的模型索引不为空，打开文件
            if currentIndex.isValid():
                # 获取文件路径
                filePath = self.model.filePath(currentIndex)
                # 使用QDesktopServices的openUrl()方法打开文件
                QDesktopServices.openUrl(QUrl.fromLocalFile(filePath))
        else:
            # 其他键盘事件交给父类处理
            super(MyTreeView, self).keyPressEvent(event)