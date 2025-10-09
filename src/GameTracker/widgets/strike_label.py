from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt 
import re

class StrikeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.strike_enable = False
        
        self._pen = QPen(QColor(200, 0, 0, 110), 2, Qt.SolidLine)
        
        self.setTextFormat(Qt.PlainText)
        self.setContentsMargins(0, 0, 0, 0)
        
    def enable_strike(self, enable=True):
        self.strike_enable = enable
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.strike_enable:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self._pen)
        
        rect = self.contentsRect()
        fm = self.fontMetrics()
        text = self.text()
        
        idx = text.rfind('$')
        if idx == -1:
            idx = text.rfind('£')
        if idx == -1:
            idx = text.rfind('€')
        if idx == -1:
            m = re.search(r'(\d[\d,\.]*\s*$)', text)
            idx = m.start() if m else -1
        
        total_width = fm.horizontalAdvance(text)
        
        if idx == -1:
            start_x = rect.x()
            strike_width = total_width
        else:
            prefix = text[:idx]
            price_part = text[idx:]
            prefix_w = fm.horizontalAdvance(prefix)
            price_w = fm.horizontalAdvance(price_part)
            
            align = self.alignment()
            if align & Qt.AlignHCenter:
                base_x = rect.x() + (rect.width() - total_width) // 2
            elif align & Qt.AlignRight:
                base_x = rect.x() + (rect.width() - total_width)
            else:
                base_x = rect.x()
                
            start_x = base_x + prefix_w
            strike_width = price_w
            
        y = rect.y() + rect.height() // 2
        painter.drawLine(start_x, y, start_x + strike_width, y)
        painter.end()