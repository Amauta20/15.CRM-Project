from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QDialogButtonBox, QComboBox, QTextEdit
from app.opportunities.opportunities_manager import update_opportunity, get_opportunity_by_id
from app.data.accounts_manager import get_all_accounts
from app.data.contacts_manager import get_contacts_for_account

class EditOpportunityDialog(QDialog):
    def __init__(self, opportunity_id, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Editar Oportunidad")
        
        self.opportunity_id = opportunity_id
        
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

        self.phase_input = QComboBox()
        self.phases = ["Contacto Inicial", "Calificación", "Propuesta", "Negociación", "Ganada", "Perdida"]
        self.phase_input.addItems(self.phases)
        self.form_layout.addRow("Fase:", self.phase_input)
        
        self.layout.addLayout(self.form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout.addWidget(self.button_box)
        
        self.load_accounts()
        self.account_input.currentIndexChanged.connect(self.load_contacts_for_account)
        self.load_opportunity_data()
        
    def load_accounts(self):
        self.account_input.clear()
        accounts = get_all_accounts()
        for account in accounts:
            self.account_input.addItem(account['name'], userData=account['id'])

    def load_contacts_for_account(self, index):
        self.contact_input.clear()
        account_id = self.account_input.currentData()
        if account_id:
            contacts = get_contacts_for_account(account_id)
            for contact in contacts:
                self.contact_input.addItem(contact['name'], userData=contact['id'])

    def load_opportunity_data(self):
        opportunity = get_opportunity_by_id(self.opportunity_id)
        if opportunity:
            self.title_input.setText(opportunity['title'])
            self.requirement_input.setPlainText(opportunity['requirement'])
            self.amount_input.setText(str(opportunity['amount']))

            # Set selected account
            account_index = self.account_input.findData(opportunity['account_id'])
            if account_index != -1:
                self.account_input.setCurrentIndex(account_index)
                self.load_contacts_for_account(account_index) # Load contacts for the selected account

            # Set selected contact
            contact_index = self.contact_input.findData(opportunity['contact_id'])
            if contact_index != -1:
                self.contact_input.setCurrentIndex(contact_index)

            if opportunity['phase'] in self.phases:
                self.phase_input.setCurrentIndex(self.phases.index(opportunity['phase']))            
    def accept(self):
        title = self.title_input.text()
        requirement = self.requirement_input.toPlainText()
        amount = self.amount_input.text()
        phase = self.phase_input.currentText()
        account_id = self.account_input.currentData()
        contact_id = self.contact_input.currentData()
        
        if title:
            update_opportunity(
                user_role="Comercial", # This should be replaced with the actual user role
                opportunity_id=self.opportunity_id,
                title=title,
                requirement=requirement,
                amount=float(amount) if amount else None,
                phase=phase,
                account_id=account_id,
                contact_id=contact_id
            )
            super().accept()
