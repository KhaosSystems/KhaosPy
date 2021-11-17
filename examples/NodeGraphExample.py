import KhaosSystems
import importlib
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector
from PySide2 import QtWidgets, QtCore, QtGui
import typing

class KSGraphicsTextInput(QtWidgets.QGraphicsTextItem):
    def __init__(self, text: str, parent: typing.Optional[QtWidgets.QGraphicsItem] = ...) -> None:
        super().__init__(text, parent=parent)

        self.setTextInteractionFlags(QtCore.Qt.TextEditable)

class KSNodeInput(QtWidgets.QGraphicsItem):
    _datatype = None
    _size: QtCore.QSizeF = QtCore.QSizeF(200, 20)
    _manualInput: KSGraphicsTextInput = None
    _connection: "KSNodeOutput" = None
    
    def __init__(self, parent: QtWidgets.QGraphicsItem, datatype):
        super().__init__(parent=parent)

        self._datatype = datatype
        
        if (self._datatype == str):
            self._manualInput = KSGraphicsTextInput("L_Joint_jnt", self)

    def setSize(self, x: float, y: float):
        self._size = QtCore.QSizeF(x, y)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(QtCore.QPointF(0, 0), self._size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        painter.fillRect(self.boundingRect(), QtCore.Qt.red)

    def value(self):
        if (self._connection == None):
            if (self._datatype == str and self._manualInput != None):
                return str(self._manualInput.toPlainText())
            else:
                return self._datatype()
        else:
            return self._connection.value()

class KSNodeOutput(QtWidgets.QGraphicsItem):
    _node = None
    _datatype = None
    _data = "NOT UPDATED"

    def __init__(self, parent: "KSNodeItemDev", datatype):
        super().__init__(parent=parent)
        
        self._node = parent
        self._datatype = datatype

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 15, 15)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        painter.fillRect(self.boundingRect(), QtCore.Qt.red)
    
    def value(self):
        self._node.executeAction()
        return self._data

class KSNodeConnection(QtWidgets.QGraphicsPathItem):
    origin = None
    target = None
    
    def __init__(self, origin: KSNodeInput, target: KSNodeOutput) -> None:
        super().__init__()

        self.origin = origin
        self.target = target

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        self.updatePath()
        return super().paint(painter, option, widget=widget)

    def updatePath(self):
        self._pen = QtGui.QPen(QtCore.Qt.red)
        self._pen.setWidth(8)
        self.setPen(self._pen)

        self.target_point = self.origin.scenePos()
        self.source_point = self.target.scenePos()

        path = QtGui.QPainterPath()
        path.moveTo(self.source_point)
        dx = (self.target_point.x() - self.source_point.x()) * 0.5
        dy = self.target_point.y() - self.source_point.y()
        ctrl1 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 0)
        ctrl2 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 1)
        path.cubicTo(ctrl1, ctrl2, self.target_point)

        self.setPath(path)

class KSNodeItemDev(KSNodeItem):
    _inputs: typing.Dict[str, KSNodeInput] = {}
    _outputs: typing.Dict[str, KSNodeOutput] = {}

    def __init__(self) -> None:
        super().__init__()

        self._contextMenu.addAction("Execute", self.executeAction)

        self.createInputs()
        self.createOutputs()

    def createInputs(self):
        self._inputs = {}
        
        executeAnnotations: dict = self.execute.__annotations__
        for annotationKey in executeAnnotations:
            if (annotationKey == 'return'):
                continue
            else:
                newInput = KSNodeInput(self, executeAnnotations[annotationKey])
                newInput.setSize(self.boundingRect().width() - 4, 15)
                newInput.setPos(2, self.headerBoundingRect().height() + len(self._inputs) * 15 + 10)
                self._bodySize.setHeight(max(self._bodySize.height() + 15, self._bodySize.height()))
                self._inputs[annotationKey] = newInput 

    def createOutputs(self):
        self._outputs = {}

        executeAnnotations: dict = self.execute.__annotations__
        if ('return' not in executeAnnotations):
            print("ERROR: The execute() function to provide a return type!")
            return

        if (executeAnnotations['return'] != None):
            newOutput = KSNodeOutput(self, executeAnnotations['return'])
            newOutput.setPos(self.boundingRect().width() - 9.5, self.headerBoundingRect().height() + len(self._outputs) * 15 + 10)
            self._outputs['return'] = newOutput 

    def executeAction(self):
        executeAnnotations: dict = self.execute.__annotations__
        if ('return' not in executeAnnotations):
            print("ERROR: The execute() function to provide a return type!")
            return

        executeArgs = []
        for annotationKey in executeAnnotations:
            if (annotationKey == 'return'):
                continue
            elif (annotationKey in self._inputs):
                executeArgs.append(self._inputs[annotationKey].value())
            else:
                print(f"ERROR: Failed to handle execute() parameter with type: {executeAnnotations[annotationKey]}")

        if (executeAnnotations['return'] != None):
            executeReturnData = self.execute(*executeArgs)
            if (type(executeReturnData) != executeAnnotations['return']):
                print("ERROR: The data returned by execute() did not fit with the specified return type!")
                return
            self._outputs['return']._data = executeReturnData
            print(executeReturnData)
        else:
            self.execute(*executeArgs)

    def execute(self) -> None:
        pass
    
class StringConstantNode(KSNodeItemDev):
    def __init__(self):
        super().__init__()
        self._title = "Sting Constant"

    def execute(self) -> str:
        return "String123"
    
class PrintString(KSNodeItemDev):
    def __init__(self):
        super().__init__()
        self._title = "Print String"

    def execute(self, string: str) -> None:
        print(string)

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeA = StringConstantNode()
nodeB = PrintString()

nodeGraph.addNode(nodeA)
nodeGraph.addNode(nodeB)

nodeB._inputs['string']._connection = nodeA._outputs['return']

pathItem = KSNodeConnection(nodeB._inputs['string'], nodeA._outputs['return'])
nodeGraph.scene().addItem(pathItem)
pathItem.updatePath()

app.exec_()