from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QMenu
from PyQt6.QtCore import pyqtSignal as Signal, Qt
from PyQt6.QtGui import QIcon, QAction
from app.messaging import service_manager
from app.ui.add_service_dialog import AddServiceDialog
from app.ui.edit_service_name_dialog import EditServiceNameDialog
from app.ui.select_service_dialog import SelectServiceDialog

class Sidebar(QWidget):
    service_selected = Signal(str, str) # Signal to emit URL and profile_path
    service_deleted = Signal(int) # Signal to emit service_id when a service is deleted
    show_notes_requested = Signal() # New signal to show NotesWidget
    show_kanban_requested = Signal() # New signal to show KanbanWidget
    show_checklist_requested = Signal() # New signal to show ChecklistWidget
    show_accounts_requested = Signal() # New signal to show AccountsWidget
    show_contacts_requested = Signal() # New signal to show ContactsWidget

    def __init__(self):
        super().__init__()
        self._unread_statuses = {} # {service_id: True/False}
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # --- Services Section ---
        self.services_title = QLabel("Servicios")
        self.layout.addWidget(self.services_title)

        self.add_service_button = QPushButton("Añadir Servicio")
        self.add_service_button.clicked.connect(self.open_select_service_dialog)
        self.layout.addWidget(self.add_service_button)

        # Container for service buttons
        self.services_container = QWidget()
        self.services_layout = QVBoxLayout(self.services_container)
        self.services_layout.setContentsMargins(0, 0, 0, 0)
        self.services_layout.setSpacing(5)
        self.layout.addWidget(self.services_container)

        self.load_services()

        self.layout.addStretch() # Push services to top

        # --- Productivity Tools Buttons ---
        self.notes_button = QPushButton("Notas")
        self.notes_button.clicked.connect(self.show_notes_requested.emit)
        self.layout.addWidget(self.notes_button)

        self.kanban_button = QPushButton("Kanban")
        self.kanban_button.clicked.connect(self.show_kanban_requested.emit)
        self.layout.addWidget(self.kanban_button)

        self.checklist_button = QPushButton("Checklist")
        self.checklist_button.clicked.connect(self.show_checklist_requested.emit)
        self.layout.addWidget(self.checklist_button)

        self.accounts_button = QPushButton("Cuentas")
        self.accounts_button.clicked.connect(self.show_accounts_requested.emit)
        self.layout.addWidget(self.accounts_button)

        self.contacts_button = QPushButton("Contactos")
        self.contacts_button.clicked.connect(self.show_contacts_requested.emit)
        self.layout.addWidget(self.contacts_button)

    # --- Service Management Methods ---
    def open_select_service_dialog(self):
        dialog = SelectServiceDialog(self)
        dialog.catalog_service_selected.connect(self._add_catalog_service)
        dialog.custom_service_requested.connect(self._add_custom_service)
        dialog.exec()

    def _add_catalog_service(self, name, url, icon):
        service_manager.add_service(name, url, icon)
        self.load_services() # Refresh the service list

    def _add_custom_service(self):
        dialog = AddServiceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, url, icon = dialog.get_service_data()
            if name and url:
                service_manager.add_service(name, url, icon)
                self.load_services() # Refresh the service list

    def load_services(self):
        # Clear existing service buttons from the dedicated layout
        while self.services_layout.count():
            child = self.services_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        services = service_manager.get_user_services()

        self._unread_statuses = {s['id']: self._unread_statuses.get(s['id'], False) for s in services} # Preserve existing unread statuses

        for service in services:
            btn = QPushButton(service['name'])
            btn.setProperty('service_id', service['id']) # Store service_id in button property
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, b=btn: self.show_service_context_menu(pos, b))

            # Apply unread style if applicable
            if self._unread_statuses.get(service['id'], False):
                btn.setProperty('class', 'unread') # Apply CSS class

            url = service['url']
            profile_path = service['profile_path']
            btn.clicked.connect(lambda checked=False, u=url, p=profile_path: self.service_selected.emit(u, p))
            self.services_layout.addWidget(btn)

    def show_service_context_menu(self, pos, button):
        service_id = button.property('service_id')
        if service_id is None: return

        menu = QMenu(self)

        add_instance_action = QAction("Añadir Otra Instancia", self)
        add_instance_action.triggered.connect(lambda checked, s_id=service_id: self.add_another_instance_from_ui(s_id))
        menu.addAction(add_instance_action)

        edit_action = QAction("Editar Nombre del Servicio", self)
        edit_action.triggered.connect(lambda checked, s_id=service_id: self.edit_service_name_from_ui(s_id))
        menu.addAction(edit_action)

        delete_action = QAction("Eliminar Servicio", self)
        delete_action.triggered.connect(lambda checked, s_id=service_id: self.delete_service_from_ui(s_id))
        menu.addAction(delete_action)

        menu.exec(button.mapToGlobal(pos))

    def add_another_instance_from_ui(self, service_id):
        service_details = service_manager.get_service_by_id(service_id)
        if not service_details: return

        suggested_name = f"{service_details['name']} (Nueva Instancia)"
        dialog = AddServiceDialog(suggested_name, service_details['url'], service_details['icon'], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, url, icon = dialog.get_service_data()
            if name and url:
                service_manager.add_service(name, url, icon)
                self.load_services() # Refresh the service list

    def edit_service_name_from_ui(self, service_id):
        service_details = service_manager.get_service_by_id(service_id)
        if not service_details: return

        dialog = EditServiceNameDialog(service_details['name'], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_new_name()
            if new_name and new_name != service_details['name']:
                service_manager.update_service_name(service_id, new_name)
                self.load_services() # Refresh the service list

    def delete_service_from_ui(self, service_id):
        service_manager.delete_service(service_id)
        self.load_services() # Refresh the service list
        self.service_deleted.emit(service_id) # Notify MainWindow to remove webview

    def set_service_unread_status(self, service_id, has_unread):
        if service_id in self._unread_statuses:
            self._unread_statuses[service_id] = has_unread
            self.load_services() # Refresh UI to apply/remove unread style
