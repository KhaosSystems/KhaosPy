import KhaosSystems
import importlib
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector
from PySide2 import QtWidgets, QtCore, QtGui
import typing

class KSNodeInput(QtWidgets.QGraphicsItem):
    _datatype = None
    _data = None
    _size: QtCore.QSizeF = QtCore.QSizeF(200, 20)

    def __init__(self, parent: QtWidgets.QGraphicsItem, datatype):
        super().__init__(parent=parent)

        self._datatype = datatype

    def setSize(self, x: float, y: float):
        self._size = QtCore.QSizeF(x, y)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(QtCore.QPointF(0, 0), self._size)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        painter.fillRect(self.boundingRect(), QtCore.Qt.red)

    def value(self):
        if (self._data != None):
            return self._datatype()
        else:
            return self._datatype() 

class ExampleNode(KSNodeItem):
    _inputs: typing.Dict[str, KSNodeInput] = {}

    def __init__(self) -> None:
        super().__init__()

        self._contextMenu.addAction("Execute", self.executeAction)

        self.createInputs()

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
                self._bodySize.setHeight(self._bodySize.height() + 15)
                self._inputs[annotationKey] = newInput 

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

        executeReturnData = self.execute(*executeArgs)
        if (type(executeReturnData) != executeAnnotations['return']):
            print("ERROR: The data returned by execute() did not fit with the specified return type!")
            return

        print(executeReturnData)

    def execute(self, string: str, integer: int, vector: KSVector) -> int:
        print(f"String: {string}")
        print(f"Integer: {integer}")
        print(f"KSVector: {vector}")

        return 2
    

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeGraph.addNode(ExampleNode())

"""parentNode.setPos(100, 100)
childNode._input = parentNode
parentNode._output = childNode
"""

# pathItem = KSNodeConnection(parentNode._output, childNode._input)
# nodeGraph.scene().addItem(pathItem)

app.exec_()    