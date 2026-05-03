import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"


class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker — Трекер прочитанных книг")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        # Список книг (каждая книга — словарь)
        self.books = self.load_books()

        # Виджеты
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()

        # Заполнить таблицу
        self.refresh_treeview()

    # ---------------------- Ввод данных ----------------------
    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="Добавить книгу", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Поля
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_entry = ttk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Автор:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.author_entry = ttk.Entry(frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Жанр:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.genre_entry = ttk.Entry(frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Страниц:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.pages_entry = ttk.Entry(frame, width=10)
        self.pages_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # Кнопка "Добавить"
        self.add_btn = ttk.Button(frame, text="Добавить книгу", command=self.add_book)
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)

    # ---------------------- Фильтрация ----------------------
    def create_filter_frame(self):
        frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        # По жанру
        ttk.Label(frame, text="Жанр:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_genre_var = tk.StringVar()
        self.filter_genre_entry = ttk.Entry(frame, textvariable=self.filter_genre_var, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5)

        # По страницам > N
        ttk.Label(frame, text="Страниц >").grid(row=0, column=2, sticky="w", padx=5)
        self.filter_pages_var = tk.StringVar()
        self.filter_pages_entry = ttk.Entry(frame, textvariable=self.filter_pages_var, width=6)
        self.filter_pages_entry.grid(row=0, column=3, padx=5)
        ttk.Label(frame, text="(0 = отключить)").grid(row=0, column=4, sticky="w", padx=5)

        # Кнопка применить фильтр
        self.apply_filter_btn = ttk.Button(frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_btn.grid(row=0, column=5, padx=10)

        # Кнопка сбросить фильтр
        self.reset_filter_btn = ttk.Button(frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=6, padx=5)

    # ---------------------- Таблица книг ----------------------
    def create_tree_view(self):
        # Рамка с прокруткой
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("title", "author", "genre", "pages"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Определяем столбцы
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")

        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=100)
        self.tree.column("pages", width=80)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

    def create_button_frame(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        self.save_btn = ttk.Button(frame, text="Сохранить в JSON", command=self.save_books_to_file)
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = ttk.Button(frame, text="Загрузить из JSON", command=self.load_books_from_file)
        self.load_btn.pack(side="left", padx=5)

    # ---------------------- Логика работы ----------------------
    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Проверки
        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Все поля (кроме страниц) должны быть заполнены!")
            return

        if not pages_str:
            messagebox.showerror("Ошибка", "Укажите количество страниц!")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Добавляем книгу
        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
        }
        self.books.append(new_book)
        self.save_books_to_file()  # автоматически сохраняем после добавления

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        self.refresh_treeview()
        messagebox.showinfo("Успех", "Книга добавлена!")

    def refresh_treeview(self, books_to_show=None):
        """Обновляет таблицу. Если books_to_show не указан, показывает все книги."""
        self.tree.delete(*self.tree.get_children())
        data = books_to_show if books_to_show is not None else self.books
        for book in data:
            self.tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def apply_filter(self):
        """Фильтрация по жанру (частичное совпадение) и по страницам > N."""
        filtered = self.books[:]  # копия

        genre_filter = self.filter_genre_var.get().strip().lower()
        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]

        pages_filter_str = self.filter_pages_var.get().strip()
        if pages_filter_str:
            try:
                min_pages = int(pages_filter_str)
                if min_pages > 0:
                    filtered = [b for b in filtered if b["pages"] > min_pages]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр страниц должен быть числом (или 0 для отключения)")
                return

        self.refresh_treeview(filtered)

    def reset_filter(self):
        """Сброс фильтров и отображение всех книг."""
        self.filter_genre_var.set("")
        self.filter_pages_var.set("")
        self.refresh_treeview(self.books)

    # ---------------------- Работа с JSON ----------------------
    def load_books(self):
        """Загружает книги из JSON при старте программы."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_books_to_file(self):
        """Сохраняет текущий список книг в JSON."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_books_from_file(self):
        """Загружает книги из JSON и обновляет интерфейс."""
        if not os.path.exists(DATA_FILE):
            messagebox.showwarning("Загрузка", "Файл с книгами не найден.")
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.refresh_treeview()
            messagebox.showinfo("Загрузка", f"Загружено {len(self.books)} книг.")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()