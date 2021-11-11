import PySide2
from PySide2 import QtWidgets, QtCore, QtGui
import typing

"""
KSViewport2D is a viewport build upon the QGraphicsView, there can be multiple KSViewport2D bound to the same KSScene2D.
For a deeper understand of how this works i suggest reading up on the "Qt Graphics View Framework".
"""
class KSViewport2D(QtWidgets.QGraphicsView):
    # Internal variables used for camera transformation calculations.
    _lastMouseMovePosition: QtCore.QPoint = None
    _lastRightMousePressPosition:QtCore.QPoint = None
    _lastRightMousePressVerticalScalingFactor:float = None
    _lastRightMousePressHorizontalScalingFactor:float = None

    # Constructor
    def __init__(self, scene: QtWidgets.QGraphicsScene, parent: QtWidgets.QWidget = None):
        super().__init__(scene, parent)
        # Configuration
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setGeometry(0, 0, 300, 300)
        self.setBackgroundBrush(QtGui.QColor(26, 26, 26))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

    # Frames the selected items within the view bounds, or all of them if no items are selected.
    def frameSelected(self):
        # Find the base selection bound.
        if len(self.scene().selectedItems()) > 0:
            selectionBounds = self.scene().selectionItemsBoundingRect()
        else:
            selectionBounds = self.scene().itemsBoundingRect()
        # Add a margin to avoid creating tangents with the window border.
        selectionBounds = selectionBounds.marginsAdded(QtCore.QMarginsF(64, 64+50, 64, 64))
        self.fitInView(selectionBounds, QtCore.Qt.KeepAspectRatio)

    # Overwritten key press event handler, please refer to the QT documentation.
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)

        # Frame selected.
        if event.key() == QtCore.Qt.Key_F:
            self.frameSelected()

        # Camera panning.
        if bool(QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier):
            # Disable box selection and don't propagate events to items until released.
            self.scene().setShouldPropagateEventsToItems(False)
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    # Overwritten key release event handler, please refer to the QT documentation.
    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyReleaseEvent(event)

        # Camera panning.
        if not bool(QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier):
            # Re-enable Re-enable disabled box selection and enable item event propagate again.
            self.scene().setShouldPropagateEventsToItems(True)
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

    # Overwritten mouse pressed event handler, please refer to the QT documentation.
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)

        # Capture necessary data used for camera transformation.
        if event.button() == QtCore.Qt.RightButton:
            self._lastRightMousePressPosition = event.pos()
            # m11() returns the horizontal scaling factor of the transform matrix.
            self._lastRightMousePressHorizontalScalingFactor = self.matrix().m11()
            # m11() returns the vertical scaling factor of the transform matrix.
            self._initialRightMousePressVerticalScalingFactor = self.matrix().m22()

        # Set cursor corresponding to the active transformation state.
        if bool(QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier):
            if bool((event.buttons() & QtCore.Qt.MiddleButton) or (event.buttons() & QtCore.Qt.LeftButton)):
                # Panning.
                self.window().setCursor(QtCore.Qt.SizeAllCursor)
            elif bool(event.buttons() & QtCore.Qt.RightButton):
                # Zooming.
                self.window().setCursor(QtCore.Qt.SizeVerCursor)

    # Overwritten mouse release event handler, please refer to the QT documentation.
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        # Set default cursor; the cursor might have been changed in the when the mouse was pressed.
        self.window().setCursor(QtCore.Qt.ArrowCursor)

    # Overwritten mouse move event handler, please refer to the QT documentation.
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

        # If these positions are not set/set to null vector, the later code will cause wired behaviour.
        if self._lastMouseMovePosition == None:
            self._lastMouseMovePosition = event.pos()
        if self._lastRightMousePressPosition == None:
            self._lastRightMousePressPosition = event.pos()

        # Camera transformation logic.
        if bool(QtWidgets.QApplication.queryKeyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier):
            if bool((event.buttons() & QtCore.Qt.MiddleButton) or (event.buttons() & QtCore.Qt.LeftButton)):
                # Camera panning.
                verticalScrollBar = self.verticalScrollBar()
                horizontalScrollBar = self.horizontalScrollBar()
                delta = event.pos() - self._lastMouseMovePosition
                verticalScrollBar.setValue(verticalScrollBar.value() - delta.y())
                horizontalScrollBar.setValue(horizontalScrollBar.value() - delta.x())
            elif bool(event.buttons() & QtCore.Qt.RightButton):
                """ 
                Camera zooming; this is some freaking messy math, don't judge; it works pretty well! xD
                There is most likely a cleaner way of doing this but i honestly can't bother finding it.
                If this is triggering to you, feel free to hit me with a pull request.
                """
                self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
                # TODO: Make zooming slower when distanceToOrigin increases
                # Capture data for correcting view translation offset.
                oldSceneSpaceOriginPoint = self.mapToScene(self._lastRightMousePressPosition)
                ### Calculate scaleing factor
                cursorPoint = QtGui.QVector2D(event.pos())
                originPoint = QtGui.QVector2D(self._lastRightMousePressPosition)
                orientationPoint = originPoint + QtGui.QVector2D(1, 1)
                orientationVector = orientationPoint - originPoint
                cursorVector = orientationPoint - cursorPoint
                # Introduce a small constant value if the vector length is 0.
                # This is needed since the vector normalization calulation will cause an error if the vector has a length of 0
                orientationVector = (orientationVector + QtGui.QVector2D(0.001, 0.001)) if bool(orientationVector.length() == 0) else orientationVector
                cursorVector = (cursorVector + QtGui.QVector2D(0.001, 0.001)) if bool(cursorVector.length() == 0) else cursorVector
                orientationUnitVector = orientationVector.normalized() # Normalization calulation
                cursorUnitVector = cursorVector.normalized() # Normalization calulation
                dotProduct = QtGui.QVector2D.dotProduct(orientationUnitVector, cursorUnitVector)
                distanceToOrigin = originPoint.distanceToPoint(cursorPoint)
                globalScaleFactor = 1 - (dotProduct * distanceToOrigin * 0.0015) # dot * dist * zoomSensitivity
                ### Create the actial matrix for applying the scale; the initial scaleing factors should be set on mouse putton pressed.
                finalHorizontalScalingFactor = min(max(self._lastRightMousePressHorizontalScalingFactor * globalScaleFactor, 0.2), 2)
                finalVerticalScalingFactor = min(max(self._initialRightMousePressVerticalScalingFactor * globalScaleFactor, 0.2), 2)
                # print(finalHorizontalScalingFactor)
                # print(finalVerticalScalingFactor) 
                horizontalScalingFactor = finalHorizontalScalingFactor # FIXME: This should possibly not by multiplying since it wont be linear; i think...
                verticalScalingFactor = finalVerticalScalingFactor # FIXME: If addition or subtraction is the correct way to go, the globalScaleFactor range need to change.
                verticalShearingFactor = self.matrix().m12()
                horizontalShearingFactor = self.matrix().m21()
                self.setMatrix(QtGui.QMatrix(horizontalScalingFactor, verticalShearingFactor, horizontalShearingFactor, verticalScalingFactor, self.matrix().dx(), self.matrix().dy()))
                # Correct view translation offset.
                newSceneSpaceOriginPoint = self.mapToScene(self._lastRightMousePressPosition)
                translationDelta = newSceneSpaceOriginPoint - oldSceneSpaceOriginPoint;
                self.translate(translationDelta.x(), translationDelta.y())
       
        # Capture necessary data used for camera transformation. 
        self._lastMouseMovePosition = event.pos()

    # Overwritten wheel event handler, please refer to the QT documentation.
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # Accepting the event stops it from propagating, canceling the default scroll behaviour.
        event.accept()

        # Mouse wheel zooming
        zoomFactor = 1.05
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        # Add angleDelta() x and y to get propper mouse wheel delta.
        if event.angleDelta().y() + event.angleDelta().x() > 0:
            self.scale(zoomFactor, zoomFactor)
        else:
            self.scale(1 / zoomFactor, 1 / zoomFactor)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        return
        
        # TODO: Dots.

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())


        # print(self.mapToScene(int(rect.left()), int(rect.top())))
        print(self.matrix().dx())
        pen = QtGui.QPen(QtGui.QColor(46, 84, 255))
        pen.setWidth(5)
        painter.setPen(pen)
        for x in range(0, 1000, 50):
            for y in range(0, 1000, 50):
                painter.drawPoint(int(x + self.matrix().dx()), int(y + self.matrix().dy()))

        painter.restore()