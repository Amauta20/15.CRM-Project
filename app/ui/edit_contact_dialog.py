from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt

class EditContactDialog(QDialog):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("Editar Contacto")
        self.init_ui()
        self.load_contact_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del Contacto")
        self.form_layout.addRow("Nombre:", self.name_input)

        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Empresa")
        self.form_layout.addRow("Empresa:", self.company_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.form_layout.addRow("Email:", self.email_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Teléfono")
        self.form_layout.addRow("Teléfono:", self.phone_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Dirección")
        self.form_layout.addRow("Dirección:", self.address_input)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Notas")
        self.form_layout.addRow("Notas:", self.notes_input)

        self.referred_by_input = QLineEdit()
        self.referred_by_input.setPlaceholderText("Referido por")
        self.form_layout.addRow("Referido por:", self.referred_by_input)

        self.classification_combo = QComboBox()
        self.classification_combo.addItems(["Lead", "Cliente"])
        self.form_layout.addRow("Clasificación:", self.classification_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
        self.form_layout.addRow("Estado:", self.status_combo)

        self.classification_combo.currentTextChanged.connect(self.update_status_options)

        self.layout.addLayout(self.form_layout)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

    def load_contact_data(self):
        self.name_input.setText(self.contact["name"])
        self.company_input.setText(self.contact["company"])
        self.email_input.setText(self.contact["email"])
        self.phone_input.setText(self.contact["phone"])
        self.address_input.setText(self.contact["address"])
        self.notes_input.setText(self.contact["notes"])
        self.referred_by_input.setText(self.contact["referred_by"])
        self.classification_combo.setCurrentText(self.contact["classification"])
        self.update_status_options(self.contact["classification"])
        self.status_combo.setCurrentText(self.contact["status"])

    def update_status_options(self, classification):
        self.status_combo.clear()
        if classification == "Lead":
            self.status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
        else:
            self.status_combo.addItems(["Activo", "Inactivo"])

    def get_contact_data(self):
        return (
            self.name_input.text(),
            self.company_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.notes_input.text(),
            self.referred_by_input.text(),
            self.classification_combo.currentText(),
            self.status_combo.currentText()
        )
