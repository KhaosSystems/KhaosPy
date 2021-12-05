import KhaosSystems
import importlib
import typing
importlib.reload(KhaosSystems)

from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector, KSNodeInput, KSNodeOutput
from PySide2 import QtWidgets, QtCore, QtGui

class StringConstantNode(KSNodeItem):
    _title: str = "Sting Constant"
    _outputDefinitions: typing.Dict[str, type] = {"String": str, "Int": int}

    def execute(self) -> None:
        return "String1234"

class PrintString(KSNodeItem):
    _title: str = "Print String"
    
    def execute(self, string: str, boolean: bool) -> None:
        print(string)

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeGraph.addNodeType(StringConstantNode)
nodeGraph.addNodeType(PrintString)

app.exec_()