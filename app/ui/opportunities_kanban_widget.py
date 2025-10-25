from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QLineEdit, QPushButton, QDialog, QMessageBox
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal as Signal
from PyQt6.QtGui import QDrag, QAction, QColor, QFont

from app.opportunities import opportunities_manager
from app.data import settings_manager
from app.opportunities.edit_opportunity_dialog import EditOpportunityDialog

class OpportunitiesKanbanWidget(QWidget):
    opportunity_updated = Signal() # Signal to notify other parts of the app about changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar oportunidades...")
        self.search_input.textChanged.connect(self.filter_opportunities)
        self.layout.addWidget(self.search_input)

        self.kanban_columns_widget = QWidget()
        self.kanban_columns_layout = QHBoxLayout(self.kanban_columns_widget)
        self.kanban_columns_layout.setContentsMargins(0, 0, 0, 0)
        self.kanban_columns_layout.setSpacing(5)
        self.layout.addWidget(self.kanban_columns_widget)

        self.opportunity_lists = {}
        self.phases = ["Contacto Inicial", "Calificación", "Propuesta", "Negociación", "Ganada", "Perdida"]

        self.load_kanban_board()

    def load_kanban_board(self):
        # Clear existing columns
        for i in reversed(range(self.kanban_columns_layout.count())):
            widget = self.kanban_columns_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        self.opportunity_lists.clear()

        for phase in self.phases:
            column_widget = QWidget()
            column_layout = QVBoxLayout(column_widget)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(2)

            column_title = QLabel(phase)
            column_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            column_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            column_layout.addWidget(column_title)

            opportunity_list = OpportunityListWidget(phase, self) # Custom QListWidget
            opportunity_list.setMinimumHeight(200)
            opportunity_list.setDragDropMode(QListWidget.DragDropMode.DropOnly)
            opportunity_list.setDefaultDropAction(Qt.DropAction.MoveAction)
            opportunity_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            opportunity_list.customContextMenuRequested.connect(lambda pos, pl=opportunity_list: self.show_opportunity_context_menu(pos, pl))
            opportunity_list.itemDoubleClicked.connect(self.edit_opportunity)
            opportunity_list.opportunity_dropped.connect(self.handle_opportunity_dropped)
            column_layout.addWidget(opportunity_list)
            self.opportunity_lists[phase] = opportunity_list

            self.kanban_columns_layout.addWidget(column_widget, 1)
        
        self.load_opportunities()

    def load_opportunities(self):
        for phase_list in self.opportunity_lists.values():
            phase_list.clear()

        opportunities = opportunities_manager.get_all_opportunities()
        for opportunity in opportunities:
            phase = opportunity['phase']
            if phase in self.opportunity_lists:
                item_text = f"{opportunity['title']} - {opportunity['amount'] or 'N/A'} {opportunity['currency'] or ''}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, opportunity['id']) # Store opportunity ID
                item.setData(Qt.ItemDataRole.UserRole + 1, opportunity['title']) # Store title for filtering
                item.setData(Qt.ItemDataRole.UserRole + 2, opportunity['requirement']) # Store requirement for filtering
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
                self.opportunity_lists[phase].addItem(item)
                self.apply_item_style(item, phase)

    def apply_item_style(self, item, phase):
        # Example styling based on phase or other criteria
        if phase == "Ganada":
            item.setBackground(QColor("#4CAF50")) # Green
        elif phase == "Perdida":
            item.setBackground(QColor("#F44336")) # Red
        elif phase == "Negociación":
            item.setBackground(QColor("#FFC107")) # Amber
        else:
            item.setBackground(QColor("#2196F3")) # Blue
        item.setForeground(QColor("#FFFFFF"))
        item.setFont(QFont("Segoe UI", 10))

    def filter_opportunities(self, text):
        search_text = text.lower()
        for phase_list in self.opportunity_lists.values():
            for i in range(phase_list.count()):
                item = phase_list.item(i)
                opportunity_title = item.data(Qt.ItemDataRole.UserRole + 1).lower()
                opportunity_requirement = item.data(Qt.ItemDataRole.UserRole + 2).lower() if item.data(Qt.ItemDataRole.UserRole + 2) else ""

                if search_text in opportunity_title or search_text in opportunity_requirement:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def handle_opportunity_dropped(self, opportunity_id, old_phase, new_phase):
        # Update the opportunity's phase in the database
        opportunity = opportunities_manager.get_opportunity_by_id(opportunity_id)
        if opportunity:
            opportunities_manager.update_opportunity(
                user_role="Comercial", # Assuming a commercial user role for this action
                opportunity_id=opportunity_id,
                title=opportunity['title'],
                requirement=opportunity['requirement'],
                conditions=opportunity['conditions'],
                amount=opportunity['amount'],
                currency=opportunity['currency'],
                status=opportunity['status'], # Keep existing status
                phase=new_phase,
                owner_user_id=opportunity['owner_user_id'],
                account_id=opportunity['account_id'],
                contact_id=opportunity['contact_id'],
                delivery_date=opportunity['delivery_date'],
                success_probability=opportunity['success_probability']
            )
            self.load_opportunities() # Reload all opportunities to reflect changes
            self.opportunity_updated.emit()

    def show_opportunity_context_menu(self, pos, list_widget):
        item = list_widget.itemAt(pos)
        if item:
            opportunity_id = item.data(Qt.ItemDataRole.UserRole)
            if opportunity_id is None: return

            menu = QMenu(self)

            edit_action = QAction("Editar Oportunidad", self)
            edit_action.triggered.connect(lambda: self.edit_opportunity(item))
            menu.addAction(edit_action)

            delete_action = QAction("Eliminar Oportunidad", self)
            delete_action.triggered.connect(lambda: self.delete_opportunity(opportunity_id))
            menu.addAction(delete_action)

            menu.exec(list_widget.mapToGlobal(pos))

    def edit_opportunity(self, item):
        opportunity_id = item.data(Qt.ItemDataRole.UserRole)
        if opportunity_id is None: return

        dialog = EditOpportunityDialog(opportunity_id, self)
        if dialog.exec():
            self.load_opportunities()
            self.opportunity_updated.emit()

    def delete_opportunity(self, opportunity_id):
        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     "¿Estás seguro de que quieres eliminar esta oportunidad?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            opportunities_manager.delete_opportunity("Comercial", opportunity_id)
            self.load_opportunities()
            self.opportunity_updated.emit()

class OpportunityListWidget(QListWidget):
    opportunity_dropped = Signal(int, str, str) # opportunity_id, old_phase, new_phase

    def __init__(self, phase_name, parent=None):
        super().__init__(parent)
        self.phase_name = phase_name
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            source_list = event.source()
            if isinstance(source_list, OpportunityListWidget):
                item = source_list.currentItem()
                if item:
                    opportunity_id = item.data(Qt.ItemDataRole.UserRole)
                    old_phase = source_list.phase_name
                    new_phase = self.phase_name

                    # Remove from old list
                    source_list.takeItem(source_list.row(item))
                    # Add to new list
                    self.addItem(item)
                    event.acceptProposedAction()
                    self.opportunity_dropped.emit(opportunity_id, old_phase, new_phase)
            else:
                event.ignore()
        else:
            event.ignore()
