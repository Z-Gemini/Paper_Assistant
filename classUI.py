from mywindow0 import *
from classWidget import *
import processor
class My_mainUI(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.images = []
        self.labels = []
    def setupUi(self, MainWindow):
        Ui_MainWindow.setupUi(self,MainWindow)
        self.mainWindow = MainWindow
        self.blank()

        # setup treeView using MyTreeView class
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.treeView = MyTreeView(self.widget)
        self.treeView.setObjectName("treeView")
        self.gridLayout_4.addWidget(self.treeView, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widget, 0, 0, 2, 1)

        # functions
        self.menu.triggered.connect(self.blank)
        self.treeView.doubleClicked.connect(self.on_treeView_doubleClicked)
        self.treeView.clicked.connect(self.on_treeView_clicked)
        self.actionFolder_2.triggered.connect(self.on_select_dir)
        self.actionFile.triggered.connect(self.on_select_file)
        self.pushButton_generatePDF.clicked.connect(self.on_generatePDF)
        self.pushButton_refresh.clicked.connect(self.refresh_image)
    def blank(self):
        self.centralwidget.setVisible(False)
        self.widget.setVisible(False)
        self.scrollArea_text.setVisible(False)
        self.pushButton_generatePDF.setVisible(False)
    def treeView_visbile(self):
        self.centralwidget.setVisible(True)
        self.widget.setVisible(True)
        self.scrollArea_text.setVisible(False)
        self.pushButton_generatePDF.setVisible(True)
        self.pushButton_generatePDF.setEnabled(False)
        self.stackedWidget.setCurrentIndex(1)
    def resultView_visbile(self):
        self.centralwidget.setVisible(True)
        self.widget.setVisible(False)
        self.scrollArea_text.setVisible(True)
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_generatePDF.setVisible(True)
        self.pushButton_generatePDF.setEnabled(True)
    def treeView_resultView(self):
        self.centralwidget.setVisible(True)
        self.widget.setVisible(True)
        self.scrollArea_text.setVisible(True)
        self.pushButton_generatePDF.setVisible(True)
        self.pushButton_generatePDF.setEnabled(True)
        self.stackedWidget.setCurrentIndex(0)
    def set_abstract(self, abstract):
        self.plainTextEdit_abstract.setPlainText(abstract)
    def get_abstract(self):
        p = self.plainTextEdit_abstract.toPlainText()
        return p
    def set_title(self, title):
        self.lineEdit_title.setText(title)
    def get_title(self):
        p = self.lineEdit_title.text()
        return p
    def set_keywords(self, keywords):
        self.plainTextEdit_Keywords.setPlainText(keywords)
    def get_keywords(self):
        p = self.plainTextEdit_Keywords.toPlainText()
        return p
    def set_comments(self, comments):
        self.plainTextEdit_Comments.setPlainText(comments)
    def get_comments(self):
        p = self.plainTextEdit_Comments.toPlainText()
        return p
    def set_images(self,images):
        self.images = images
        self.img_idx = 0
        self.show_image()
    def get_images(self):
        self.images = []
        if not len(self.processor.inout.dir_images)==0:
            img_list = os.listdir(self.processor.inout.dir_images)
            try:
                img_list.sort(key=lambda x: float(x[:-4]))
            except ValueError:
                img_list.sort()
            for file in img_list:
                file_path = os.path.join(self.processor.inout.dir_images, file)
                self.images.append(file_path)
        return self.images
    def show_image(self):
        if not len(self.images) ==0:
            for i in range(len(self.images)):
                label = ImageLabel(self.scrollAreaWidgetContents_2)
                label.setStyleSheet("background-color: white;")
                pixmap = QtGui.QPixmap(self.images[i])
                aspect_ratio = pixmap.width() / pixmap.height()  # 计算图片的宽高比
                scaled_pixmap = pixmap.scaled(160, int(160 / aspect_ratio), QtCore.Qt.KeepAspectRatio)  # 缩放图片并保持长宽比
                label.setPixmap(scaled_pixmap)
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setObjectName(f"label_image_{i}")
                label.setFrameShape(QLabel.Box)
                label.setFrameShadow(QLabel.Raised)
                label.setContextMenuPolicy(Qt.CustomContextMenu)
                label.filename = self.images[i]
                self.labels.append(label)
                row, col = divmod(i, 5)  # 每行最多显示5张图片
                self.gridLayout_3.addWidget(label, row, col)
        else:
            label = ImageLabel(self.scrollAreaWidgetContents_2)
            label.setStyleSheet("background-color: white;")
            label.setText("Image Folder Is Empty")
    def refresh_image(self):
        self.get_images()
        # 遍历布局中的所有控件
        for i in reversed(range(self.gridLayout_3.count())):
            # 获取控件
            widgetToRemove = self.gridLayout_3.itemAt(i).widget()
            # 如果控件是标签，就删除它
            if isinstance(widgetToRemove, QtWidgets.QLabel):
                widgetToRemove.setParent(None)
                widgetToRemove.deleteLater()
        self.show_image()
    def on_select_dir(self):
        self.selected_dir = QtWidgets.QFileDialog.getExistingDirectory(self.mainWindow, "Select folder", "/",
                                                                       QtWidgets.QFileDialog.ShowDirsOnly)
        if self.selected_dir:
            # 设置文件系统模型
            self.dirModel = QtWidgets.QFileSystemModel()
            self.dirModel.setRootPath(self.selected_dir)
            self.dirModel.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
            self.treeView.setSelectionMode(QTreeView.ExtendedSelection)
            self.treeView.setModel(self.dirModel)
            self.treeView.setRootIndex(self.dirModel.index(self.selected_dir))

            self.treeView.hideColumn(1)
            self.treeView.hideColumn(2)
            self.treeView.hideColumn(3)
            self.treeView_visbile()
    def on_select_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self.mainWindow, "Select a PDF File", "./",
                                                         "All Files (*);;PDF Files (*.pdf)")

        if filename[0] != "":
            self.parserPDF(filename[0])
            self.resultView_visbile()
    def parserPDF(self,pdf):
        self.processor = processor.AllProcessor(pdf)
        self.processor.extract()
        self.processor.showOnWindow(self)
    def on_treeView_doubleClicked(self, Qmodelidx):
        self.clear_window()
        filePath = self.dirModel.filePath(Qmodelidx)
        file_type = filePath.split('.')[-1]
        self.images = []
        if os.path.isfile(filePath) and file_type in ['pdf']:
            self.parserPDF(filePath)
            self.treeView_resultView()
        else:
            self.treeView_visbile()
    def on_treeView_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
        self.pushButton_generatePDF.setVisible(False)
        index = self.treeView.currentIndex()
        filePath = self.dirModel.filePath(index)
        file_type = filePath.split('.')[-1]
        if os.path.isfile(filePath) and file_type in ['png','jpg']:
            pixmap = QtGui.QPixmap(filePath)
            aspect_ratio = pixmap.width() / pixmap.height()  # 计算图片的宽高比
            scaled_pixmap = pixmap.scaled(500, int(500/ aspect_ratio), QtCore.Qt.KeepAspectRatio)  # 缩放图片并保持长宽比
            self.info_label.setPixmap(scaled_pixmap)
            self.info_label.setAlignment(QtCore.Qt.AlignCenter)
    def clear_window(self):
        self.lineEdit_title.clear()
        self.plainTextEdit_Keywords.clear()
        self.plainTextEdit_abstract.clear()
        self.plainTextEdit_Comments.clear()

        # 遍历布局中的所有控件
        for i in reversed(range(self.gridLayout_3.count())):
            # 获取控件
            widgetToRemove = self.gridLayout_3.itemAt(i).widget()
            # 如果控件是标签，就删除它
            if isinstance(widgetToRemove, QtWidgets.QLabel):
                widgetToRemove.setParent(None)
                widgetToRemove.deleteLater()
    def on_generatePDF(self):
        self.processor.updateFromView(self)
        self.processor.drawToPdf()
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.processor.inout.dir_pdf))
