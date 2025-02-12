from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
import csv
import os
from datetime import datetime

# ---------------------------- STATE MANAGEMENT ---------------------------- #
class TaskTrackerState:
    """Handles task tracking, saving, and categorization"""

    DATA_FILE = "daily_tasks.csv"
    TASK_NAMES = [
        "Education", "Organisation", "Socialisation", "Food", "Activity", 
        "Meow", "Mini", "Journaling", "Portfolio", "Work"
    ]

    def __init__(self):
        """Initialize state and load previous data"""
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.task_status = [False] * len(self.TASK_NAMES)
        self.category = None
        if not os.path.exists(self.DATA_FILE):
            self._create_csv()

    def _create_csv(self):
        """Creates a CSV file if it does not exist"""
        with open(self.DATA_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Completed Tasks", "Category"])  # CSV Headers

    def categorize_day(self, completed):
        """Categorize the day based on tasks completed"""
        if completed < 5:
            return None  # Less than 5 tasks → show warning
        elif completed == 5:
            return "🔴 Bare Minimum Day (Red)"
        elif 6 <= completed <= 8:
            return "🟠 Maintenance Day (Orange)"
        else:
            return "🟢 Ideal Day (Green)"

    def save_progress(self):
        """Saves the completed tasks count and categorizes the day"""
        completed_tasks = sum(self.task_status)
        self.category = self.categorize_day(completed_tasks)

        if self.category is not None:
            with open(self.DATA_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([self.today, completed_tasks, self.category])

    def load_history(self):
        """Load the last 5 days of task tracking"""
        if not os.path.exists(self.DATA_FILE):
            return "📜 No past records yet."

        with open(self.DATA_FILE, mode="r") as file:
            reader = csv.reader(file)
            history = list(reader)[-5:]  # Show last 5 days

        if not history:
            return "📜 No past records yet."

        return "\n".join([f"📌 {date}: {tasks}/10 tasks - {category}" for date, tasks, category in history[1:]])  # Skip header row

# ---------------------------- UI MANAGEMENT ---------------------------- #
class TaskTrackerUI(BoxLayout):
    """Handles UI elements and interactions"""

    def __init__(self, state, app_ref, **kwargs):
        super().__init__(orientation='vertical', padding=10, **kwargs)
        self.state = state  # Injected state manager
        self.app_ref = app_ref  # Injected app reference (for state transitions)

        # Header
        self.add_widget(Label(text=f"📅 Today: {self.state.today}", font_size=20))

        # Task checkboxes
        self.checkboxes = []
        for i, task_name in enumerate(TaskTrackerState.TASK_NAMES):
            task_box = BoxLayout(orientation='horizontal')
            task_label = Label(text=task_name, font_size=18, size_hint_x=0.7)
            task_check = CheckBox(size_hint_x=0.3)
            task_check.bind(active=self.update_tasks)
            self.checkboxes.append(task_check)
            task_box.add_widget(task_label)
            task_box.add_widget(task_check)
            self.add_widget(task_box)

        # Submit button
        self.submit_button = Button(text="✅ Save & Categorize", font_size=20)
        self.submit_button.bind(on_press=self.app_ref.handle_state_transition)
        self.add_widget(self.submit_button)

        # Status label
        self.status_label = Label(text="Select tasks completed", font_size=18)
        self.add_widget(self.status_label)

        # Display past performance
        self.history_label = Label(text=self.state.load_history(), font_size=16)
        self.add_widget(self.history_label)

    def update_tasks(self, checkbox, value):
        """Update task completion status"""
        index = self.checkboxes.index(checkbox)
        self.state.task_status[index] = value

    def update_ui(self):
        """Updates UI after task submission"""
        if self.state.category is None:
            self.status_label.text = "⚠️ Not enough tasks completed!"
        else:
            self.status_label.text = f"🌟 Today is categorized as: {self.state.category}"
        self.history_label.text = self.state.load_history()

# ---------------------------- APPLICATION MANAGEMENT ---------------------------- #
class TaskTrackerApp(App):
    """Controls state transitions and manages the app lifecycle"""

    def __init__(self, state, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.ui = None  # UI will be initialized later

    def build(self):
        """Build the UI and inject dependencies"""
        self.ui = TaskTrackerUI(self.state, self)
        return self.ui

    def handle_state_transition(self, instance):
        """Handles state transitions when the user saves tasks"""
        self.state.save_progress()  # Save progress in the state
        self.ui.update_ui()  # Update UI based on the new state

# ---------------------------- MAIN FUNCTION ---------------------------- #
def main():
    """Handles state transitions explicitly and runs the app"""
    state = TaskTrackerState()  # Initialize state manager
    app = TaskTrackerApp(state)  # Initialize app with state
    app.run()  # Run the UI loop

# ---------------------------- RUN APP ---------------------------- #
if __name__ == "__main__":
    main()
