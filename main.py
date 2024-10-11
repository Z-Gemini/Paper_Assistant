from processor import *

class My_mainWindow(QtWidgets.QMainWindow):
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = My_mainWindow()
    uiMain = My_mainUI()
    uiMain.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
