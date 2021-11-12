from PySide2 import QtGui, QtCore, QtWidgets

class NodeGraph(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        self.currentState = 'DEFAULT'

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        scene = NodeScene(self)
        scene.setSceneRect(0, 0, 2000, 2000)
        self.setScene(scene)

    # region Mouse events
    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.NoModifier and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
            self.startRubberband(event.pos())
        elif (event.button() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.NoModifier and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is not None):
            self.currentState = 'DRAG_ITEM'
            self.setInteractive(True)
        else:
            self.currentState = 'DEFAULT'

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self.currentState == 'SELECTION'):
            self.updateRubberband(event.pos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.currentState == 'SELECTION':
            self.releaseRubberband()
        self.currentState = 'DEFAULT'

        super().mouseReleaseEvent(event)
    # endregion

    # region Rubberband
    def startRubberband(self, position):
        self.currentState = 'SELECTION'
        self.rubberBandStart = position
        self.origin = position
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        self.setInteractive(False)

    def updateRubberband(self, mousePosition):
        self.rubberband.setGeometry(QtCore.QRect(self.origin, mousePosition).normalized())

    def releaseRubberband(self):
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self.rubberband.geometry())
        painterPath.addPolygon(rect)
        self.rubberband.hide()
        self.setInteractive(True)
        self.scene().setSelectionArea(painterPath)
    # endregion

    # region Node related
    def createNode(self):
        nodeItem = KSNodeItem()
        self.scene().nodes['name'] = nodeItem
        self.scene().addItem(nodeItem)
        nodeItem.setPos(self.mapToScene(self.viewport().rect().center()))
        return nodeItem
    # endregion

class NodeScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.setBackgroundBrush(QtGui.QColor(26, 26, 26))
        self.nodes = dict()

class KSNodeItem(QtWidgets.QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setZValue(1)

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(QtGui.QColor(130, 130, 130, 255))

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(2)
        self._pen.setColor(QtGui.QColor(50, 50, 50, 255))

        self._penSel = QtGui.QPen()
        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(2)
        self._penSel.setColor(QtGui.QColor(250, 250, 250, 255))

        self._textPen = QtGui.QPen()
        self._textPen.setStyle(QtCore.Qt.SolidLine)
        self._textPen.setColor(QtGui.QColor(230, 230, 230, 255))

        self._nodeTextFont = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)

    @property
    def pen(self):
        if self.isSelected():
            return self._penSel
        else:
            return self._pen

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 200, 50)

    def paint(self, painter, option, widget):
        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(0, 0, 200, 50, 10, 10)

        # Node label.
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)
        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect('Node Name').width() + 14
        text_height = metrics.boundingRect('Node Name').height() + 14
        margin = (text_width - 200) * 0.5
        textRect = QtCore.QRect(-margin, -text_height, text_width, text_height)
        painter.drawText(textRect, QtCore.Qt.AlignCenter, 'Node Name')

    def remove(self):
        scene = self.scene()
        scene.removeItem(self)

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction("Delete", self.remove)
        menu.exec_(event.screenPos())

app = QtWidgets.QApplication()

nodeGraph = NodeGraph(None)
nodeGraph.show()
nodeGraph.createNode()

app.exec_()