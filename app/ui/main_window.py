from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QStackedWidget, QToolBar, QLineEdit, QDialog, QSystemTrayIcon, QPushButton
from PyQt6.QtCore import Qt, QUrl, QTimer, QDateTime
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineScript
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import os

from app.ui.sidebar import Sidebar
from app.search import search_manager
from app.data import checklist_manager, settings_manager, kanban_manager
from app.utils import time_utils
from app.ui.search_results_widget import SearchResultsWidget
from app.ui.styles import dark_theme_stylesheet, light_theme_stylesheet
from app.messaging import service_manager
from app.ui.welcome_widget import WelcomeWidget
from app.ui.add_service_dialog import AddServiceDialog # Needed for opening dialog from welcome widget
from app.ui.notes_widget import NotesWidget
from app.ui.kanban_widget import KanbanWidget
from app.ui.checklist_widget import ChecklistWidget
from app.metrics.metrics_manager import MetricsManager
from app.ui.accounts_widget import AccountsWidget # New import
from app.ui.contacts_widget import ContactsWidget # New import

from app.ui.select_service_dialog import SelectServiceDialog
from app.ui.unified_settings_dialog import UnifiedSettingsDialog
from PyQt6.QtGui import QDesktopServices

from PyQt6.QtWidgets import QMenu, QApplication, QStyle
from PyQt6.QtGui import QAction

class LinkHandlingPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if self.url().host() != url.host():
                QDesktopServices.openUrl(url)
                return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        pos = event.globalPos()
        js_script = f"""
            (function() {{
                let element = document.elementFromPoint({event.pos().x()}, {event.pos().y()});
                let isContentEditable = element.isContentEditable;
                let linkUrl = '';
                let linkText = '';
                
                // Find the anchor tag
                while (element && element.tagName !== 'A') {{
                    element = element.parentElement;
                }}
                
                if (element) {{
                    linkUrl = element.href;
                    linkText = element.textContent;
                }}
                
                return {{
                    'isContentEditable': isContentEditable,
                    'linkUrl': linkUrl,
                    'linkText': linkText
                }};
            }})();
        """
        self.page().runJavaScript(js_script, lambda result: self._build_context_menu(result, pos))

    def _build_context_menu(self, data, pos):
        menu = QMenu(self)
        style = QApplication.style()

        # Standard navigation actions
        action_back = menu.addAction("Atrás")
        action_back.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        action_back.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Back))
        action_back.setEnabled(self.page().history().canGoBack())

        action_forward = menu.addAction("Adelante")
        action_forward.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        action_forward.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Forward))
        action_forward.setEnabled(self.page().history().canGoForward())

        action_reload = menu.addAction("Recargar")
        action_reload.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        action_reload.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Reload))

        action_stop = menu.addAction("Detener")
        action_stop.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserStop))
        action_stop.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Stop))
        action_stop.setEnabled(self.page().isLoading())

        if data and (data.get('linkUrl') or data.get('isContentEditable')):
            menu.addSeparator()

        if data and data.get('linkUrl'):
            link_url = QUrl(data['linkUrl'])
            action_open_external = menu.addAction("Abrir enlace en navegador externo")
            action_open_external.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            action_open_external.triggered.connect(lambda: QDesktopServices.openUrl(link_url))
            
            action_copy_link = menu.addAction("Copiar dirección de enlace")
            action_copy_link.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TitleBarContextHelpButton))
            action_copy_link.triggered.connect(lambda: QApplication.clipboard().setText(link_url.toString()))

        if data and data.get('isContentEditable'):
            if data.get('linkUrl'):
                menu.addSeparator()
                
            action_undo = menu.addAction("Deshacer")
            action_undo.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
            action_undo.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Undo))
            action_redo = menu.addAction("Rehacer")
            action_redo.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
            action_redo.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Redo))
            menu.addSeparator()
            action_cut = menu.addAction("Cortar")
            action_cut.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
            action_cut.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Cut))
            action_copy = menu.addAction("Copiar")
            action_copy.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
            action_copy.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Copy))
            action_paste = menu.addAction("Pegar")
            action_paste.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
            action_paste.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.Paste))
            action_select_all = menu.addAction("Seleccionar todo")
            action_select_all.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogListView))
            action_select_all.triggered.connect(lambda: self.page().triggerAction(QWebEnginePage.WebAction.SelectAll))

        if not menu.isEmpty():
            menu.exec(pos)

class MainWindow(QMainWindow):
    def __init__(self, metrics_manager_instance):
        super().__init__()
        self.metrics_manager = metrics_manager_instance

        # Dictionary to store service-specific JavaScript for unread message detection
        self._service_unread_js_scripts = {
            "WhatsApp": '''
                (function() {
                    // WhatsApp Web unread message indicator
                    // This selector might need adjustment if WhatsApp Web's DOM changes.
                    var unread = document.querySelector('._1gL0j, [aria-label*="unread" i]');
                    return unread !== null;
                })();
            ''',
            "Teams": '''
                (function() {
                    // Microsoft Teams unread message indicator
                    // This selector might need adjustment.
                    var unread = document.querySelector('.activity-badge, [data-tid="unseen-count"]');
                    return unread !== null;
                })();
            ''',
            "LinkedIn": '''
                (function() {
                    // LinkedIn unread message indicator
                    // This selector might need adjustment.
                    var unread = document.querySelector('.msg-overlay-bubble--is-active, .notification-badge--show');
                    return unread !== null;
                })();
            ''',
            # Add more services here
        }

        self.setWindowTitle("InfoMensajero")
        self.setGeometry(100, 100, 1280, 720)

        # Main layout
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Header (Toolbar) ---
        self.toolbar = self.addToolBar("Barra de Herramientas Principal")
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Búsqueda Global (Notas, Kanban, Texto Pegado)")
        self.search_input.setFixedWidth(300)
        self.search_input.returnPressed.connect(self.perform_global_search)
        self.toolbar.addWidget(self.search_input)

        self.toolbar.addSeparator()

        self.general_settings_button = QPushButton("Configuración General")
        self.general_settings_button.clicked.connect(self.open_unified_settings_dialog)
        self.toolbar.addWidget(self.general_settings_button)

        # Global Search Shortcut (Ctrl+F)
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focus_search_bar)

        # --- Web view management ---
        self.web_view_stack = QStackedWidget()
        self.web_views = {} # Cache for web views: {profile_path: QWebEngineView}

        # Search Results Widget
        self.search_results_widget = SearchResultsWidget()
        self.web_view_stack.addWidget(self.search_results_widget) # Add it to the stack, but not visible initially

        # Welcome Widget
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.add_service_requested.connect(self.add_service_from_welcome)
        self.web_view_stack.addWidget(self.welcome_widget)

        # Notes Widget
        self.notes_widget = NotesWidget()
        self.web_view_stack.addWidget(self.notes_widget)

        # Kanban Widget
        self.kanban_widget = KanbanWidget()
        self.web_view_stack.addWidget(self.kanban_widget)

        # Checklist Widget
        self.checklist_widget = ChecklistWidget()
        self.web_view_stack.addWidget(self.checklist_widget)

        # Accounts Widget (New)
        self.accounts_widget = AccountsWidget()
        self.web_view_stack.addWidget(self.accounts_widget)

        # Contacts Widget (New)
        self.contacts_widget = ContactsWidget()
        self.web_view_stack.addWidget(self.contacts_widget)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(240)

        # Splitter to manage sidebar and web_view_stack
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.web_view_stack)
        self.splitter.setSizes([240, 1040]) # Sidebar width, main content width

        self.main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.central_widget)

        # Connect signals
        self.sidebar.service_selected.connect(self.load_service)
        self.sidebar.service_deleted.connect(self.remove_webview_for_service)
        self.sidebar.show_notes_requested.connect(self.show_notes_tools)
        self.sidebar.show_kanban_requested.connect(self.show_kanban_tools)
        self.sidebar.show_checklist_requested.connect(self.show_checklist_tools)
        self.sidebar.show_accounts_requested.connect(self.show_accounts_tools) # New connection
        self.sidebar.show_contacts_requested.connect(self.show_contacts_tools) # New connection

        # Welcome widget signals
        self.welcome_widget.show_kanban_requested.connect(self.show_kanban_tools)
        self.welcome_widget.show_checklist_requested.connect(self.show_checklist_tools)

        # Productivity widget update signals
        self.kanban_widget.kanban_updated.connect(self.welcome_widget.refresh)
        self.checklist_widget.checklist_updated.connect(self.welcome_widget.refresh)

        self.kanban_widget.kanban_updated.connect(self.checklist_widget.refresh_kanban_cards)

        self.search_results_widget.result_clicked.connect(self.on_search_result_clicked)

        # Notification system
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icon.ico'))
        print(f"Icon path: {icon_path}")
        print(f"Icon file exists: {os.path.exists(icon_path)}")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.show()

        # Set application window icon
        self.setWindowIcon(QIcon(icon_path))

        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_for_notifications)
        self.notification_timer.start(10000) # Check every 10 seconds

        # Load initial service or a default page
        self.load_initial_page()

        # Start tracking initial page
        self.metrics_manager.start_tracking("Bienvenida") # Start tracking Welcome widget

    def closeEvent(self, event):
        self.metrics_manager.stop_tracking_current()
        super().closeEvent(event)

    def _handle_download_requested(self, download):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
            
        file_name = download.downloadFileName()
        if not file_name:
            file_name = os.path.basename(download.url().path())
        
        download.setDownloadDirectory(downloads_path)
        if file_name:
            download.setDownloadFileName(file_name)
            
        download.accept()
        
        self.show_notification("Descarga Aceptada", f"El archivo se está descargando en {downloads_path}")

    def show_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)

    def check_for_notifications(self):
        # Get pre-notification offset
        pre_notification_offset_minutes = settings_manager.get_pre_notification_offset()

        # Check for pre-due checklist items
        pre_due_checklist_items = checklist_manager.get_pre_due_checklist_items(pre_notification_offset_minutes)
        for item in pre_due_checklist_items:
            self.show_notification("Tarea de Checklist Próxima", f"'{item['text']}' vence pronto ({item['due_at']})")
            checklist_manager.update_checklist_item(item['id'], pre_notified_at=time_utils.to_utc(time_utils.datetime_from_qdatetime(time_utils.get_current_qdatetime())).isoformat())

        # Check for due checklist items
        due_checklist_items = checklist_manager.get_actual_due_checklist_items()
        for item in due_checklist_items:
            self.show_notification("Tarea de Checklist", item['text'])
            checklist_manager.update_checklist_item(item['id'], is_notified=1)
    
    def open_unified_settings_dialog(self):
        dialog = UnifiedSettingsDialog(self)
        if dialog.exec():
            # Reload settings that might affect UI or timers
            # Potentially refresh checklist/reminder views if date format changes
            self.checklist_widget.load_checklist_items() # Assuming this refreshes display
            self.kanban_widget.load_kanban_boards()

    def show_notes_tools(self):
        self.web_view_stack.setCurrentWidget(self.notes_widget)
        self.track_current_widget_usage()

    def show_kanban_tools(self):
        self.web_view_stack.setCurrentWidget(self.kanban_widget)
        self.track_current_widget_usage()

    def show_checklist_tools(self):
        self.web_view_stack.setCurrentWidget(self.checklist_widget)
        self.track_current_widget_usage()

    def show_accounts_tools(self):
        self.web_view_stack.setCurrentWidget(self.accounts_widget)
        self.accounts_widget.load_accounts() # Refresh accounts when shown
        self.track_current_widget_usage()

    def show_contacts_tools(self):
        self.web_view_stack.setCurrentWidget(self.contacts_widget)
        self.contacts_widget.load_contacts() # Refresh contacts when shown
        self.track_current_widget_usage()

    def track_current_widget_usage(self):
        current_widget = self.web_view_stack.currentWidget()
        service_name = "Desconocido"

        if isinstance(current_widget, QWebEngineView):
            # For web views, try to get the service name from the URL or profile
            # This is a simplified approach; a more robust one would map profile_path back to service name
            for profile_path, view in self.web_views.items():
                if view == current_widget:
                    service_details = service_manager.get_service_by_profile_path(profile_path)
                    if service_details: service_name = service_details['name']
                    break
        elif hasattr(current_widget, '__class__'):
            # For internal widgets, use their class name or a predefined name
            if current_widget == self.welcome_widget: service_name = "Bienvenida"
            elif current_widget == self.notes_widget: service_name = "Notas"
            elif current_widget == self.kanban_widget: service_name = "Kanban"
            elif current_widget == self.checklist_widget: service_name = "Checklist"
            elif current_widget == self.accounts_widget: service_name = "Cuentas" # New tracking
            elif current_widget == self.contacts_widget: service_name = "Contactos" # New tracking
            elif current_widget == self.search_results_widget: service_name = "Búsqueda"
            # Add other internal widgets here

        self.metrics_manager.start_tracking(service_name)

    def show_productivity_tools(self):
        # This method is now obsolete, but kept for compatibility until sidebar is fully refactored
        self.web_view_stack.setCurrentWidget(self.notes_widget) # Default to notes for now

    def trigger_add_service_dialog(self):
        self.sidebar.open_select_service_dialog()

    def add_service_from_welcome(self, name, url, icon):
        service_manager.add_service(name, url, icon)
        self.sidebar.load_services()
        self.load_initial_page()

    def focus_search_bar(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def perform_global_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        results = search_manager.search_all(query)
        self.search_results_widget.display_results(results, query)
        self.web_view_stack.setCurrentWidget(self.search_results_widget)
        self.track_current_widget_usage()

    def on_search_result_clicked(self, result_data):
        result_type = result_data.get('type')
        result_id = result_data.get('id')

        if result_type == 'note':
            self.web_view_stack.setCurrentWidget(self.notes_widget)
            self.notes_widget.find_and_select_note(result_id)
        elif result_type == 'kanban_card':
            self.web_view_stack.setCurrentWidget(self.kanban_widget)
            self.kanban_widget.find_and_highlight_card(result_id)

    def load_service(self, url, profile_path):
        """
        Loads a service in its own profile and view, creating it if it doesn't exist.
        """
        service_details = service_manager.get_service_by_profile_path(profile_path)
        if not service_details: # Handle case where service_details might not be found
            print(f"Error: Service details not found for profile_path: {profile_path}")
            return

        if profile_path in self.web_views:
            view = self.web_views[profile_path]
        else:
            # Create a new profile and view for this service
            profile_name = os.path.basename(profile_path) # Use folder name as profile name
            profile = QWebEngineProfile(profile_name, self)
            profile.setPersistentStoragePath(profile_path) # Set the actual storage path
            # Spoof user agent to a recent Chrome version for better compatibility
            profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            profile.downloadRequested.connect(self._handle_download_requested)

            view = CustomWebEngineView()
            page = LinkHandlingPage(profile, view)
            view.setPage(page)
            view.setProperty('service_id', service_details['id'])
            view.loadFinished.connect(self._on_web_view_load_finished)
            view.setUrl(QUrl(url))
            
            self.web_views[profile_path] = view
            self.web_view_stack.addWidget(view)

        self.web_view_stack.setCurrentWidget(view)
        self.track_current_widget_usage() # Track usage for web views

    def remove_webview_for_service(self, service_id):
        # Find the profile_path associated with the service_id
        service_details = service_manager.get_service_by_id(service_id)
        if not service_details: return

        profile_path = service_details['profile_path']

        if profile_path in self.web_views:
            view_to_remove = self.web_views.pop(profile_path) # Remove from cache
            self.web_view_stack.removeWidget(view_to_remove) # Remove from stack
            view_to_remove.deleteLater() # Schedule for deletion

            # If the removed view was the current one, switch to a default view
            if self.web_view_stack.currentWidget() == view_to_remove:
                self.load_initial_page() # Reload initial page (welcome or first service)

    def _on_web_view_load_finished(self, ok):
        view = self.sender() # The QWebEngineView that emitted the signal
        if not ok: # Page failed to load
            print(f"Page failed to load: {view.url().toString()}")
            return

        service_id = view.property('service_id')
        if service_id:
            self._check_unread_messages_for_service(service_id, view)

    def _check_unread_messages_for_service(self, service_id, view):
        service_details = service_manager.get_service_by_id(service_id)
        if not service_details: return

        service_name = service_details['name']
        js_script = self._service_unread_js_scripts.get(service_name, '''
            (function() {
                // Generic placeholder: You MUST customize this for each service.
                var unreadIndicator = document.querySelector('.unread-count, .badge-unread, [aria-label*="unread messages" i]');
                if (unreadIndicator) {
                    var text = unreadIndicator.innerText.trim();
                    if (text && !isNaN(parseInt(text))) {
                        return parseInt(text) > 0; // Return true if count > 0
                    } else {
                        return true; // Indicator present, assume unread
                    }
                }
                return false; // No unread indicator found
            })();
        ''')

        view.page().runJavaScript(js_script, lambda result: self._handle_unread_result(service_id, result))

    def _handle_unread_result(self, service_id, has_unread):
        print(f"Service {service_id} has unread messages: {has_unread}")
        self.sidebar.set_service_unread_status(service_id, has_unread)

    def load_initial_page(self):
        """
        Loads the first service in the list or a default welcome page.
        """
        services = service_manager.get_all_services()
        if services:
            first_service = services[0]
            self.load_service(first_service['url'], first_service['profile_path'])
        else:
            # If no services, show welcome widget
            self.web_view_stack.setCurrentWidget(self.welcome_widget)