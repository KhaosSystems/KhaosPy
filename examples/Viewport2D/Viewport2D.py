from PySide2 import QtWidgets, QtCore, QtGui
import KhaosSystems
import sys
import typing

import importlib
importlib.reload(KhaosSystems)

class FujinNode(KhaosSystems.KSSceneEntity):
    _width: float = 200
    _height: float = 150

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        
    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._width, self._height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        super().paint(painter, option, widget)
        painter.fillRect(self.boundingRect(), QtGui.QColor(100, 100, 100, 255))

class FujinWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtCore.QObject):
        super().__init__(parent)
        
        # Create and configure the scene.
        self.scene = KSScene2D(self)
        self.scene.addItem(FujinNode())

        # Create and configure the viewport.
        self.viewport = KSViewport2D(self.scene, self)
        self.viewport.move(0, 0)
        self.viewport.setInteractive(True)

        # Create and configure layout.
        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.viewport)
        self.setLayout(layout)
        self.show()

class FujinWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Khaos Systems | Fujin")
        self.setGeometry(300, 50, 1280, 720)

        self.fujin = FujinWidget(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.fujin)
        self.setLayout(layout)
        self.show()

if (__name__ == "__main__"):
    app = QtWidgets.QApplication(sys.argv)
    fujinWindow = FujinWindow()
    fujinWindow.show()

app.exec_()
sys.exit(0)