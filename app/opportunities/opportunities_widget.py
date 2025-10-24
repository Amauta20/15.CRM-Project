from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
from .opportunities_manager import get_all_opportunities, get_opportunity_by_id
from .add_opportunity_dialog import AddOpportunityDialog
from .edit_opportunity_dialog import EditOpportunityDialog
from .upload_proposal_dialog import UploadProposalDialog
from app.utils.report_utils import generate_proposal_document
import os
import datetime
from app.data.database import get_app_data_dir

class OpportunitiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("Módulo de Oportunidades")
        self.layout.addWidget(self.label)
        
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Añadir Oportunidad")
        self.add_button.clicked.connect(self.open_add_opportunity_dialog)
        self.button_layout.addWidget(self.add_button)

        self.upload_proposal_button = QPushButton("Subir Propuesta")
        self.upload_proposal_button.clicked.connect(self.open_upload_proposal_dialog)
        self.upload_proposal_button.setEnabled(False)
        self.button_layout.addWidget(self.upload_proposal_button)

        self.view_proposal_button = QPushButton("Ver Propuesta")
        self.view_proposal_button.clicked.connect(self.view_proposal)
        self.view_proposal_button.setEnabled(False)
        self.button_layout.addWidget(self.view_proposal_button)

        self.generate_proposal_button = QPushButton("Generar Propuesta")
        self.generate_proposal_button.clicked.connect(self.generate_proposal_for_opportunity)
        self.generate_proposal_button.setEnabled(False)
        self.button_layout.addWidget(self.generate_proposal_button)

        self.layout.addLayout(self.button_layout)
        
        self.opportunities_list = QListWidget()
        self.opportunities_list.itemDoubleClicked.connect(self.open_edit_opportunity_dialog)
        self.opportunities_list.itemSelectionChanged.connect(self.update_button_states)
        self.layout.addWidget(self.opportunities_list)
        
        self.load_opportunities()
        
    def load_opportunities(self):
        self.opportunities_list.clear()
        opportunities = get_all_opportunities()
        for opportunity in opportunities:
            item_text = f"{opportunity['title']} - {opportunity['phase']}"
            item = QListWidgetItem(item_text)
            item.setData(1, opportunity['id']) # Store the id in the item's data
            self.opportunities_list.addItem(item)
            
    def open_add_opportunity_dialog(self):
        dialog = AddOpportunityDialog(self)
        if dialog.exec():
            self.load_opportunities()

    def open_edit_opportunity_dialog(self, item):
        opportunity_id = item.data(1)
        dialog = EditOpportunityDialog(opportunity_id, self)
        if dialog.exec():
            self.load_opportunities()

    def open_upload_proposal_dialog(self):
        selected_item = self.opportunities_list.currentItem()
        if selected_item:
            opportunity_id = selected_item.data(1)
            dialog = UploadProposalDialog(opportunity_id, self)
            if dialog.exec():
                self.load_opportunities()

    def view_proposal(self):
        selected_item = self.opportunities_list.currentItem()
        if selected_item:
            opportunity_id = selected_item.data(1)
            opportunity = get_opportunity_by_id(opportunity_id)
            if opportunity and opportunity['proposal_path']:
                os.startfile(opportunity['proposal_path'])

    def update_button_states(self):
        selected_item = self.opportunities_list.currentItem()
        if selected_item:
            opportunity_id = selected_item.data(1)
            opportunity = get_opportunity_by_id(opportunity_id)
            if opportunity:
                is_proposal_phase = opportunity['phase'] == 'Propuesta' # Assuming 'Propuesta' is the phase for generating proposals
                has_proposal = bool(opportunity['proposal_path'])
                self.upload_proposal_button.setEnabled(is_proposal_phase)
                self.view_proposal_button.setEnabled(has_proposal)
                self.generate_proposal_button.setEnabled(True) # Enable generate button if an opportunity is selected
            else:
                self.upload_proposal_button.setEnabled(False)
                self.view_proposal_button.setEnabled(False)
                self.generate_proposal_button.setEnabled(False)
        else:
            self.upload_proposal_button.setEnabled(False)
            self.view_proposal_button.setEnabled(False)
            self.generate_proposal_button.setEnabled(False)

    def generate_proposal_for_opportunity(self):
        selected_item = self.opportunities_list.currentItem()
        if selected_item:
            opportunity_id = selected_item.data(1)
            # Define a path for the generated proposal (e.g., in a 'proposals' subfolder)
            proposal_dir = os.path.join(get_app_data_dir(), "proposals")
            os.makedirs(proposal_dir, exist_ok=True)
            opportunity = get_opportunity_by_id(opportunity_id)
            if opportunity:
                file_name = f"Propuesta_{opportunity['title']}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"
                file_path = os.path.join(proposal_dir, file_name)
                if generate_proposal_document(opportunity_id, file_path):
                    print(f"Propuesta generada en: {file_path}")
                    update_opportunity_proposal_path(opportunity_id, file_path, None) # if you want to store the generated proposal path
                    self.load_opportunities()
                else:
                    print("Error al generar la propuesta.")
