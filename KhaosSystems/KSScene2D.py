from PySide2 import QtWidgets, QtCore, QtGui
import typing

"""
The KSScene2D can be thought of as the scene data, the class also provides all necessary functions to alter and manage the scene items.
For a deeper understand of how this works i suggest reading up on the "Qt Graphics View Framework".
"""
class KSScene2D(QtWidgets.QGraphicsScene):
    # If false, items won't recieve events and vise-versa.
    shouldPropagateEventsToItems: bool = True
    # All InariItem in this list will recieve scene/global mouse events.
    _sceneMouseMoveEventListeners:typing.List["KSSceneItem"] = []

    # Constructor
    def __init__(self, parentItem: QtWidgets.QGraphicsItem) -> None:
        super().__init__(parentItem)
        # Register signals
        QtCore.QObject.connect(self, QtCore.SIGNAL("selectionChanged()"), self.selectionChangedSignal)

    # If false, items won't recieve events and vise-versa.
    def setShouldPropagateEventsToItems(self, shouldPropagateEventsToItems: bool) -> None:
        self.shouldPropagateEventsToItems = shouldPropagateEventsToItems

    # Returns bounding box of the selected items. 
    def selectionItemsBoundingRect(self) -> QtCore.QRectF:
        # Does not take untransformable items into account.
        boundingRect = QtCore.QRectF()
        for item in self.selectedItems():
            boundingRect |= item.sceneBoundingRect()
        return boundingRect

    # Registers an InariItem for receiving scene space/global mouse events.
    def registerSceneMouseMoveEventListener(self, item: "KSSceneItem") -> None:
        self._sceneMouseMoveEventListeners.append(item)

    # Unregisters an InariItem for receiving scene space/global mouse events.
    def unregisterSceneMouseMoveEventListener(self, item: "KSSceneItem") -> None:
        self._sceneMouseMoveEventListeners.remove(item)

    # Overwritten mouse move event handler, please refer to the QT documentation.
    def mouseMoveEvent(self, event:QtWidgets.QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        # Notify all InariItems registered for scene mouse move events.
        for listener in self._sceneMouseMoveEventListeners:
            listener.sceneMouseMoveEvent(event)
    
    # Overwritten master event handler/dispatcher, please refer to the QT documentation.
    def event(self, event: QtCore.QEvent) -> bool:
        # Handle event blocking.
        if self.shouldPropagateEventsToItems:
            return super().event(event)
        else:
            # Mark the event as handled.
            return True

    # Overwritten addItem function, please refer to the QT documentation.
    def addItem(self, item: QtWidgets.QGraphicsItem) -> None:
        super().addItem(item)
        # Recalculate the scene rect size and add a big margin, this allows freer scene movement
        # since camera transformations won't be blocked due to the small default scene size.
        self.setSceneRect(self.itemsBoundingRect().marginsAdded(QtCore.QMarginsF(1024*128, 1024*128, 1024*128, 1024*128)))

    # Connected to the selectionChanged() signal, please refer to the QT documentation.
    def selectionChangedSignal(self) -> None:
        pass
        # Tell the host application to update it's selection to match Inari.
        # items = [item.itemName for item in self.selectedItems() if isinstance(item, InariLocator)]
        # self.commandInterpreter.Host_SetSelection(items)