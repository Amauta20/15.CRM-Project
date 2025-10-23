from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QDialog, QComboBox
from PyQt6.QtCore import Qt
from app.data import contacts_manager
from app.ui.add_contact_dialog import AddContactDialog
from app.ui.edit_contact_dialog import EditContactDialog
from PyQt6.QtGui import QIcon
from app.data import settings_manager
import qtawesome as qta
from datetime import datetime

class ContactsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_contacts()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Añadir Contacto")
        self.add_button.clicked.connect(self.add_contact)
        self.buttons_layout.addWidget(self.add_button)

        self.restore_button = QPushButton("Restaurar Contacto")
        self.restore_button.clicked.connect(self.restore_contact_from_selection)
        self.restore_button.hide()
        self.buttons_layout.addWidget(self.restore_button)

        self.show_deleted_checkbox = QCheckBox("Mostrar eliminados")
        self.show_deleted_checkbox.stateChanged.connect(self.toggle_deleted)
        self.buttons_layout.addWidget(self.show_deleted_checkbox)

        self.layout.addLayout(self.buttons_layout)

        # Table for contacts
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(11)
        self.contacts_table.setHorizontalHeaderLabels(["ID", "Nombre", "Empresa", "Email", "Teléfono", "Confirmado", "Notas", "Referido por", "Cuenta", "Creado", "Acciones"])
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.contacts_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.contacts_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.contacts_table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.contacts_table)

    def toggle_deleted(self, state):
        if state == Qt.CheckState.Checked.value:
            self.restore_button.show()
        else:
            self.restore_button.hide()
        self.load_contacts()

    def load_contacts(self):
        self.contacts_table.setRowCount(0)
        if self.show_deleted_checkbox.isChecked():
            contacts = contacts_manager.get_deleted_contacts()
        else:
            contacts = contacts_manager.get_all_contacts(include_deleted=False)
        datetime_format = settings_manager.get_datetime_format()
        for row_num, contact in enumerate(contacts):
            self.contacts_table.insertRow(row_num)
            self.contacts_table.setItem(row_num, 0, QTableWidgetItem(str(contact["id"])))
            self.contacts_table.setItem(row_num, 1, QTableWidgetItem(contact["name"]))
            self.contacts_table.setItem(row_num, 2, QTableWidgetItem(contact["company"] or ""))
            self.contacts_table.setItem(row_num, 3, QTableWidgetItem(contact["email"] or ""))
            self.contacts_table.setItem(row_num, 4, QTableWidgetItem(contact["phone"] or ""))
            confirmed_item = QTableWidgetItem()
            confirmed_item.setCheckState(Qt.CheckState.Checked if contact["confirmed"] else Qt.CheckState.Unchecked)
            self.contacts_table.setItem(row_num, 5, confirmed_item)
            self.contacts_table.setItem(row_num, 6, QTableWidgetItem(contact["notes"] or ""))
            self.contacts_table.setItem(row_num, 7, QTableWidgetItem(contact["referred_by"] or ""))

            # Display associated account
            accounts = contacts_manager.get_accounts_for_contact(contact["id"])
            account_names = ", ".join([acc["name"] for acc in accounts])
            self.contacts_table.setItem(row_num, 8, QTableWidgetItem(account_names))

            created_at = datetime.fromisoformat(contact["created_at"]).strftime(datetime_format)
            self.contacts_table.setItem(row_num, 9, QTableWidgetItem(created_at))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_button = QPushButton()
            edit_button.setIcon(qta.icon('fa5s.pencil-alt', color='white'))  # Font Awesome edit icon
            edit_button.setToolTip("Editar")
            edit_button.clicked.connect(lambda _, r=contact["id"]: self.edit_contact(r))
            actions_layout.addWidget(edit_button)

            delete_button = QPushButton()
            delete_button.setIcon(qta.icon('fa5s.trash-alt', color='white'))  # Font Awesome delete icon
            delete_button.setToolTip("Eliminar")
            delete_button.clicked.connect(lambda _, r=contact["id"]: self.delete_contact(r))
            actions_layout.addWidget(delete_button)
            
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.contacts_table.setCellWidget(row_num, 10, actions_widget)




    def on_selection_changed(self):
        has_selection = len(self.contacts_table.selectedItems()) > 0
        self.restore_button.setEnabled(has_selection and self.show_deleted_checkbox.isChecked())

    def get_selected_contact_id(self):
        selected_rows = self.contacts_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            return int(self.contacts_table.item(row, 0).text())
        return None

    def add_contact(self):
        dialog = AddContactDialog(self)
        if dialog.exec():
            name, company, email, phone, notes, referred_by, confirmed, account_id = dialog.get_contact_data()
            if name:
                try:
                    contacts_manager.add_contact(name, company, email, phone, notes, referred_by, confirmed, account_id, user_role="Comercial")
                    self.load_contacts()
                except PermissionError as e:
                    QMessageBox.warning(self, "Permiso Denegado", str(e))
            else:
                QMessageBox.warning(self, "Advertencia", "El nombre del contacto no puede estar vacío.")

    def edit_contact(self, contact_id):
        contact = contacts_manager.get_contact_by_id(contact_id)
        if contact:
            dialog = EditContactDialog(contact, self)
            if dialog.exec():
                name, company, email, phone, notes, referred_by, confirmed, account_id = dialog.get_contact_data()
                if name:
                    try:
                        contacts_manager.update_contact(contact_id, name, company, email, phone, notes, referred_by, confirmed, account_id, user_role="Comercial")
                        self.load_contacts()
                    except PermissionError as e:
                        QMessageBox.warning(self, "Permiso Denegado", str(e))
                else:
                    QMessageBox.warning(self, "Advertencia", "El nombre del contacto no puede estar vacío.")

    def delete_contact(self, contact_id):
        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     "¿Estás seguro de que quieres eliminar este contacto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                contacts_manager.delete_contact(contact_id, deleted_by_user_id=1, user_role="Comercial") # Placeholder user ID
                self.load_contacts()
            except PermissionError as e:
                QMessageBox.warning(self, "Permiso Denegado", str(e))

    def restore_contact(self, contact_id):
        reply = QMessageBox.question(self, "Confirmar Restauración",
                                     "¿Estás seguro de que quieres restaurar este contacto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                contacts_manager.restore_contact(contact_id, user_role="Comercial")
                self.load_contacts()
            except PermissionError as e:
                QMessageBox.warning(self, "Permiso Denegado", str(e))

    def restore_contact_from_selection(self):
        contact_id = self.get_selected_contact_id()
        if contact_id:
            self.restore_contact(contact_id)
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un contacto para restaurar.")
