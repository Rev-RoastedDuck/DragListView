from PySide6.QtWidgets import QListView
from PySide6.QtCore import Qt, QRect, QModelIndex, QTimer
from PySide6.QtGui import QStandardItem, QDragEnterEvent,QDropEvent, QDragMoveEvent, QMouseEvent, QKeyEvent

from card_delegate import CardDelegate



class CardListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.__dragged_item = None
        self.__is_dragging = False
        self.__scroll_bar_timer = None
        self.__scroll_area_to_left = False
        self.anim_index: QModelIndex = QModelIndex()

        self.setAutoScroll(False)
        self.scrollAreaTimerInit()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        super().dragEnterEvent(event)
        self.__is_dragging = True
        self.__dragged_item = self.indexAt(event.position().toPoint())

    def dropEvent(self, event: QDropEvent) -> None:
        super().dropEvent(event)
        self.__scroll_bar_timer.stop()

        self.__is_dragging = False
        delegate = self.itemDelegate()
        if isinstance(delegate, CardDelegate):
            delegate.setDragStatus(False)

        data = self.__dragged_item.data()
        dragged_row_old = self.__dragged_item.row()
        dragged_row_new = self.indexAt(event.position().toPoint()).row()

        self.model().removeRow(dragged_row_old)

        item = QStandardItem()
        item.setData(data, Qt.DisplayRole)
        self.model().insertRow(dragged_row_new, item)

        index = self.model().index(dragged_row_new, 0, QModelIndex())
        self.setCurrentIndex(index)

    def dragMoveEvent(self, event: QDragMoveEvent):
        super().dragMoveEvent(event)
        x = event.position().x()
        scroll_area_width = self.viewport().width()

        curr_index = self.indexAt(event.position().toPoint())
        delagate = self.itemDelegate()
        if isinstance(delagate, CardDelegate):
            delagate.setDragIndex(curr_index)
            delagate.setDragStatus(True)

            self.repaint(QRect(0, 0, self.width(), self.height()))

        if x < 30:
            self.__scroll_area_to_left = True
            self.__scroll_bar_timer.start()
        elif x > scroll_area_width - 30:
            self.__scroll_area_to_left = False
            self.__scroll_bar_timer.start()
        else:
            self.__scroll_bar_timer.stop()

    def scrollAreaTimerInit(self):
        self.__scroll_bar_timer = QTimer()
        self.__scroll_bar_timer.setInterval(10)
        self.__scroll_bar_timer.timeout.connect(self.__scrollBarMove)

    def __scrollBarMove(self):
        if self.__scroll_area_to_left:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 4)
        else:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + 4)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        super().mouseReleaseEvent(e)
        self.__scroll_bar_timer.stop()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete:
            self.delItem()

    def delItem(self):
        selected_indexes = self.selectedIndexes()
        if not selected_indexes:
            return
        selected_index = selected_indexes[0]
        index_rect = self.visualRect(selected_index)

        delagate = self.itemDelegate()
        if isinstance(delagate, CardDelegate):
            delagate.animStart(list_view=self, index=selected_index, index_rect=index_rect)

        self.setCurrentIndex(selected_index)

    def addItem(self):
        pass
