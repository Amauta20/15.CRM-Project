from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtCore import Qt, QDateTime
from app.data import settings_manager
from app.utils import time_utils

class ViewKanbanCardDetailsDialog(QDialog):
    def __init__(self, card_details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de la Tarjeta Kanban")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        def format_datetime(dt_str):
            if not dt_str:
                return "N/A"
            utc_dt = QDateTime.fromString(dt_str, Qt.DateFormat.ISODate)
            datetime_format = settings_manager.get_datetime_format()
            return utc_dt.toLocalTime().toString(time_utils.convert_strftime_to_qt_format(datetime_format))

        self.title_label = QLabel(f"<b>Título:</b> {card_details['title']}")
        self.layout.addWidget(self.title_label)

        self.description_label = QLabel(f"<b>Descripción:</b> {card_details['description'] or 'N/A'}")
        self.layout.addWidget(self.description_label)

        self.assignee_label = QLabel(f"<b>Asignado a:</b> {card_details['assignee'] or 'N/A'}")
        self.layout.addWidget(self.assignee_label)

        self.created_at_label = QLabel(f"<b>Creada el:</b> {format_datetime(card_details['created_at'])}")
        self.layout.addWidget(self.created_at_label)

        self.started_at_label = QLabel(f"<b>Iniciada el:</b> {format_datetime(card_details['started_at'])}")
        self.layout.addWidget(self.started_at_label)

        self.finished_at_label = QLabel(f"<b>Finalizada el:</b> {format_datetime(card_details['finished_at'])}")
        self.layout.addWidget(self.finished_at_label)

        self.due_date_label = QLabel(f"<b>Fecha de Entrega:</b> {format_datetime(card_details['due_date'])}")
        self.layout.addWidget(self.due_date_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        self.layout.addWidget(button_box)