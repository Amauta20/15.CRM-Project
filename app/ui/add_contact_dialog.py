from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QDialog, QComboBox, QLabel
from PyQt6.QtCore import Qt
from app.data import contacts_manager
from app.ui.add_contact_dialog import AddContactDialog
from app.ui.edit_contact_dialog import EditContactDialog
from PyQt6.QtGui import QIcon
from app.data import settings_manager
from datetime import datetime
import qtawesome as qta

class ContactsWidget(QWidget):
    def __init__(self):
        super().__init__()
        print("ContactsWidget: __init__ called")
        self.init_ui()
        self.load_contacts()

    def init_ui(self):
        print("ContactsWidget: init_ui called")
        self.layout = QVBoxLayout(self)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Añadir Contacto")
        self.add_button.setIcon(qta.icon('fa5s.user-plus', color='white'))
        self.add_button.clicked.connect(self.add_contact)
        self.buttons_layout.addWidget(self.add_button)

        self.restore_button = QPushButton("Restaurar Contacto")
        self.restore_button.setIcon(qta.icon('fa5s.undo', color='white'))
        self.restore_button.clicked.connect(self.restore_contact_from_selection)
        self.restore_button.hide()
        self.buttons_layout.addWidget(self.restore_button)

        self.show_deleted_checkbox = QCheckBox("Mostrar eliminados")
        self.show_deleted_checkbox.stateChanged.connect(self.toggle_deleted)
        self.buttons_layout.addWidget(self.show_deleted_checkbox)

        self.layout.addLayout(self.buttons_layout)

        # Table for contacts
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(12)
        self.contacts_table.setHorizontalHeaderLabels(["ID", "Nombre", "Empresa", "Email", "Teléfono", "Dirección", "Notas", "Referido por", "Clasificación", "Estado", "Creado", "Acciones"])
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
        print("ContactsWidget: load_contacts called")
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
            self.contacts_table.setItem(row_num, 5, QTableWidgetItem(contact["address"] or ""))
            self.contacts_table.setItem(row_num, 6, QTableWidgetItem(contact["notes"] or ""))
            self.contacts_table.setItem(row_num, 7, QTableWidgetItem(contact["referred_by"] or ""))

            # Classification ComboBox
            classification_combo = QComboBox()
            classification_combo.addItems(["Lead", "Cliente"])
            classification_combo.setCurrentText(contact["classification"])
            classification_combo.currentTextChanged.connect(lambda text, row=row_num: self.update_contact_classification_and_status(row))
            self.contacts_table.setCellWidget(row_num, 8, classification_combo)

            # Status ComboBox
            status_combo = QComboBox()
            if contact["classification"] == "Lead":
                status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
            else:
                status_combo.addItems(["Activo", "Inactivo"])
            status_combo.setCurrentText(contact["status"])
            status_combo.currentTextChanged.connect(lambda text, row=row_num: self.update_contact_classification_and_status(row))
            self.contacts_table.setCellWidget(row_num, 9, status_combo)

            created_at = datetime.fromisoformat(contact["created_at"]).strftime(datetime_format)
            self.contacts_table.setItem(row_num, 10, QTableWidgetItem(created_at))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_button = QPushButton()
            edit_button.setIcon(qta.icon('fa5s.pencil-alt', color='white'))
            edit_button.setToolTip("Editar")
            edit_button.clicked.connect(lambda _, r=contact["id"]: self.edit_contact(r))
            actions_layout.addWidget(edit_button)

            delete_button = QPushButton()
            delete_button.setIcon(qta.icon('fa5s.trash-alt', color='white'))
            delete_button.setToolTip("Eliminar")
            delete_button.clicked.connect(lambda _, r=contact["id"]: self.delete_contact(r))
            actions_layout.addWidget(delete_button)
            
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.contacts_table.setCellWidget(row_num, 11, actions_widget)

    def update_contact_classification_and_status(self, row):
        contact_id = int(self.contacts_table.item(row, 0).text())
        classification_combo = self.contacts_table.cellWidget(row, 7)
        status_combo = self.contacts_table.cellWidget(row, 8)
        classification = classification_combo.currentText()
        status = status_combo.currentText()

        # Update status options based on classification
        if classification == "Lead":
            status_combo.clear()
            status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
        else:
            status_combo.clear()
            status_combo.addItems(["Activo", "Inactivo"])

        # Get current contact data to pass to update_contact
        contact = contacts_manager.get_contact_by_id(contact_id)
        
        contacts_manager.update_contact(
            contact_id,
            contact['name'],
            contact['company'],
            contact['email'],
            contact['phone'],
            contact['address'],
            contact['notes'],
            contact['referred_by'],
            classification,
            status,
            user_role="Comercial"
        )


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
            name, company, email, phone, address, notes, referred_by, classification, status = dialog.get_contact_data()
            if name:
                try:
                    contacts_manager.add_contact(name, company, email, phone, address, notes, referred_by, classification, status)
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
                name, company, email, phone, address, notes, referred_by, classification, status = dialog.get_contact_data()
                if name:
                    try:
                        contacts_manager.update_contact(contact_id, name, company, email, phone, address, notes, referred_by, classification, status, user_role="Comercial")
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