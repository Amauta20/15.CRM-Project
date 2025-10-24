from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QCheckBox
from app.data import accounts_manager
from PyQt6.QtCore import Qt
from app.data import contacts_manager

class EditContactDialog(QDialog):
    def __init__(self, contact_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Contacto: {contact_data['name']}")
        self.contact_data = contact_data
        self.init_ui()
        self.load_contact_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.load_accounts()

    def load_accounts(self):
        self.account_combo.clear()
        self.account_combo.addItem("Ninguna", None) # Option for no account
        accounts = accounts_manager.get_all_accounts()
        for account in accounts:
            self.account_combo.addItem(account["name"], account["id"])

        # Name
        self.name_label = QLabel("Nombre del Contacto:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        # Email
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)

        # Phone
        self.phone_label = QLabel("Teléfono:")
        self.phone_input = QLineEdit()
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_input)

        # Referred By
        self.referred_by_label = QLabel("Referido por:")
        self.referred_by_input = QLineEdit()
        self.layout.addWidget(self.referred_by_label)
        self.layout.addWidget(self.referred_by_input)

        # Account
        self.account_label = QLabel("Cuenta:")
        self.account_combo = QComboBox()
        self.layout.addWidget(self.account_label)
        self.layout.addWidget(self.account_combo)

        # Confirmed
        self.confirmed_checkbox = QCheckBox("Confirmado")
        self.layout.addWidget(self.confirmed_checkbox)

        # Notes
        self.notes_label = QLabel("Notas:")
        self.notes_input = QTextEdit()
        self.layout.addWidget(self.notes_label)
        self.layout.addWidget(self.notes_input)

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

    def load_contact_data(self):
        self.name_input.setText(self.contact_data["name"])
        self.email_input.setText(self.contact_data["email"] or "")
        self.phone_input.setText(self.contact_data["phone"] or "")
        self.referred_by_input.setText(self.contact_data["referred_by"] or "")
        self.notes_input.setPlainText(self.contact_data["notes"] or "")
        self.confirmed_checkbox.setChecked(self.contact_data["confirmed"] == 1)

        # Set current account
        accounts = contacts_manager.get_accounts_for_contact(self.contact_data["id"])
        if accounts:
            account_id = accounts[0]["id"]
            index = self.account_combo.findData(account_id)
            if index != -1:
                self.account_combo.setCurrentIndex(index)

    def get_contact_data(self):
        return (
            self.name_input.text().strip(),
            self.email_input.text().strip() if self.email_input.text().strip() else None,
            self.phone_input.text().strip() if self.phone_input.text().strip() else None,
            self.notes_input.toPlainText().strip() if self.notes_input.toPlainText().strip() else None,
            self.referred_by_input.text().strip() if self.referred_by_input.text().strip() else None,
            1 if self.confirmed_checkbox.isChecked() else 0,
            self.account_combo.currentData()
        )