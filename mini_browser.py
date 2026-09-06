"""
Mini navigateur web - PySide6 + QtWebEngine
--------------------------------------------
Un navigateur simple avec :
- Barre d'adresse
- Boutons Précédent / Suivant / Rafraîchir / Accueil
- Onglets multiples (Ctrl+T pour ouvrir, Ctrl+W pour fermer)
- Barre de progression de chargement

Installation (Windows, PowerShell ou cmd) :
    pip install PySide6

Lancement :
    python mini_browser.py
"""

import sys
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget,
    QWidget, QVBoxLayout, QPushButton, QProgressBar, QStyle
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QKeySequence, QShortcut

HOME_URL = "https://www.google.com"


class BrowserTab(QWidget):
    def __init__(self, url=HOME_URL, parent=None):
        super().__init__(parent)
        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)


class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Navigateur")
        self.resize(1200, 800)

        # --- Onglets ---
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

        # --- Barre d'outils ---
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        style = self.style()

        back_btn = QPushButton()
        back_btn.setIcon(style.standardIcon(QStyle.SP_ArrowBack))
        back_btn.clicked.connect(lambda: self.current_view().back())
        toolbar.addWidget(back_btn)

        fwd_btn = QPushButton()
        fwd_btn.setIcon(style.standardIcon(QStyle.SP_ArrowForward))
        fwd_btn.clicked.connect(lambda: self.current_view().forward())
        toolbar.addWidget(fwd_btn)

        reload_btn = QPushButton()
        reload_btn.setIcon(style.standardIcon(QStyle.SP_BrowserReload))
        reload_btn.clicked.connect(lambda: self.current_view().reload())
        toolbar.addWidget(reload_btn)

        home_btn = QPushButton()
        home_btn.setIcon(style.standardIcon(QStyle.SP_DirHomeIcon))
        home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        toolbar.addWidget(new_tab_btn)

        # --- Barre de progression ---
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(3)
        self.progress.setTextVisible(False)
        self.statusBar().addPermanentWidget(self.progress, 1)
        self.progress.hide()

        # --- Raccourcis clavier ---
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: self.url_bar.setFocus())

        self.add_new_tab(HOME_URL)

    # ----------------------------------------------------------------
    def current_view(self):
        widget = self.tabs.currentWidget()
        return widget.view if widget else None

    def add_new_tab(self, url=HOME_URL):
        tab = BrowserTab(url)
        index = self.tabs.addTab(tab, "Nouvel onglet")
        self.tabs.setCurrentIndex(index)

        tab.view.urlChanged.connect(lambda qurl, t=tab: self.update_url_bar_for(t, qurl))
        tab.view.titleChanged.connect(lambda title, t=tab: self.update_tab_title(t, title))
        tab.view.loadStarted.connect(self.show_progress)
        tab.view.loadFinished.connect(self.hide_progress)
        return tab

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def go_home(self):
        if self.current_view():
            self.current_view().setUrl(QUrl(HOME_URL))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "." in text and " " not in text and not text.startswith(("http://", "https://")):
            url = "https://" + text
        elif text.startswith(("http://", "https://")):
            url = text
        else:
            # Traiter comme une recherche Google
            url = "https://www.google.com/search?q=" + text.replace(" ", "+")
        if self.current_view():
            self.current_view().setUrl(QUrl(url))

    def update_url_bar(self, index):
        widget = self.tabs.widget(index)
        if widget:
            self.url_bar.setText(widget.view.url().toString())

    def update_url_bar_for(self, tab, qurl):
        if self.tabs.currentWidget() is tab:
            self.url_bar.setText(qurl.toString())

    def update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index != -1:
            short = title if len(title) <= 20 else title[:20] + "…"
            self.tabs.setTabText(index, short or "Nouvel onglet")

    def show_progress(self):
        self.progress.show()
        self.progress.setRange(0, 0)  # mode indéterminé

    def hide_progress(self):
        self.progress.hide()


def main():
    app = QApplication(sys.argv)
    window = MiniBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
