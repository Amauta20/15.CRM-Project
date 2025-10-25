from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QDialogButtonBox, QDateEdit, QSpinBox, QComboBox, QTextEdit, QCheckBox
from app.opportunities.opportunities_manager import add_opportunity
from app.data.accounts_manager import get_all_accounts
from app.data.contacts_manager import get_contacts_for_account
from PyQt6.QtCore import QDate

class AddOpportunityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Añadir Oportunidad")
        
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.form_layout.addRow("Título:", self.title_input)
        
        self.requirement_input = QTextEdit()
        self.form_layout.addRow("Requerimiento:", self.requirement_input)
        
        self.amount_input = QLineEdit()
        self.form_layout.addRow("Monto:", self.amount_input)

        self.account_input = QComboBox()
        self.form_layout.addRow("Cuenta:", self.account_input)

        self.contact_input = QComboBox()
        self.form_layout.addRow("Contacto:", self.contact_input)

        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setDate(QDate.currentDate())
        self.form_layout.addRow("Fecha de Entrega:", self.delivery_date_input)

        self.success_probability_input = QSpinBox()
        self.success_probability_input.setRange(0, 100)
        self.success_probability_input.setSuffix("%")
        self.form_layout.addRow("Probabilidad de Éxito:", self.success_probability_input)

        self.phase_input = QComboBox()
        self.phase_input.addItems(["Contacto Inicial", "Calificación", "Propuesta", "Negociación", "Ganada", "Perdida"])
        self.form_layout.addRow("Fase:", self.phase_input)

        self.status_checkbox = QCheckBox("Activa")
        self.status_checkbox.setChecked(True)
        self.form_layout.addRow("Estado:", self.status_checkbox)
        
        self.layout.addLayout(self.form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout.addWidget(self.button_box)

        self.load_accounts()
        self.account_input.currentIndexChanged.connect(self.load_contacts_for_account)

    def load_accounts(self):
        self.account_input.clear()
        accounts = get_all_accounts()
        for account in accounts:
            self.account_input.addItem(account['name'], userData=account['id'])
        self.load_contacts_for_account(0) # Load contacts for the initially selected account

    def load_contacts_for_account(self, index):
        self.contact_input.clear()
        account_id = self.account_input.currentData()
        if account_id:
            contacts = get_contacts_for_account(account_id)
            for contact in contacts:
                self.contact_input.addItem(contact['name'], userData=contact['id'])
    def accept(self):
        title = self.title_input.text()
        requirement = self.requirement_input.toPlainText()
        amount = self.amount_input.text()
        account_id = self.account_input.currentData()
        contact_id = self.contact_input.currentData()
        delivery_date = self.delivery_date_input.date().toString("yyyy-MM-dd")
        success_probability = self.success_probability_input.value()
        phase = self.phase_input.currentText()
        status = "Activa" if self.status_checkbox.isChecked() else "Inactiva"
        
        if title:
            add_opportunity(
                user_role="Comercial", # This should be replaced with the actual user role
                title=title,
                requirement=requirement,
                amount=float(amount) if amount else None,
                account_id=account_id,
                contact_id=contact_id,
                delivery_date=delivery_date,
                success_probability=success_probability,
                phase=phase,
                status=status
            )
            super().accept()
