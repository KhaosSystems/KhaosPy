from PySide2 import QtWidgets, QtCore, QtGui, QtSvg
import typing

"""
KSSceneItem is the master class for all scene items.
If you want to create an item with custom logic, it needs to inherit from KSSceneItem.
"""
class KSSceneEntity(QtWidgets.QGraphicsItem):
    def __init__(self) -> None:
        super().__init__()

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, 0, 0)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        pass