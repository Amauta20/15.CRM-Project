
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from app.drive.drive_manager import upload_file
from app.opportunities.opportunities_manager import update_opportunity_proposal_path

class UploadProposalDialog(QDialog):
    def __init__(self, opportunity_id, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Subir Propuesta")
        
        self.opportunity_id = opportunity_id
        self.file_path = None
        
        self.layout = QVBoxLayout(self)
        
        self.select_file_button = QPushButton("Seleccionar Archivo")
        self.select_file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_file_button)
        
        self.upload_button = QPushButton("Subir")
        self.upload_button.clicked.connect(self.upload)
        self.upload_button.setEnabled(False)
        self.layout.addWidget(self.upload_button)
        
    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo de Propuesta")
        if self.file_path:
            self.upload_button.setEnabled(True)
            
    def upload(self):
        if self.file_path:
            try:
                proposal_path, drive_folder_id = upload_file(self.opportunity_id, self.file_path)
                update_opportunity_proposal_path(self.opportunity_id, proposal_path, drive_folder_id)
                QMessageBox.information(self, "Éxito", "¡Propuesta subida exitosamente!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al subir la propuesta: {e}")

