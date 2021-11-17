import KhaosSystems
import importlib
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector, KSNodeInput, KSNodeOutput
from PySide2 import QtWidgets, QtCore, QtGui
import typing

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
    
class StringConstantNode(KSNodeItem):
    def __init__(self):
        super().__init__()
        self._title = "Sting Constant"

    def execute(self) -> str:
        return "String123"
    
class PrintString(KSNodeItem):
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