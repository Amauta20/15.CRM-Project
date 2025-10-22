from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QDialog, QComboBox
from PyQt6.QtCore import Qt
from app.data import accounts_manager
from app.ui.add_account_dialog import AddAccountDialog
from app.ui.edit_account_dialog import EditAccountDialog
from PyQt6.QtGui import QIcon
from app.data import settings_manager
import qtawesome as qta
from datetime import datetime

class AccountsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_accounts()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Añadir Cuenta")
        self.add_button.clicked.connect(self.add_account)
        self.buttons_layout.addWidget(self.add_button)

        self.restore_button = QPushButton("Restaurar Cuenta")
        self.restore_button.clicked.connect(self.restore_account_from_selection)
        self.restore_button.hide()
        self.buttons_layout.addWidget(self.restore_button)

        self.show_deleted_checkbox = QCheckBox("Mostrar eliminados")
        self.show_deleted_checkbox.stateChanged.connect(self.toggle_deleted)
        self.buttons_layout.addWidget(self.show_deleted_checkbox)

        self.layout.addLayout(self.buttons_layout)

        # Table for accounts
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(12)
        self.accounts_table.setHorizontalHeaderLabels(["ID", "Nombre", "Empresa", "Email", "Teléfono", "Dirección", "Notas", "Referido por", "Clasificación", "Estado", "Creado", "Acciones"])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.accounts_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.accounts_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.accounts_table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.accounts_table)

    def toggle_deleted(self, state):
        if state == Qt.CheckState.Checked.value:
            self.restore_button.show()
        else:
            self.restore_button.hide()
        self.load_accounts()

    def load_accounts(self):
        self.accounts_table.setRowCount(0)
        if self.show_deleted_checkbox.isChecked():
            accounts = accounts_manager.get_deleted_accounts()
        else:
            accounts = accounts_manager.get_all_accounts(include_deleted=False)
        datetime_format = settings_manager.get_datetime_format()
        for row_num, account in enumerate(accounts):
            self.accounts_table.insertRow(row_num)
            self.accounts_table.setItem(row_num, 0, QTableWidgetItem(str(account["id"])))
            self.accounts_table.setItem(row_num, 1, QTableWidgetItem(account["name"]))
            self.accounts_table.setItem(row_num, 2, QTableWidgetItem(account["company"] or ""))
            self.accounts_table.setItem(row_num, 3, QTableWidgetItem(account["email"] or ""))
            self.accounts_table.setItem(row_num, 4, QTableWidgetItem(account["phone"] or ""))
            self.accounts_table.setItem(row_num, 5, QTableWidgetItem(account["address"] or ""))
            self.accounts_table.setItem(row_num, 6, QTableWidgetItem(account["notes"] or ""))
            self.accounts_table.setItem(row_num, 7, QTableWidgetItem(account["referred_by"] or ""))

            # Classification ComboBox
            classification_combo = QComboBox()
            classification_combo.addItems(["Lead", "Cliente"])
            classification_combo.setCurrentText(account["classification"])
            classification_combo.currentTextChanged.connect(lambda text, row=row_num: self.update_account_classification_and_status(row))
            self.accounts_table.setCellWidget(row_num, 8, classification_combo)

            # Status ComboBox
            status_combo = QComboBox()
            if account["classification"] == "Lead":
                status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
            else:
                status_combo.addItems(["Activo", "Inactivo"])
            status_combo.setCurrentText(account["status"])
            status_combo.currentTextChanged.connect(lambda text, row=row_num: self.update_account_classification_and_status(row))
            self.accounts_table.setCellWidget(row_num, 9, status_combo)

            created_at = datetime.fromisoformat(account["created_at"]).strftime(datetime_format)
            self.accounts_table.setItem(row_num, 10, QTableWidgetItem(created_at))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_button = QPushButton()
            edit_button.setIcon(qta.icon('fa5s.pencil-alt', color='white'))  # Font Awesome edit icon
            edit_button.setToolTip("Editar")
            edit_button.clicked.connect(lambda _, r=account["id"]: self.edit_account(r))
            actions_layout.addWidget(edit_button)

            delete_button = QPushButton()
            delete_button.setIcon(qta.icon('fa5s.trash-alt', color='white'))  # Font Awesome delete icon
            delete_button.setToolTip("Eliminar")
            delete_button.clicked.connect(lambda _, r=account["id"]: self.delete_account(r))
            actions_layout.addWidget(delete_button)
            
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.accounts_table.setCellWidget(row_num, 11, actions_widget)

    def update_account_classification_and_status(self, row):
        account_id = int(self.accounts_table.item(row, 0).text())
        classification_combo = self.accounts_table.cellWidget(row, 7)
        status_combo = self.accounts_table.cellWidget(row, 8)
        classification = classification_combo.currentText()
        status = status_combo.currentText()

        # Update status options based on classification
        if classification == "Lead":
            status_combo.clear()
            status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
        else:
            status_combo.clear()
            status_combo.addItems(["Activo", "Inactivo"])

        # Get current account data to pass to update_account
        account = accounts_manager.get_account_by_id(account_id)
        
        accounts_manager.update_account(
            account_id,
            account['name'],
            account['company'],
            account['email'],
            account['phone'],
            account['address'],
            account['notes'],
            account['referred_by'],
            classification,
            status,
            user_role="Comercial"
        )


    def on_selection_changed(self):
        has_selection = len(self.accounts_table.selectedItems()) > 0
        self.restore_button.setEnabled(has_selection and self.show_deleted_checkbox.isChecked())

    def get_selected_account_id(self):
        selected_rows = self.accounts_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            return int(self.accounts_table.item(row, 0).text())
        return None

    def add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec():
            name, company, email, phone, address, notes, referred_by, classification, status = dialog.get_account_data()
            if name:
                try:
                    accounts_manager.add_account(name, company, email, phone, address, notes, referred_by, "Comercial", classification, status)
                    self.load_accounts()
                except PermissionError as e:
                    QMessageBox.warning(self, "Permiso Denegado", str(e))
            else:
                QMessageBox.warning(self, "Advertencia", "El nombre de la cuenta no puede estar vacío.")

    def edit_account(self, account_id):
        account = accounts_manager.get_account_by_id(account_id)
        if account:
            dialog = EditAccountDialog(account, self)
            if dialog.exec():
                name, company, email, phone, address, notes, referred_by, classification, status = dialog.get_account_data()
                if name:
                    try:
                        accounts_manager.update_account(account_id, name, company, email, phone, address, notes, referred_by, classification, status, user_role="Comercial")
                        self.load_accounts()
                    except PermissionError as e:
                        QMessageBox.warning(self, "Permiso Denegado", str(e))
                else:
                    QMessageBox.warning(self, "Advertencia", "El nombre de la cuenta no puede estar vacío.")

    def delete_account(self, account_id):
        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     "¿Estás seguro de que quieres eliminar esta cuenta?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                accounts_manager.delete_account(account_id, deleted_by_user_id=1, user_role="Comercial") # Placeholder user ID
                self.load_accounts()
            except PermissionError as e:
                QMessageBox.warning(self, "Permiso Denegado", str(e))

    def restore_account(self, account_id):
        reply = QMessageBox.question(self, "Confirmar Restauración",
                                     "¿Estás seguro de que quieres restaurar esta cuenta?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                accounts_manager.restore_account(account_id, user_role="Comercial")
                self.load_accounts()
            except PermissionError as e:
                QMessageBox.warning(self, "Permiso Denegado", str(e))

    def restore_account_from_selection(self):
        account_id = self.get_selected_account_id()
        if account_id:
            self.restore_account(account_id)
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una cuenta para restaurar.")
