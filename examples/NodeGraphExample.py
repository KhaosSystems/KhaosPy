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
        self._outputs["String"].setData("String1234")
        self._outputs["Int"].setData(1234)

class PrintString(KSNodeItem):
    _title: str = "Print String"
    _inputDefinitions: typing.Dict[str, type] = {"String": str, "Boolean": bool}

    def execute(self) -> None:
        print(self._inputs["String"].data())

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeGraph.addNodeType(StringConstantNode)
nodeGraph.addNodeType(PrintString)

app.exec_()