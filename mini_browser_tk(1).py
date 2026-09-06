"""
Mini navigateur web - CustomTkinter + tkinterweb
--------------------------------------------------
IMPORTANT : Tkinter n'a pas de moteur de rendu web natif.
Ce script utilise "tkinterweb" pour afficher du HTML/CSS basique.
Le JavaScript N'EST PAS supporté -> les sites très dynamiques
(Google, réseaux sociaux, apps web) s'afficheront mal ou pas du tout.
Ca fonctionne bien en revanche pour : Wikipédia, blogs, docs, sites simples.

Installation (Windows, cmd ou PowerShell) :
    pip install customtkinter tkinterweb

Lancement (IMPORTANT: lance depuis un terminal pour voir les erreurs) :
    python mini_browser_tk.py
"""

import sys
import traceback
import customtkinter as ctk
from tkinterweb import HtmlFrame

HOME_URL = "https://fr.wikipedia.org"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MiniBrowser(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mini Navigateur (Tk)")
        self.geometry("1200x800")

        # --- Barre d'outils ---
        toolbar = ctk.CTkFrame(self, height=40)
        toolbar.pack(side="top", fill="x", padx=6, pady=6)

        back_btn = ctk.CTkButton(toolbar, text="◀", width=36, command=self.go_back)
        back_btn.pack(side="left", padx=2)

        fwd_btn = ctk.CTkButton(toolbar, text="▶", width=36, command=self.go_forward)
        fwd_btn.pack(side="left", padx=2)

        reload_btn = ctk.CTkButton(toolbar, text="⟳", width=36, command=self.reload_page)
        reload_btn.pack(side="left", padx=2)

        home_btn = ctk.CTkButton(toolbar, text="⌂", width=36, command=self.go_home)
        home_btn.pack(side="left", padx=2)

        self.url_var = ctk.StringVar(value=HOME_URL)
        self.url_entry = ctk.CTkEntry(toolbar, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.url_entry.bind("<Return>", lambda e: self.navigate_to_url())

        go_btn = ctk.CTkButton(toolbar, text="Aller", width=60, command=self.navigate_to_url)
        go_btn.pack(side="left", padx=2)

        # --- Barre de statut ---
        self.status_var = ctk.StringVar(value="Prêt")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=6, pady=(0, 4))

        # --- Zone de rendu HTML ---
        self.html_frame = HtmlFrame(self, messages_enabled=False)
        self.html_frame.pack(side="top", fill="both", expand=True, padx=6, pady=(0, 6))

        # Historique simple
        self.history = []
        self.history_index = -1

        # Callbacks tkinterweb
        self.html_frame.on_link_click(self.on_link_click)
        self.html_frame.on_url_change(self.on_url_change)
        self.html_frame.on_title_change(self.on_title_change)

        self.go_home()

    # ----------------------------------------------------------------
    def load_url(self, url, record_history=True):
        self.status_var.set(f"Chargement de {url} ...")
        try:
            self.html_frame.load_website(url)
            self.url_var.set(url)
            if record_history:
                # tronque le futur si on navigue depuis un point antérieur
                self.history = self.history[: self.history_index + 1]
                self.history.append(url)
                self.history_index = len(self.history) - 1
            self.status_var.set(f"Chargé : {url}")
        except Exception as e:
            self.status_var.set(f"Erreur : {e}")
            traceback.print_exc()

    def navigate_to_url(self):
        text = self.url_var.get().strip()
        if not text:
            return
        if not text.startswith(("http://", "https://")):
            if "." in text and " " not in text:
                text = "https://" + text
            else:
                text = "https://fr.wikipedia.org/wiki/Special:Search?search=" + text.replace(" ", "+")
        self.load_url(text)

    def go_home(self):
        self.load_url(HOME_URL)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_url(self.history[self.history_index], record_history=False)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_url(self.history[self.history_index], record_history=False)

    def reload_page(self):
        if self.history:
            self.load_url(self.history[self.history_index], record_history=False)

    # --- Callbacks tkinterweb ---
    def on_link_click(self, url):
        self.load_url(url)

    def on_url_change(self, url):
        self.url_var.set(url)

    def on_title_change(self, title):
        self.title(f"{title} - Mini Navigateur (Tk)" if title else "Mini Navigateur (Tk)")


def main():
    try:
        app = MiniBrowser()
        app.mainloop()
    except Exception:
        print("=== ERREUR AU LANCEMENT ===")
        traceback.print_exc()
        input("Appuie sur Entrée pour fermer...")
        sys.exit(1)


if __name__ == "__main__":
    main()
