from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox

class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nueva Cuenta")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Name
        self.name_label = QLabel("Nombre de la Cuenta:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        # Company
        self.company_label = QLabel("Empresa:")
        self.company_input = QLineEdit()
        self.layout.addWidget(self.company_label)
        self.layout.addWidget(self.company_input)

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

        # Address
        self.address_label = QLabel("Dirección:")
        self.address_input = QLineEdit()
        self.layout.addWidget(self.address_label)
        self.layout.addWidget(self.address_input)

        # Referred By
        self.referred_by_label = QLabel("Referido por:")
        self.referred_by_input = QLineEdit()
        self.layout.addWidget(self.referred_by_label)
        self.layout.addWidget(self.referred_by_input)

        # Classification
        self.classification_label = QLabel("Clasificación:")
        self.classification_combo = QComboBox()
        self.classification_combo.addItems(["Lead", "Cliente"])
        self.classification_combo.currentTextChanged.connect(self.update_status_options)
        self.layout.addWidget(self.classification_label)
        self.layout.addWidget(self.classification_combo)

        # Status
        self.status_label = QLabel("Estado:")
        self.status_combo = QComboBox()
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.status_combo)
        self.update_status_options("Lead")


        # Notes
        self.notes_label = QLabel("Notas:")
        self.notes_input = QTextEdit()
        self.layout.addWidget(self.notes_label)
        self.layout.addWidget(self.notes_input)

        # Buttons
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

    def update_status_options(self, text):
        self.status_combo.clear()
        if text == "Lead":
            self.status_combo.addItems(["Por contactar", "Contactado", "Calificado", "No calificado"])
        else:
            self.status_combo.addItems(["Activo", "Inactivo"])

    def get_account_data(self):
        return (
            self.name_input.text().strip(),
            self.company_input.text().strip() if self.company_input.text().strip() else None,
            self.email_input.text().strip() if self.email_input.text().strip() else None,
            self.phone_input.text().strip() if self.phone_input.text().strip() else None,
            self.address_input.text().strip() if self.address_input.text().strip() else None,
            self.notes_input.toPlainText().strip() if self.notes_input.toPlainText().strip() else None,
            self.referred_by_input.text().strip() if self.referred_by_input.text().strip() else None,
            self.classification_combo.currentText(),
            self.status_combo.currentText()
        )
