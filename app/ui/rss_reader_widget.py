from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QInputDialog, QMessageBox, QListWidgetItem, QLabel, QSplitter
from PyQt6.QtCore import Qt, QUrl, QDateTime
from PyQt6.QtGui import QDesktopServices
from app.db import rss_manager
from app.ui.rss_article_item_widget import RssArticleItemWidget
from app.data import settings_manager
from app.utils import time_utils
import time
import feedparser

class RssReaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_feed_url = None

        self.layout = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        # Left side: RSS feed list
        self.feed_list_widget = QWidget()
        self.feed_list_layout = QVBoxLayout(self.feed_list_widget)
        self.feed_list = QListWidget()
        self.feed_list.itemClicked.connect(self.on_feed_selected)
        self.feed_list_layout.addWidget(self.feed_list)

        self.feed_buttons_layout = QHBoxLayout()
        self.add_feed_button = QPushButton("Añadir Feed")
        self.add_feed_button.clicked.connect(self.add_feed)
        self.delete_feed_button = QPushButton("Eliminar Feed")
        self.delete_feed_button.clicked.connect(self.delete_feed)
        self.feed_buttons_layout.addWidget(self.add_feed_button)
        self.feed_buttons_layout.addWidget(self.delete_feed_button)
        self.feed_list_layout.addLayout(self.feed_buttons_layout)

        # Right side: Article list
        self.article_list_widget = QWidget()
        self.article_list_layout = QVBoxLayout(self.article_list_widget)
        self.article_list_label = QLabel("Artículos")
        self.article_list_layout.addWidget(self.article_list_label)
        self.article_list = QListWidget()
        self.article_list.itemDoubleClicked.connect(self.open_article_link)
        self.article_list_layout.addWidget(self.article_list)

        self.splitter.addWidget(self.feed_list_widget)
        self.splitter.addWidget(self.article_list_widget)

        self.load_feeds()

    def load_feeds(self):
        self.feed_list.clear()
        feeds = rss_manager.get_all_feeds()
        for feed in feeds:
            item = QListWidgetItem(feed['name'])
            item.setData(Qt.ItemDataRole.UserRole, feed['id'])
            item.setData(Qt.ItemDataRole.UserRole + 1, feed['url'])
            self.feed_list.addItem(item)

    def on_feed_selected(self, item):
        self.current_feed_url = item.data(Qt.ItemDataRole.UserRole + 1)
        self.article_list_label.setText(f"Artículos de: {item.text()}")
        self.load_articles()

    def load_articles(self):
        self.article_list.clear()
        if self.current_feed_url:
            articles = rss_manager.fetch_feed_items(self.current_feed_url)
            datetime_format = settings_manager.get_datetime_format()
            for article in articles:
                published_str = article.get('published_parsed') or article.get('published')
                if published_str:
                    if isinstance(published_str, str):
                        # Try to parse various date formats
                        try:
                            # Example: "Wed, 22 May 2024 13:30:00 +0000"
                            dt_object = datetime.datetime.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')
                        except ValueError:
                            try:
                                # Example: "2024-05-22T13:30:00Z"
                                dt_object = datetime.datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                            except ValueError:
                                dt_object = None
                    elif isinstance(published_str, time.struct_time):
                        dt_object = datetime.datetime.fromtimestamp(time.mktime(published_str))
                    else:
                        dt_object = None

                    if dt_object:
                        published_formatted = dt_object.strftime(datetime_format)
                    else:
                        published_formatted = "Fecha no disponible"
                else:
                    published_formatted = "Fecha no disponible"

                item_widget = RssArticleItemWidget(
                    article['title'],
                    published_formatted,
                    article['summary'][:400] + '...' if len(article['summary']) > 400 else article['summary']
                )
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                self.article_list.addItem(list_item)
                self.article_list.setItemWidget(list_item, item_widget)
                list_item.setData(Qt.ItemDataRole.UserRole, article['link'])


    def add_feed(self):
        name, ok = QInputDialog.getText(self, 'Añadir Feed RSS', 'Nombre del Feed:')
        if not ok or not name: return

        url, ok = QInputDialog.getText(self, 'Añadir Feed RSS', 'URL del Feed:')
        if ok and url:
            rss_manager.add_feed(name, url)
            self.load_feeds()

    def delete_feed(self):
        selected_item = self.feed_list.currentItem()
        if selected_item:
            feed_id = selected_item.data(Qt.ItemDataRole.UserRole)
            reply = QMessageBox.question(self, 'Eliminar Feed', '¿Estás seguro de que quieres eliminar este feed?')
            if reply == QMessageBox.Yes:
                rss_manager.delete_feed(feed_id)
                self.load_feeds()
                self.article_list.clear()

    def open_article_link(self, item):
        link = item.data(Qt.ItemDataRole.UserRole)
        if link:
            QDesktopServices.openUrl(QUrl(link))
