import KhaosSystems
import importlib
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector, KSNodeInput, KSNodeOutput
from PySide2 import QtWidgets, QtCore, QtGui
import typing

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

app.exec_()