from PySide2 import QtCore, QtWidgets, QtGui

STYLE_QMENU = '''
QMenu {
    color: rgba(255, 255, 255, 200);
    background-color: rgba(47, 47, 47, 255);
    border: 1px solid rgba(0, 0, 0, 30);
}
QMenu::item {
    padding: 5px 18px 2px;
    background-color: transparent;
}
QMenu::item:selected {
    color: rgba(98, 68, 10, 255);
    background-color: rgba(219, 158, 0, 255);
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 50);
    margin: 4px 8px;
}
'''

class KSNodeItem(QtWidgets.QGraphicsItem):
    _contextMenu: QtWidgets.QMenu = None
    _title: str = "Node Title"

    def __init__(self):
        super().__init__()
        self.setZValue(1)

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self._contextMenu = QtWidgets.QMenu()
        self._contextMenu.setMinimumWidth(200)
        self._contextMenu.setStyleSheet(STYLE_QMENU)
        self._contextMenu.addAction("Remove", self.remove)

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(QtGui.QColor(70, 70, 70, 255))

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(2)
        self._pen.setColor(QtGui.QColor(50, 50, 50, 255))

        self._penSel = QtGui.QPen()
        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(2)
        self._penSel.setColor(QtGui.QColor(219, 158, 0, 255))

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
        return QtCore.QRectF(0, 0, 200, 25)

    def paint(self, painter, option, widget):
        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)
        painter.drawRoundedRect(0, 0, 200, 25, 10, 10)

        # Node label.
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)
        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self._title).width() + 14
        text_height = metrics.boundingRect(self._title).height() + 14
        margin = (text_width - 200) * 0.5
        textRect = QtCore.QRect(-margin, -text_height, text_width, text_height)
        painter.drawText(textRect, QtCore.Qt.AlignCenter, self._title)

    def remove(self):
        scene = self.scene()
        scene.removeItem(self)

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        self._contextMenu.exec_(event.screenPos())

class KSNodeGraph(QtWidgets.QGraphicsView):
    _contextMenu: QtWidgets.QMenu = None

    def __init__(self, parent):
        super().__init__(parent)

        self.frameSelectedAction = QtWidgets.QAction("Frame Selected", self)
        self.frameSelectedAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F))
        self.frameSelectedAction.triggered.connect(self.frameSelected)
        self.addAction(self.frameSelectedAction)

        self._contextMenu = QtWidgets.QMenu()
        self._contextMenu.setMinimumWidth(200)
        self._contextMenu.setStyleSheet(STYLE_QMENU)
        self._contextMenu.addAction(self.frameSelectedAction)

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

        scene = KSNodeScene(self)
        scene.setSceneRect(0, 0, 2000, 2000)
        self.setScene(scene)

        self.show()

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
    def addNode(self, node: KSNodeItem):
        self.scene().nodes['name'] = node
        self.scene().addItem(node)
        node.setPos(self.mapToScene(self.viewport().rect().center()))
    # endregion

    def frameSelected(self):
        if len(self.scene().selectedItems()) > 0:
            selectionBounds = self.scene().selectionItemsBoundingRect()
        else:
            selectionBounds = self.scene().itemsBoundingRect()
        selectionBounds = selectionBounds.marginsAdded(QtCore.QMarginsF(64, 64+50, 64, 64))
        self.fitInView(selectionBounds, QtCore.Qt.KeepAspectRatio)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self._contextMenu.exec_(event.globalPos())

class KSNodeScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.setBackgroundBrush(QtGui.QColor(26, 26, 26))
        self.nodes = dict()

    def selectionItemsBoundingRect(self) -> QtCore.QRectF:
        # Does not take untransformable items into account.
        boundingRect = QtCore.QRectF()
        for item in self.selectedItems():
            boundingRect |= item.sceneBoundingRect()
        return boundingRect
