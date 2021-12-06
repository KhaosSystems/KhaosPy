import KhaosSystems
import importlib
import typing
importlib.reload(KhaosSystems)
import string
import random
from KhaosSystems import KSNodeGraph, KSNodeItem, KSVector, KSNodeInput, KSNodeOutput
from PySide2 import QtWidgets, QtCore, QtGui

class StringConstantNode(KSNodeItem):
    _title: str = "Sting Constant"
    _inputDefinitions: typing.Dict[str, type] = {"Seed": str}
    _outputDefinitions: typing.Dict[str, type] = {"String": str, "Int": int}

    def execute(self) -> None:
        print("StringConstantNode::Execute()")

        alphabet = list(string.ascii_lowercase)
        
        random.seed(self.getInputData("Seed"))
        randomString = ''.join(alphabet[random.randint(0, len(alphabet)-1)] for _ in range(16))
        randomInt = random.randint(0, 4096)

        self.setOutputData("String", randomString)
        self.setOutputData("Int", randomInt)

class PrintString(KSNodeItem):
    _title: str = "Print String"
    _inputDefinitions: typing.Dict[str, type] = {"String": str}

    def execute(self) -> None:
        print("PrintString::Execute()")
        print(self.getInputData("String"))

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
nodeGraph.addNodeType(StringConstantNode)
nodeGraph.addNodeType(PrintString)

app.exec_()