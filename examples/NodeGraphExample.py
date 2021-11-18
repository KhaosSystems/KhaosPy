import KhaosSystems
import importlib
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector, KSNodeInput, KSNodeOutput
from PySide2 import QtWidgets, QtCore, QtGui

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

    def execute(self, string: str, boolean: bool) -> None:
        print(string)

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeA = StringConstantNode()
nodeB = PrintString()

nodeGraph.addNodeType(StringConstantNode)
nodeGraph.addNodeType(PrintString)

nodeGraph.addNode(nodeA)
nodeGraph.addNode(nodeB)

nodeGraph.serializeToFile("./graph.json")
nodeGraph.deserializeFromFile("./graph.json")

app.exec_()