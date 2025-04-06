from PySide6 import QtWidgets, QtGui, QtCore

class GraphicsLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, backgroundColor: QtGui.QColor, color: QtGui.QColor = "black", text: str = ""):
        super().__init__(text)
        self.backgroundColor = backgroundColor
        self.text = text
        self.setDefaultTextColor(color)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.backgroundColor)))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)