from PySide2 import QtCore, QtWidgets, QtGui
from enum import Enum
import typing
import json
import uuid
import sys
import importlib

class KSColor(object):
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 0

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def toQColor(self) -> QtGui.QColor:
        return QtGui.QColor(self.r, self.g, self.b, self.a)

class KSStyleingData(object):
    COLOR_VIEWPORT_BACKGROUND: KSColor = KSColor(26, 26, 26)
    COLOR_NODE_TEXT: KSColor = KSColor(194, 194, 194)
    COLOR_NODE_BORDER: KSColor = KSColor(51, 51, 51)
    COLOR_NODE_BORDER_SELECTED: KSColor = KSColor(219, 158, 0)
    COLOR_NODE_BACKGROUND: KSColor = KSColor(59, 59, 59)
    COLOR_DATATYPE_VOID: KSColor = KSColor(255, 255, 255)
    COLOR_DATATYPE_STRING: KSColor = KSColor(0, 194, 255)
    COLOR_DATATYPE_MATRIX: KSColor = KSColor(255, 170, 0)

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

# TODO: Make a master class of this.
class KSGraphicsStringInput(QtWidgets.QGraphicsTextItem):
    def __init__(self, text: str, parent: typing.Optional[QtWidgets.QGraphicsItem] = ...) -> None:
        super().__init__(text, parent=parent)

        self.setTextInteractionFlags(QtCore.Qt.TextEditable)

    def setData(self, data: str) -> None:
        self.setPlainText(data)

    def data(self) -> str:
        return self.toPlainText()

class KSGraphicsBoolInput(QtWidgets.QGraphicsItem):
    _data: bool = False

    def __init__(self, parent: QtWidgets.QGraphicsItem) -> None:
        super().__init__(parent=parent)
    
    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 15, 15)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        if (self._data):
            painter.fillRect(self.boundingRect(), QtCore.Qt.green)
        else:
            painter.fillRect(self.boundingRect(), QtCore.Qt.red)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        self._data = not self._data
        self.update()

    def setData(self, data: bool) -> None:
        self._data = data

    def data(self) -> bool:
        return self._data

class KSNodeConnectionPath(QtWidgets.QGraphicsPathItem):
    originPoint: QtCore.QPointF = None
    targetPoint: QtCore.QPointF = None
    
    def __init__(self, originPoint: QtCore.QPointF, targetPoint: QtCore.QPointF) -> None:
        super().__init__()

        self.updatePath(originPoint, targetPoint)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        self.updatePath(self.originPoint, self.targetPoint)
        return super().paint(painter, option, widget=widget)

    def updatePath(self, originPoint: QtCore.QPointF, targetPoint: QtCore.QPointF) -> None:
        self.originPoint = originPoint
        self.targetPoint = targetPoint

        self._pen = QtGui.QPen(QtCore.Qt.red)
        self._pen.setWidth(4)
        self.setPen(self._pen)

        self.source_point = self.originPoint
        self.target_point = self.targetPoint

        path = QtGui.QPainterPath()
        path.moveTo(self.source_point)
        dx = (self.target_point.x() - self.source_point.x()) * 0.5
        dy = self.target_point.y() - self.source_point.y()
        ctrl1 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 0)
        ctrl2 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 1)
        path.cubicTo(ctrl1, ctrl2, self.target_point)

        self.setPath(path)
    
class KSNodeInput(QtWidgets.QGraphicsItem):
    _datatype: type = None
    _connection: "KSNodeOutput" = None
    _connectionPath: KSNodeConnectionPath = None
    _manualInput: KSGraphicsStringInput = None

    _uniqueIdentifier: str = None

    _brush: QtGui.QBrush = None
    _pen: QtGui.QPen = None

    _borderWidth: int = 2

    def __init__(self, parent: "KSNodeItem", datatype: type) -> None:
        super().__init__(parent=parent)
        self._datatype = datatype

        self._borderWidth = 2

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(KSStyleingData.COLOR_DATATYPE_STRING.toQColor())

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self._borderWidth)
        self._pen.setColor(KSStyleingData.COLOR_NODE_BORDER.toQColor())

        if (self._datatype == str):
            self._manualInput = KSGraphicsStringInput("L_Joint_jnt", self)
            self._manualInput.setPos(15, 0)
        elif(self._datatype == bool):
            self._manualInput = KSGraphicsBoolInput(self)
            self._manualInput.setPos(15, 0)

    def isUsingManualInput(self) -> bool:
        return self._connection == None

    def connect(self, output: "KSNodeOutput") -> None:
        if (self._connection != None):
            self.disconnect()

        self._connection = output
        self._connection.onConnect(self)
        self._manualInput.hide()

        targetPoint = output.scenePos() + output.boundingRect().center()
        originPoint = self.scenePos() + self.boundingRect().center()
        self._connectionPath = KSNodeConnectionPath(targetPoint, originPoint)
        self.scene().addItem(self._connectionPath)

    def disconnect(self) -> None:
        self._connection.onDisconnect(self)
        self._connection = None
        self.scene().removeItem(self._connectionPath)
        self._connectionPath = None

    def updatePath(self) -> None:
        if (self._connectionPath != None):
            targetPoint = self._connection.scenePos() + self._connection.boundingRect().center()
            originPoint = self.scenePos() + self.boundingRect().center()
            self._connectionPath.updatePath(targetPoint, originPoint)

    def data(self) -> typing.Any:
        if (self._connection != None):
            return self._connection.data()
        else:
            return self._manualInput.data()

    def serialize(self) -> object:
        connectionUUID = ""
        connectionOutputKey = ""
        if (self._connection != None):
            connectionUUID = self._connection.dataProvider().uniqueIdentifier()

            for key in self._connection.dataProvider()._outputs:
                if (self._connection.dataProvider()._outputs[key] == self._connection):
                    connectionOutputKey = key

        return {  
            'manualInputData': self._manualInput.data(),
            'connectionUUID': connectionUUID,
            'connectionOutputKey': connectionOutputKey
            }

    def deserialize(self, nodeGraph: "KSNodeGraph", data: object) -> None:
        self._manualInput.setData(data['manualInputData'])
        
        connection = None
        for item in nodeGraph.scene().items():
            if (isinstance(item, KSNodeItem) and item.uniqueIdentifier() == data['connectionUUID'] and data['connectionOutputKey'] in item._outputs):
                connection = item._outputs[data['connectionOutputKey']]

        if (connection != None):
            self.connect(connection)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 16, 22)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        # painter.fillRect(self.boundingRect(), QtGui.QColor(0, 0, 255, 255))
        
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(1, 4, 14, 14)

class KSNodeOutput(QtWidgets.QGraphicsItem):
    _dataProvider: "KSNodeItem" = None
    _datatype: type = None
    _dataCache: typing.Any = None
    _connections: typing.List[KSNodeInput] = []
    
    _brush: QtGui.QBrush = None
    _pen: QtGui.QPen = None

    _borderWidth: int = 2

    def __init__(self, parent: "KSNodeItem", datatype: type) -> None:
        super().__init__(parent=parent)
        self._dataProvider = parent
        self._datatype = datatype

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(QtGui.QColor(70, 70, 70, 255))

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self._borderWidth)
        self._pen.setColor(QtGui.QColor(50, 50, 50, 255))

    def setData(self, data: typing.Any) -> None:
        self._dataCache = data

    def onConnect(self, connection: KSNodeInput) -> None:
        self._connections.append(connection)

    def onDisconnect(self, connection) -> None:
        self._connections.remove(connection)

    def updatePaths(self) -> None:
        for connection in self._connections:
            connection.updatePath()

    def dataProvider(self) -> "KSNodeItem":
        return self._dataProvider

    def data(self) -> typing.Any:
        self._dataProvider.executeImplicit()
        return self._dataCache

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 16, 22)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        painter.fillRect(self.boundingRect(), QtCore.Qt.red)

        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(1, 4, 14, 14)

class KSNodeItem(QtWidgets.QGraphicsItem):
    _title: str = "Node Title"
    
    _inputDefinitions: typing.Dict[str, type] = {}
    _outputDefinitions: typing.Dict[str, type] = {}

    _inputs: typing.Dict[str, KSNodeInput] = {}
    _outputs: typing.Dict[str, KSNodeOutput] = {}

    _outputDefinitions: typing.Dict[str, type]

    _contextMenu: QtWidgets.QMenu = None

    _brush: QtGui.QBrush = None
    _pen: QtGui.QPen = None

    _borderWidth: float = None
    _bodyMarginTop: float = None
    _bodyMarginBottom: float = None
    _headerSize: QtCore.QRectF = None
    _bodySize: QtCore.QSizeF = None

    _uniqueIdentifier: str = None

    _tmpDisableAutoOutputs: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.setZValue(1)

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self._borderWidth = 2
        self._bodyMarginTop = 10
        self._bodyMarginBottom = 10
        self._headerSize = QtCore.QSizeF(200, 33)
        self._bodySize = QtCore.QSizeF(200, self._borderWidth + self._bodyMarginTop + self._bodyMarginBottom)

        self._contextMenu = QtWidgets.QMenu()
        self._contextMenu.setMinimumWidth(200)
        self._contextMenu.setStyleSheet(STYLE_QMENU)
        self._contextMenu.addAction("Remove", self.remove)
        self._contextMenu.addAction("Reload", self.reload)

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(KSStyleingData.COLOR_NODE_BACKGROUND.toQColor())

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self._borderWidth)
        self._pen.setColor(KSStyleingData.COLOR_NODE_BORDER.toQColor())

        self._penSel = QtGui.QPen()
        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(self._borderWidth)
        self._penSel.setColor(KSStyleingData.COLOR_NODE_BORDER_SELECTED.toQColor())

        self._textPen = QtGui.QPen()
        self._textPen.setStyle(QtCore.Qt.SolidLine)
        self._textPen.setColor(KSStyleingData.COLOR_NODE_TEXT.toQColor())

        self._nodeTextFont = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)

        self._contextMenu.addAction("Execute", self.executeImplicit)

        self.createInputs()
        if not self._tmpDisableAutoOutputs:
            self.createOutputs()

    def createInputs(self) -> None:
        self._inputs = {}

        for inputDefinitionKey in self._inputDefinitions:
            newInput = KSNodeInput(self, self._inputDefinitions[inputDefinitionKey])

            position = QtCore.QPointF()
            position.setX(-newInput.boundingRect().width() / 2 + self._borderWidth / 2)
            position.setY(sum([self._inputs[key].boundingRect().height() for key in self._inputs]) + self._borderWidth / 2 + self._bodyMarginBottom + self.bodyBoundingRect().y())
            newInput.setPos(position)
                
            self._inputs[inputDefinitionKey] = newInput 

            self.recalculateBodySize()

    def createOutputs(self) -> None:

        self._outputs = {}

        for outputDefinitionKey in self._outputDefinitions:
            newOutput = KSNodeOutput(self, self._outputDefinitions[outputDefinitionKey])

            position = QtCore.QPointF()
            position.setX(self.bodyBoundingRect().width() - (newOutput.boundingRect().width() / 2 + self._borderWidth / 2))
            position.setY(sum([self._outputs[key].boundingRect().height() for key in self._outputs]) + self._borderWidth / 2 + self._bodyMarginBottom + self.bodyBoundingRect().y())
            newOutput.setPos(position)

            self._outputs[outputDefinitionKey] = newOutput 

            self.recalculateBodySize()

    def getInputData(self, inputKey: str) -> typing.Any:
        return self._inputs[inputKey].data()

    def setOutputData(self, outputKey: str, data: typing.Any) -> None:
        self._outputs[outputKey].setData(data)

    def executeImplicit(self) -> None:
        executeAnnotations: dict = self.execute.__annotations__
        if ('return' not in executeAnnotations):
            print("ERROR: The 'execute' function always need to provide a return type! If the desired return type is void/None, use the 'None' type.")
            return

        executeArgs = []
        for annotationKey in executeAnnotations:
            if (annotationKey == 'return'):
                continue
            elif (annotationKey in self._inputs):
                executeArgs.append(self._inputs[annotationKey].data())
            else:
                print(f"ERROR: Failed to provide 'execute()' argument with identifier: {annotationKey}")

        if (executeAnnotations['return'] == None):
            self.execute(*executeArgs)
        else:
            executeReturnData = self.execute(*executeArgs)
            if (type(executeReturnData) != executeAnnotations['return']):
                print("ERROR: The data returned by execute() did not match with the specified return type!")
                return
            self._outputs['return'].setData(executeReturnData)

    def execute(self) -> None:
        pass

    # region Serialization
    def serialize(self) -> object:
        data = {
            'typeIdentifier': self.typeIdentifier(),
            'UUID': self.uniqueIdentifier(),
            'position': [self.scenePos().x(), self.scenePos().y()],
            'inputs': { i:self._inputs[i].serialize() for i in self._inputs }
        }

        return data

    @staticmethod
    def deserialize(nodeGraph: "KSNodeGraph", data: object) -> KSNodeInput:
        # print(f" - {data}")

        nodeType = nodeGraph.getNodeTypeFromIdentifier(data['typeIdentifier'])
        if (nodeType != None and isinstance(nodeType, KSNodeItem)):
            print("ERROR: Failed to deserialize node.")
            return
        
        node = nodeType()
        node._uniqueIdentifier = data['UUID']
        node.setPos(data['position'][0], data['position'][1])

        return node

    def deserializeInputs(self, nodeGraph: "KSNodeGraph", data: object) -> None:
        for inputKey in data['inputs']:
            if (inputKey in self._inputs):
                inputData = data['inputs'][inputKey]
                self._inputs[inputKey].deserialize(nodeGraph, inputData)

    @classmethod
    def typeIdentifier(cls) -> str:
        return cls.__name__
    
    def uniqueIdentifier(self) -> str:
        if (self._uniqueIdentifier == None):
            self._uniqueIdentifier =  ("NODE_" + str(uuid.uuid4().int))

        return self._uniqueIdentifier
    # endregion

    @property
    def pen(self):
        if self.isSelected():
            return self._penSel
        else:
            return self._pen

    def recalculateBodySize(self):
        newWidth = self._bodySize.width()
        newHeight = self._borderWidth + self._bodyMarginTop + self._bodyMarginBottom

        inputHeight = sum([self._inputs[key].boundingRect().height() for key in self._inputs])
        outputHeight = sum([self._outputs[key].boundingRect().height() for key in self._outputs])
        newHeight += max(inputHeight, outputHeight)

        self._bodySize = QtCore.QSizeF(newWidth, newHeight)

    def headerBoundingRect(self) -> QtCore.QRectF:
        margin = (self._headerSize.width() - self._bodySize.width()) * 0.5
        return QtCore.QRectF(QtCore.QPointF(-margin, 0), self._headerSize)

    def bodyBoundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(QtCore.QPointF(0, self._headerSize.height()), self._bodySize)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._bodySize.width(), self._bodySize.height() + self._headerSize.height())

    def paint(self, painter, option, widget):
        # Debug
        """painter.fillRect(self.boundingRect(), QtCore.Qt.yellow)
        painter.fillRect(self.bodyBoundingRect(), QtCore.Qt.green)
        painter.fillRect(self.headerBoundingRect(), QtCore.Qt.blue)"""

        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)
        margin = QtCore.QMarginsF(self._borderWidth / 2, self._borderWidth / 2, self._borderWidth / 2, self._borderWidth / 2)
        painter.drawRoundedRect(self.bodyBoundingRect().marginsRemoved(margin), 10, 10)

        # Node label.
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)
        """metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self._title).width() + 14
        text_height = metrics.boundingRect(self._title).height() + 14
        self._headerSize = QtCore.QSizeF(text_width, text_height)"""
        painter.drawText(self.headerBoundingRect(), QtCore.Qt.AlignCenter, self._title)

    def remove(self):
        scene = self.scene()
        scene.removeItem(self)

    def reload(self):
        print("Reload", self.__class__.__name__)
        importlib.reload(sys.modules[self.__class__.__name__])

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        self._contextMenu.exec_(event.screenPos())

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        # FIXME: The path updateing logic should be happening on drag move event, but i don't want to spend time debugging why that ain't working right now..-
        for inputKey in self._inputs:
            self._inputs[inputKey].updatePath()
        for outputKey in self._outputs:
            self._outputs[outputKey].updatePaths()

        super().mouseMoveEvent(event)

class KSViewportState(Enum):
    NONE = 1
    PANNING = 2
    ZOOMING = 3
    SELECTING = 4
    DRAGGING_ITEM = 5
    CREATING_CONNECTION = 6

class KSNodeGraph(QtWidgets.QGraphicsView):
    _contextMenu: QtWidgets.QMenu = None
    _lastMouseMovePosition: QtCore.QPoint = None
    _viewportState: KSViewportState = KSViewportState.NONE

    # Internal variables used for camera transformation calculations.
    _lastMouseMovePosition: QtCore.QPoint = None
    _lastRightMousePressPosition:QtCore.QPoint = None
    _lastRightMousePressVerticalScalingFactor:float = None
    _lastRightMousePressHorizontalScalingFactor:float = None

    _connectionPath: KSNodeConnectionPath = None
    _connectionOriginItem: typing.Union[KSNodeInput, KSNodeOutput] = None

    _nodeTypes: typing.Dict[str, type] = {}

    _addNodeMenu: QtWidgets.QMenu = None

    _activeFilepath: str = None

    def __init__(self, parent):
        super().__init__(parent)

        self.frameSelectedAction = QtWidgets.QAction("Frame Selected", self)
        self.frameSelectedAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F))
        self.frameSelectedAction.triggered.connect(self.frameSelected)
        self.addAction(self.frameSelectedAction)

        self.showAddNodeMenuAction = QtWidgets.QAction("Add Node", self)
        self.showAddNodeMenuAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Tab))
        self.showAddNodeMenuAction.triggered.connect(self.toggleAddNodeMenu)
        self.addAction(self.showAddNodeMenuAction)

        self.reloadGraphAction = QtWidgets.QAction("Reload", self)
        self.reloadGraphAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))
        self.reloadGraphAction.triggered.connect(self.reloadGraph)
        self.addAction(self.reloadGraphAction)

        self.newFileAction = QtWidgets.QAction("New File", self)
        self.newFileAction.setShortcut(QtGui.QKeySequence('Ctrl+N'))
        self.newFileAction.triggered.connect(self.newFile)
        self.addAction(self.newFileAction)

        self.saveFileAction = QtWidgets.QAction("Save", self)
        self.saveFileAction.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        self.saveFileAction.triggered.connect(self.saveFile)
        self.addAction(self.saveFileAction)

        self.saveFileAsAction = QtWidgets.QAction("Save As", self)
        self.saveFileAsAction.setShortcut(QtGui.QKeySequence('Ctrl+Shift+S'))
        self.saveFileAsAction.triggered.connect(self.saveFileAs)
        self.addAction(self.saveFileAsAction)

        self.openFileAction = QtWidgets.QAction("Open File", self)
        self.openFileAction.setShortcut(QtGui.QKeySequence('Ctrl+O'))
        self.openFileAction.triggered.connect(self.openFile)
        self.addAction(self.openFileAction)

        self._contextMenu = QtWidgets.QMenu()
        self._contextMenu.setMinimumWidth(200)
        self._contextMenu.setStyleSheet(STYLE_QMENU)
        self._contextMenu.addAction(self.showAddNodeMenuAction)
        self._contextMenu.addSeparator()
        self._contextMenu.addAction(self.reloadGraphAction)
        self._contextMenu.addAction(self.frameSelectedAction)
        self._contextMenu.addSeparator()
        self._contextMenu.addAction(self.newFileAction)
        self._contextMenu.addAction(self.saveFileAction)
        self._contextMenu.addAction(self.saveFileAsAction)
        self._contextMenu.addAction(self.openFileAction)

        self._addNodeMenu = QtWidgets.QMenu()
        self._addNodeMenu.setMinimumWidth(200)
        self._addNodeMenu.setStyleSheet(STYLE_QMENU)

        self.currentState = 'DEFAULT'

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)

        self.rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        scene = KSNodeScene(self)
        scene.setSceneRect(0, 0, 2000, 2000)
        self.setScene(scene)

        self.show()

    # region Serialization and deserialization
    def newFile(self):
        self.removeAllNodes()

    def saveFile(self):
        if (self._activeFilepath != None):
            with open(self._activeFilepath, "w") as filepath:
                filepath.write(self.serializeToJson())
        else:
            self.saveFileAs()

    def saveFileAs(self):
        fileInfo = QtWidgets.QFileDialog.getSaveFileName(self, caption="Save As", filter="Json Files (*.json)")
        self._activeFilepath = fileInfo[0]
        with open(self._activeFilepath, "w") as file:
            file.write(self.serializeToJson())

    def openFile(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, caption="Open File", filter="Json Files (*.json)")
        self.removeAllNodes()
        with open(filepath[0]) as file:
            data = file.read().replace('\n', '')
            self.deserializeFromJson(data)

    def serializeToJson(self) -> str:
        # Items
        items = []
        for item in self.scene().items():
            if (isinstance(item, KSNodeItem)):
                items.append(item.serialize())
                
        data = { 'items': items }
        return json.dumps(data)

    def deserializeFromJson(self, jsonStr: str) -> None:
        data = json.loads(jsonStr)

        # Deserialize items
        if (data['items'] != None):
            print(f"Deserializing {len(data['items'])} items:")
                
            # Add items
            deserializedNodes = []
            for itemData in data['items']:
                node = KSNodeItem.deserialize(self, itemData)
                deserializedNodes.append([node, itemData])
                self.addNode(node)

            # Add connections
            for nodeData in deserializedNodes:
                nodeData[0].deserializeInputs(self, nodeData[1])
    # endregion

    # region Rubberband
    def startRubberband(self, position):
        self._viewportState = KSViewportState.SELECTING
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
        self._viewportState = KSViewportState.NONE
    # endregion
    
    # region Connection
    def startConnection(self, originItem: typing.Union[KSNodeInput, KSNodeOutput]) -> None:
        if (type(originItem) not in (KSNodeInput, KSNodeOutput)):
            return

        self._viewportState = KSViewportState.CREATING_CONNECTION
        self._connectionOriginItem = originItem
        self._connectionPath = KSNodeConnectionPath(originItem.scenePos() + originItem.boundingRect().center(), originItem.scenePos() + originItem.boundingRect().center())
        self.scene().addItem(self._connectionPath)
        self.setInteractive(False)

    def updateConnection(self, mousePosition: QtCore.QPointF()) -> None:
        if (self._connectionPath == None or self._connectionOriginItem == None):
            return

        self._connectionPath.updatePath(self._connectionOriginItem.scenePos() + self._connectionOriginItem.boundingRect().center(), self.mapToScene(mousePosition))

    def releaseConnection(self, destinationItem: typing.Any) -> None:
        if (destinationItem != None):
            if (type(self._connectionOriginItem) == KSNodeInput and type(destinationItem) == KSNodeOutput):
                self._connectionOriginItem.connect(destinationItem)
            elif (type(self._connectionOriginItem) == KSNodeOutput and type(destinationItem) == KSNodeInput):
                destinationItem.connect(self._connectionOriginItem)
        self.scene().removeItem(self._connectionPath)
        self._connectionPath = None
        self._connectionOriginItem = None
        self.setInteractive(True)
        self._viewportState = KSViewportState.NONE
    # endregion

    # region Node related
    def reloadGraph(self) -> None:
        print("Reloading")

    def addNode(self, node: KSNodeItem) -> None:
        if (node.__class__.__name__ not in self._nodeTypes):
            print(f"ERROR: Failed to find node type with identifier: {node.__class__.__name__} in the node dictionary.")
            return
        self.scene().nodes['name'] = node
        self.scene().addItem(node)

    def removeNode(self, node: KSNodeInput) -> None:
        if (node in self.scene().items()):
           self.scene().removeItem(node)

    def removeAllNodes(self) -> None:
        for item in self.scene().items():
            if (isinstance(item, KSNodeItem)):
                self.removeNode(item)

    def addNodeType(self, nodeType: type) -> None:
        if (isinstance(nodeType, KSNodeItem) and nodeType.typeIdentifier() in self._nodeTypes):
            print(f"ERROR: The node dictionary already contains an entry with identifier: {nodeType.typeIdentifier()}.")
            return
        
        self._nodeTypes[nodeType.typeIdentifier()] = nodeType

        addNodeAction = QtWidgets.QAction(str(nodeType._title), self)
        addNodeAction.triggered.connect( lambda checked: self.addNodeFromNodeMenu(nodeType) )
        self._addNodeMenu.addAction(addNodeAction)

    def addNodeFromNodeMenu(self, nodeType: type) -> None:
        print(nodeType)
        node = nodeType()
        node.setPos(self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())))
        self.addNode(node)

    def getNodeTypeFromIdentifier(self, identifier: str) -> type:
        return self._nodeTypes[identifier]
    # endregion

    def frameSelected(self):
        if len(self.scene().selectedItems()) > 0:
            selectionBounds = self.scene().selectionItemsBoundingRect()
        else:
            selectionBounds = self.scene().itemsBoundingRect()
        selectionBounds = selectionBounds.marginsAdded(QtCore.QMarginsF(64, 64+50, 64, 64))
        self.fitInView(selectionBounds, QtCore.Qt.KeepAspectRatio)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        if (self._viewportState == KSViewportState.NONE and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
            self._contextMenu.exec_(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def toggleAddNodeMenu(self) -> None:
        self._addNodeMenu.exec_(QtGui.QCursor.pos())

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)

        # Frame selected.
        if event.key() == QtCore.Qt.Key_F:
            self.frameSelected()

    # region Mouse events
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.RightButton:
            self._lastRightMousePressPosition = event.pos()
            self._lastRightMousePressHorizontalScalingFactor = self.matrix().m11()
            self._lastRightMousePressVerticalScalingFactor = self.matrix().m22()

        # Camera panning
        if (QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier and event.button() in (QtCore.Qt.MiddleButton, QtCore.Qt.LeftButton)):
            self.window().setCursor(QtCore.Qt.SizeAllCursor)
            self._viewportState = KSViewportState.PANNING

        # Camera mouse zoom
        elif (QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier and event.button() == QtCore.Qt.RightButton):
            self.window().setCursor(QtCore.Qt.SizeVerCursor)
            self._viewportState = KSViewportState.ZOOMING

        # Rubberband selecting
        elif (event.button() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.NoModifier and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
            self.startRubberband(event.pos())
        
        # Create connection or click selecting
        elif (event.button() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.NoModifier and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is not None):
            item = self.itemAt(event.pos())

            # Create connection
            if (type(item) in (KSNodeInput, KSNodeOutput)):
                self.startConnection(item)
            
            # Select connection path
            elif (type(item) == KSNodeConnectionPath):
                pass
                #TODO: Handle

            # Click selecting / moveing
            else:
                self._viewportState = KSViewportState.DRAGGING_ITEM
                self.setInteractive(True)
                super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        
        if (self._viewportState == KSViewportState.CREATING_CONNECTION):
            item = self.itemAt(event.pos())
            self.releaseConnection(item)

        elif self._viewportState == KSViewportState.SELECTING:
            self.releaseRubberband()

        if (self._viewportState != KSViewportState.NONE):
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
            self.window().setCursor(QtCore.Qt.ArrowCursor)
        else:
            self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)

        self._viewportState = KSViewportState.NONE

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        # If these positions are not set/set to null vector, the later code will cause wired behaviour.
        if self._lastMouseMovePosition == None:
            self._lastMouseMovePosition = event.pos()
        if self._lastRightMousePressPosition == None:
            self._lastRightMousePressPosition = event.pos()

        # Camera panning
        if self._viewportState == KSViewportState.PANNING:
            delta = event.pos() - self._lastMouseMovePosition
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

        # Camera mouse zoom.
        elif self._viewportState == KSViewportState.ZOOMING:
            """ 
            Camera zooming; this is some freaking messy math, don't judge; it works pretty well! xD
            There is most likely a cleaner way of doing this but i honestly can't bother finding it.
            If this is triggering to you, feel free to hit me with a pull request.
            """
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            # TODO: Make zooming slower when distanceToOrigin increases
            # Capture data for correcting view translation offset.
            oldSceneSpaceOriginPoint = self.mapToScene(self._lastRightMousePressPosition)
            ### Calculate scaleing factor
            cursorPoint = QtGui.QVector2D(event.pos())
            originPoint = QtGui.QVector2D(self._lastRightMousePressPosition)
            orientationPoint = originPoint + QtGui.QVector2D(1, 1)
            orientationVector = orientationPoint - originPoint
            cursorVector = orientationPoint - cursorPoint
            # Introduce a small constant value if the vector length is 0.
            # This is needed since the vector normalization calulation will cause an error if the vector has a length of 0
            orientationVector = (orientationVector + QtGui.QVector2D(0.001, 0.001)) if bool(orientationVector.length() == 0) else orientationVector
            cursorVector = (cursorVector + QtGui.QVector2D(0.001, 0.001)) if bool(cursorVector.length() == 0) else cursorVector
            orientationUnitVector = orientationVector.normalized() # Normalization calulation
            cursorUnitVector = cursorVector.normalized() # Normalization calulation
            dotProduct = QtGui.QVector2D.dotProduct(orientationUnitVector, cursorUnitVector)
            distanceToOrigin = originPoint.distanceToPoint(cursorPoint)
            globalScaleFactor = 1 - (dotProduct * distanceToOrigin * 0.0015) # dot * dist * zoomSensitivity
            ### Create the actial matrix for applying the scale; the initial scaleing factors should be set on mouse putton pressed.
            finalHorizontalScalingFactor = min(max(self._lastRightMousePressHorizontalScalingFactor * globalScaleFactor, 0.2), 2)
            finalVerticalScalingFactor = min(max(self._lastRightMousePressVerticalScalingFactor * globalScaleFactor, 0.2), 2)
            # print(finalHorizontalScalingFactor)
            # print(finalVerticalScalingFactor) 
            horizontalScalingFactor = finalHorizontalScalingFactor # FIXME: This should possibly not by multiplying since it wont be linear; i think...
            verticalScalingFactor = finalVerticalScalingFactor # FIXME: If addition or subtraction is the correct way to go, the globalScaleFactor range need to change.
            verticalShearingFactor = self.matrix().m12()
            horizontalShearingFactor = self.matrix().m21()
            self.setMatrix(QtGui.QMatrix(horizontalScalingFactor, verticalShearingFactor, horizontalShearingFactor, verticalScalingFactor, self.matrix().dx(), self.matrix().dy()))
            # Correct view translation offset.
            newSceneSpaceOriginPoint = self.mapToScene(self._lastRightMousePressPosition)
            translationDelta = newSceneSpaceOriginPoint - oldSceneSpaceOriginPoint;
            self.translate(translationDelta.x(), translationDelta.y())
       
        # Creating connection
        elif (self._viewportState == KSViewportState.CREATING_CONNECTION):
            self.updateConnection(event.pos())

        # Selecting
        elif (self._viewportState == KSViewportState.SELECTING):
            self.updateRubberband(event.pos())

        # Capture necessary data used for camera transformation. 
        self._lastMouseMovePosition = event.pos()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        event.accept()
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        scaleFactor = (1.05) if (event.angleDelta().y() + event.angleDelta().x() > 0) else (0.95)
        self.scale(scaleFactor, scaleFactor)
    # endregion
    
class KSNodeScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.setBackgroundBrush(KSStyleingData.COLOR_VIEWPORT_BACKGROUND.toQColor())
        self.nodes = dict()

    def addItem(self, item: QtWidgets.QGraphicsItem) -> None:
        super().addItem(item)
        self.setSceneRect(self.itemsBoundingRect().marginsAdded(QtCore.QMarginsF(1024*128, 1024*128, 1024*128, 1024*128)))

    def selectionItemsBoundingRect(self) -> QtCore.QRectF:
        # Does not take untransformable items into account.
        boundingRect = QtCore.QRectF()
        for item in self.selectedItems():
            boundingRect |= item.sceneBoundingRect()
        return boundingRect