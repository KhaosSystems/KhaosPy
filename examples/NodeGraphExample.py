from KhaosSystems import KSNodeGraph
from PySide2 import QtWidgets

app = QtWidgets.QApplication()

nodeGraph = KSNodeGraph(None)
newNode = nodeGraph.CreateNode()
nodeGraph.Show()

app.exec_()    