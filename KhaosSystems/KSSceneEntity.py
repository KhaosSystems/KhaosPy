from PySide2 import QtWidgets, QtCore, QtGui, QtSvg
import typing

"""
KSSceneItem is the master class for all scene items.
If you want to create an item with custom logic, it needs to inherit from KSSceneItem.
"""
class KSSceneEntity(QtWidgets.QGraphicsItem):
    # The owning InariWidget.
    inariWidget: "InariWidget" = None
    # The QSvgRenderer used to render the item. 
    renderer: QtSvg.QSvgRenderer = None

    # Constructor.
    def __init__(self, inariWidget: "InariWidget", filepath: str) -> None:
        super().__init__()

        # Configure the item.
        self.inariWidget = InariWidget
        self.renderer = QtSvg.QSvgRenderer(filepath)

    # Overwritten boundingRect() method, please refer to the QT documentation.
    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(QtCore.QPointF(0, 0), self.renderer.defaultSize())

    # Overwritten paint method, please refer to the QT documentation.
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        self.renderer.render(painter, self.boundingRect())