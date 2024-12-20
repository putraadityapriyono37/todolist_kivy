import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, RoundedRectangle

# Database class for CRUD operations
class Database:
    @staticmethod
    def connect_to_database():
        try:
            db = sqlite3.connect('todo.db')
            c = db.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, Task VARCHAR(255) NOT NULL, Date VARCHAR(255) NOT NULL, Completed BOOLEAN NOT NULL)')
            return db
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    @staticmethod
    def read_database(db):
        c = db.cursor()
        c.execute("SELECT id, Task, Date, Completed FROM tasks")
        return c.fetchall()

    @staticmethod
    def insert_database(db, values):
        c = db.cursor()
        c.execute("INSERT INTO tasks (Task, Date, Completed) VALUES (?, ?, ?)", values)
        db.commit()

    @staticmethod
    def delete_database(db, task_id):
        c = db.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        db.commit()

    @staticmethod
    def update_database(db, task_id, new_task, completed):
        c = db.cursor()
        c.execute("UPDATE tasks SET Task=?, Completed=? WHERE id=?", (new_task, completed, task_id))
        db.commit()


class TaskItem(BoxLayout):
    def __init__(self, task_id: int, task: str, date: str, completed: bool, delete_func, update_func, toggle_func, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.task = task
        self.completed = completed

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80
        self.padding = (10, 10)
        self.spacing = 15

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark background for task items
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])

        self.bind(size=self._update_rect, pos=self._update_rect)

        # CheckBox to mark task as complete/incomplete
        self.checkbox = CheckBox(active=self.completed, size_hint=(None, None), size=(40, 40))
        self.checkbox.bind(active=toggle_func)
        self.add_widget(self.checkbox)

        # Task label
        self.task_label = Label(text=f"[b]{task}[/b]\n[size=12sp]{date}[/size]",
                                markup=True, halign='left', valign='middle',
                                color=(1, 1, 1, 1))
        self.task_label.bind(size=self.task_label.setter('text_size'))
        self.add_widget(self.task_label)

        # Edit button
        edit_button = Button(background_normal='', background_color=(0.24, 0.56, 0.34, 1), text='Edit',
                             font_size='18sp', size_hint=(None, None), size=(80, 40), color=(1, 1, 1, 1),
                             bold=True)
        edit_button.bind(on_press=lambda x: update_func(self))
        edit_button.bind(on_enter=lambda x: edit_button.background_color.set((0.28, 0.64, 0.38, 1)))  # Hover effect
        edit_button.bind(on_leave=lambda x: edit_button.background_color.set((0.24, 0.56, 0.34, 1)))  # Hover effect
        self.add_widget(edit_button)

        # Delete button
        delete_button = Button(background_normal='', background_color=(0.8, 0.2, 0.2, 1), text='Delete',
                               font_size='18sp', size_hint=(None, None), size=(80, 40), color=(1, 1, 1, 1),
                               bold=True)
        delete_button.bind(on_press=lambda x: delete_func(self))
        delete_button.bind(on_enter=lambda x: delete_button.background_color.set((0.9, 0.3, 0.3, 1)))  # Hover effect
        delete_button.bind(on_leave=lambda x: delete_button.background_color.set((0.8, 0.2, 0.2, 1)))  # Hover effect
        self.add_widget(delete_button)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_task_text(self, new_task):
        self.task = new_task
        self.task_label.text = f"[b]{new_task}[/b]\n[size=12sp]{datetime.now().strftime('%b %d, %Y %I:%M')}[/size]"

    def update_task_status(self, completed):
        self.completed = completed
        if completed:
            self.task_label.text = f"[s]{self.task}[/s]\n[size=12sp]{datetime.now().strftime('%b %d, %Y %I:%M')}[/size]"
        else:
            self.task_label.text = f"[b]{self.task}[/b]\n[size=12sp]{datetime.now().strftime('%b %d, %Y %I:%M')}[/size]"


class ToDoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header area for app name at the top
        header = BoxLayout(size_hint_y=None, height=60, padding=(10, 10), spacing=10)
        app_label = Label(text='[b]To-Do List[/b]', markup=True,
                          halign='left', valign='middle',
                          color=(1, 1, 1, 1), font_size='24sp')
        app_label.bind(size=app_label.setter('text_size'))
        header.add_widget(app_label)

        self.layout.add_widget(header)

        # Input area for adding tasks below the header
        input_area = BoxLayout(size_hint_y=None, height=50, spacing=10)

        # Text input field
        self.task_input = TextInput(hint_text='Enter new task...', multiline=False,
                                    size_hint=(1, None), height=40, padding=(10, 5))
        input_area.add_widget(self.task_input)

        # Add task button
        submit_button = Button(text='Add Task', size_hint=(None, None), height=40, width=120,
                               background_color=(0.24, 0.56, 0.94, 1), color=(1, 1, 1, 1), bold=True)
        submit_button.bind(on_press=self.add_task)
        submit_button.bind(on_enter=lambda x: submit_button.background_color.set((0.28, 0.64, 1, 1)))  # Hover effect
        submit_button.bind(on_leave=lambda x: submit_button.background_color.set((0.24, 0.56, 0.94, 1)))  # Hover effect
        input_area.add_widget(submit_button)

        self.layout.add_widget(input_area)

        # Scrollable area for task items
        self.scroll_view = ScrollView()
        self.task_list_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        self.scroll_view.add_widget(self.task_list_layout)

        self.layout.add_widget(self.scroll_view)

        # Load existing tasks from database
        self.load_tasks()

        return self.layout

    def load_tasks(self):
        db = Database.connect_to_database()

        if db:
            try:
                for task in Database.read_database(db)[::-1]:
                    task_item = TaskItem(task[0], task[1], task[2], task[3], self.delete_task,
                                         self.update_task, self.toggle_task)
                    self.task_list_layout.add_widget(task_item)
            finally:
                if db:
                    db.close()

    def add_task(self, instance):
        db = Database.connect_to_database()

        if db is None:
            print("Database connection failed. Task not added.")
            return

        try:
            task_description = self.task_input.text.strip()
            if not task_description:
                print("Task description cannot be empty.")
                return

            date_time = datetime.now().strftime("%b %d, %Y %I:%M")

            Database.insert_database(db, (task_description, date_time, False))
            task_item = TaskItem(None, task_description, date_time, False, self.delete_task,
                                 self.update_task, self.toggle_task)
            self.task_list_layout.add_widget(task_item)
            self.task_input.text = ''

        except Exception as ex:
            print(f"Error during task addition: {ex}")

        finally:
            if db:
                db.close()

    def delete_task(self, task_instance):
        db = Database.connect_to_database()

        if db is None:
            print("Database connection failed. Task not deleted.")
            return

        try:
            task_id = task_instance.task_id
            Database.delete_database(db, task_id)
            self.task_list_layout.remove_widget(task_instance)

        except Exception as ex:
            print(f"Error during task deletion: {ex}")

        finally:
            if db:
                db.close()

    def update_task(self, task_instance):
        # Create an input to update task
        input_area = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10)
        task_input = TextInput(text=task_instance.task, multiline=False, size_hint=(1, None), height=40)
        input_area.add_widget(task_input)

        # Button to confirm update
        update_button = Button(text='Update', size_hint=(None, None), height=40, width=120,
                               background_color=(0.24, 0.56, 0.94, 1), color=(1, 1, 1, 1), bold=True)
        
        def on_update(instance):
            new_task = task_input.text.strip()
            if new_task:
                db = Database.connect_to_database()
                if db:
                    try:
                        Database.update_database(db, task_instance.task_id, new_task, task_instance.completed)
                        task_instance.update_task_text(new_task)
                    finally:
                        if db:
                            db.close()
            else:
                print("Task cannot be empty.")
            self.layout.remove_widget(input_area)

        update_button.bind(on_press=on_update)
        input_area.add_widget(update_button)
        
        # Add the input area for editing task
        self.layout.add_widget(input_area)

    def toggle_task(self, checkbox_instance, value):
        db = Database.connect_to_database()

        if db:
            try:
                task_id = checkbox_instance.parent.task_id
                task_instance = checkbox_instance.parent
                Database.update_database(db, task_id, task_instance.task, value)
                task_instance.update_task_status(value)
            finally:
                if db:
                    db.close()

if __name__ == '__main__':
    ToDoApp().run()
