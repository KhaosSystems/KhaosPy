from PySide2 import QtCore, QtWidgets, QtGui

class KSScene2D(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)

        self.setBackgroundBrush(QtGui.QColor(26, 26, 26))
        self.setSceneRect(2000, 2000)

class KSViewport2D(QtWidgets.QGraphicsView):
    _RubberBand: QtWidgets.QRubberBand = None

    def __init__(self, scene, parent) -> None:
        super().__init__(scene, parent)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._RubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def StartRubberBandSelect(self, position):
        self.origin = position
        self._RubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self._RubberBand.show()

    def ReleaseRubberBandSelect(self):
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self.rubberband.geometry())
        painterPath.addPolygon(rect)
        self.rubberband.hide()
        return painterPath

class KSNodeScene(KSScene2D):
    def __init__(self, parent):
        super().__init__(parent)

class KSNodeGraph(KSViewport2D):
    _Scene: KSNodeScene = None

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self._Scene = KSNodeScene(self)
        self.setScene(self._Scene)