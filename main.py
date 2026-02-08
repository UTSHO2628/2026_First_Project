import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, date

# --- CONFIGURATION ---
APP_TITLE = "Habit & Finance Tracker"
GEOMETRY = "800x850"
DATA_DIR = "data"
FONT_FAMILY = "Segoe UI" # A modern, clean font available on Windows

# --- STYLING ---
# Using a dark theme inspired by modern productivity apps......
class StyleManager:
    """Manages the visual styling of the application."""
    COLOR_BACKGROUND = "#1e1e1e"
    COLOR_CARD = "#2d2d2d"
    COLOR_TEXT = "#e0e0e0"
    COLOR_PRIMARY = "#007acc"
    COLOR_ENTRY_BG = "#3c3c3c"
    COLOR_BORDER = "#444444"
    FONT_NORMAL = (FONT_FAMILY, 10)
    FONT_BOLD = (FONT_FAMILY, 11, "bold")
    FONT_TITLE = (FONT_FAMILY, 14, "bold")

    @staticmethod
    def apply_styles():
        style = ttk.Style()
        style.theme_use('clam')

        # --- General Widget Styling ---
        style.configure('.',
                        background=StyleManager.COLOR_BACKGROUND,
                        foreground=StyleManager.COLOR_TEXT,
                        font=StyleManager.FONT_NORMAL,
                        borderwidth=0,
                        focuscolor=StyleManager.COLOR_BACKGROUND)

        # --- Frame/Card Styling ---
        style.configure('Card.TFrame',
                        background=StyleManager.COLOR_CARD,
                        relief='solid',
                        borderwidth=1)

        # --- Label Styling ---
        style.configure('TLabel', background=StyleManager.COLOR_BACKGROUND)
        style.configure('Card.TLabel', background=StyleManager.COLOR_CARD)
        style.configure('Title.TLabel', font=StyleManager.FONT_TITLE, background=StyleManager.COLOR_CARD)
        style.configure('Bold.TLabel', font=StyleManager.FONT_BOLD, background=StyleManager.COLOR_CARD)

        # --- Entry Styling ---
        style.configure('TEntry',
                        fieldbackground=StyleManager.COLOR_ENTRY_BG,
                        foreground=StyleManager.COLOR_TEXT,
                        insertcolor=StyleManager.COLOR_TEXT,
                        borderwidth=1,
                        relief='solid')
        style.map('TEntry',
                  bordercolor=[('focus', StyleManager.COLOR_PRIMARY), ('!focus', StyleManager.COLOR_BORDER)],
                  relief=[('focus', 'solid'), ('!focus', 'solid')])

        # --- Button Styling ---
        style.configure('TButton',
                        background=StyleManager.COLOR_PRIMARY,
                        foreground="#ffffff",
                        font=StyleManager.FONT_BOLD,
                        padding=(10, 5))
        style.map('TButton',
                  background=[('active', '#005f9e')],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        # --- Combobox (Dropdown) Styling ---
        style.configure('TCombobox',
                        fieldbackground=StyleManager.COLOR_ENTRY_BG,
                        background=StyleManager.COLOR_ENTRY_BG,
                        foreground=StyleManager.COLOR_TEXT,
                        arrowcolor=StyleManager.COLOR_TEXT,
                        insertcolor=StyleManager.COLOR_TEXT,
                        bordercolor=StyleManager.COLOR_BORDER)
        style.map('TCombobox',
                  background=[('readonly', StyleManager.COLOR_ENTRY_BG)],
                  fieldbackground=[('readonly', StyleManager.COLOR_ENTRY_BG)])

class DataHandler:
    """Handles loading and saving of tracking data."""
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_filepath(self, year):
        return os.path.join(self.data_dir, f"{year}.json")

    def load_year_data(self, year):
        filepath = self._get_filepath(year)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {} # Handle corrupted file
        return {}

    def get_data_for_date(self, selected_date):
        year_data = self.load_year_data(selected_date.year)
        return year_data.get(selected_date.strftime('%Y-%m-%d'), {})

    def save_data_for_date(self, selected_date, data):
        year = selected_date.year
        year_data = self.load_year_data(year)
        date_key = selected_date.strftime('%Y-%m-%d')
        year_data[date_key] = data

        filepath = self._get_filepath(year)
        with open(filepath, 'w') as f:
            json.dump(year_data, f, indent=4)

class HabitTrackerApp(tk.Tk):
    """The main application class for the Habit & Finance Tracker."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(GEOMETRY)
        self.configure(bg=StyleManager.COLOR_BACKGROUND)
        self.resizable(False, False)

        StyleManager.apply_styles()
        self.data_handler = DataHandler(DATA_DIR)
        
        self.selected_date = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        
        # --- UI Variables ---
        self.vars = {
            'morning_juice': tk.StringVar(value="No"),
            'water_intake': tk.StringVar(),
            'sleep_hours': tk.StringVar(),
            'self_improvement_time': tk.StringVar(),
            'education_time': tk.StringVar(),
            'github_commits': tk.StringVar(),
            'linkedin_posts': tk.StringVar(),
            'linkedin_engagement': tk.StringVar(),
            'facebook_posts': tk.StringVar(),
            'facebook_engagement': tk.StringVar(),
            'instagram_posts': tk.StringVar(),
            'instagram_engagement': tk.StringVar(),
            'money_earned': tk.StringVar(),
            'money_spent': tk.StringVar(),
            'notes': tk.StringVar()
        }

        self._create_main_layout()
        self._create_widgets()
        self.load_data_for_date()

    def _create_main_layout(self):
        """Creates the main scrolling canvas and frames for the UI."""
        main_frame = ttk.Frame(self, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        self.header_frame.pack(fill='x', padx=10, pady=(10, 5))

        self.content_frame = ttk.Frame(main_frame, style='Card.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.footer_frame = ttk.Frame(main_frame, style='Card.TFrame')
        self.footer_frame.pack(fill='x', padx=10, pady=(5, 10))

    def _create_widgets(self):
        """Creates all the UI widgets for data entry."""
        self._create_header()
        self._create_category_cards()
        self._create_footer()

    def _create_header(self):
        """Creates the date selection and title header."""
        header_content_frame = ttk.Frame(self.header_frame, style='Card.TFrame')
        header_content_frame.pack(fill='x', expand=True, padx=10, pady=10)
        header_content_frame.columnconfigure(1, weight=1)

        ttk.Label(header_content_frame, text="Date:", style='Bold.TLabel').grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        
        date_frame = ttk.Frame(header_content_frame, style='Card.TFrame')
        date_frame.grid(row=0, column=1, sticky='ew')

        today = date.today()
        self.year_var = tk.StringVar(value=today.year)
        self.month_var = tk.StringVar(value=today.month)
        self.day_var = tk.StringVar(value=today.day)

        year_cb = ttk.Combobox(date_frame, textvariable=self.year_var, values=[y for y in range(today.year - 5, today.year + 2)], width=6)
        month_cb = ttk.Combobox(date_frame, textvariable=self.month_var, values=[m for m in range(1, 13)], width=4)
        day_cb = ttk.Combobox(date_frame, textvariable=self.day_var, values=[d for d in range(1, 32)], width=4)

        year_cb.pack(side='left', padx=2)
        month_cb.pack(side='left', padx=2)
        day_cb.pack(side='left', padx=2)

        for cb in (year_cb, month_cb, day_cb):
            cb.bind('<<ComboboxSelected>>', self.update_and_load_data)
            cb.bind('<KeyRelease>', self.update_and_load_data)

    def _create_category_cards(self):
        """Creates frames for each data category."""
        # Use grid for flexible card layout
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        
        finance_card = self._create_card("Finance (Daily)", 0, 0, colspan=2)
        self._add_entry(finance_card, "Money Earned:", self.vars['money_earned'])
        self._add_entry(finance_card, "Money Spent:", self.vars['money_spent'])
        
        health_card = self._create_card("Health & Routine", 1, 0)
        self._add_option(health_card, "Morning Juice:", self.vars['morning_juice'], ["Yes", "No"])
        self._add_entry(health_card, "Water Intake (L):", self.vars['water_intake'])
        self._add_entry(health_card, "Sleep Hours:", self.vars['sleep_hours'])
        
        prod_card = self._create_card("Productivity", 1, 1)
        self._add_entry(prod_card, "Self Improvement (min):", self.vars['self_improvement_time'])
        self._add_entry(prod_card, "Education Time (min):", self.vars['education_time'])
        self._add_entry(prod_card, "GitHub Commits:", self.vars['github_commits'])
        
        social_card = self._create_card("Social Media", 2, 0, colspan=2)
        social_content_frame = ttk.Frame(social_card, style='Card.TFrame')
        social_content_frame.pack(fill='both', expand=True, padx=10, pady=10) # Pack this frame into the main card
        social_content_frame.columnconfigure((1, 3, 5), weight=1)
        self._add_social_entries(social_content_frame, "LinkedIn:", self.vars['linkedin_posts'], self.vars['linkedin_engagement'], 0)
        self._add_social_entries(social_content_frame, "Facebook:", self.vars['facebook_posts'], self.vars['facebook_engagement'], 1)
        self._add_social_entries(social_content_frame, "Instagram:", self.vars['instagram_posts'], self.vars['instagram_engagement'], 2)

        notes_card = self._create_card("Notes", 3, 0, colspan=2)
        notes_entry = ttk.Entry(notes_card, textvariable=self.vars['notes'], style='TEntry', width=60)
        notes_entry.pack(fill='x', expand=True, padx=10, pady=(0, 10))

    def _create_card(self, title, row, col, colspan=1):
        """Helper to create a styled card frame."""
        card = ttk.Frame(self.content_frame, style='Card.TFrame', borderwidth=1, relief='solid')
        card.grid(row=row, column=col, columnspan=colspan, sticky='nsew', padx=10, pady=10)
        
        title_label = ttk.Label(card, text=title, style='Title.TLabel')
        title_label.pack(fill='x', padx=10, pady=(5, 10))
        return card

    def _add_entry(self, parent, label_text, string_var):
        """Helper to add a label and entry to a card."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame, text=label_text, style='Card.TLabel').pack(side='left', anchor='w')
        ttk.Entry(frame, textvariable=string_var, style='TEntry', width=15).pack(side='right')

    def _add_option(self, parent, label_text, string_var, options):
        """Helper to add a label and combobox (dropdown) to a card."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame, text=label_text, style='Card.TLabel').pack(side='left', anchor='w')
        ttk.Combobox(frame, textvariable=string_var, values=options, state='readonly', width=13).pack(side='right')

    def _add_social_entries(self, parent, label_text, posts_var, engagement_var, row):
        """Helper for the social media card layout."""
        ttk.Label(parent, text=label_text, style='Bold.TLabel').grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        ttk.Label(parent, text="Posts:", style='Card.TLabel').grid(row=row, column=1, sticky='e', padx=(10, 2))
        ttk.Entry(parent, textvariable=posts_var, width=8).grid(row=row, column=2, sticky='w')
        
        ttk.Label(parent, text="Time (min):", style='Card.TLabel').grid(row=row, column=3, sticky='e', padx=(10, 2))
        ttk.Entry(parent, textvariable=engagement_var, width=8).grid(row=row, column=4, sticky='w')

    def _create_footer(self):
        """Creates the save button and analysis button."""
        ttk.Button(self.footer_frame, text="Show Analysis", command=self.show_analysis).pack(side='left', padx=10, pady=10)
        ttk.Button(self.footer_frame, text="Save Data", command=self.save_data, style='TButton').pack(side='right', padx=10, pady=10)

    def update_and_load_data(self, event=None):
        try:
            d = date(int(self.year_var.get()), int(self.month_var.get()), int(self.day_var.get()))
            self.selected_date.set(d.strftime('%Y-%m-%d'))
            self.load_data_for_date()
        except (ValueError, TypeError):
            # Handles invalid date combinations during entry
            self.clear_form()

    def load_data_for_date(self):
        """Loads data for the selected date and populates the form."""
        self.clear_form()
        try:
            selected_date_obj = datetime.strptime(self.selected_date.get(), '%Y-%m-%d').date()
            data = self.data_handler.get_data_for_date(selected_date_obj)
            for key, var in self.vars.items():
                if key in data:
                    var.set(data[key])
        except ValueError:
            pass # Ignore if date is invalid

    def save_data(self):
        """Validates and saves the current form data."""
        try:
            selected_date_obj = datetime.strptime(self.selected_date.get(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date.")
            return

        data_to_save = {}
        # Validate and collect data
        for key, var in self.vars.items():
            value = var.get()
            # All fields are optional except the Y/N dropdown
            if value:
                # Validate numeric fields
                if key not in ['morning_juice', 'notes']:
                    try:
                        num_val = float(value)
                        if num_val < 0:
                            raise ValueError("Negative value")
                        # Store as int if it's a whole number
                        data_to_save[key] = int(num_val) if num_val.is_integer() else num_val
                    except ValueError:
                        messagebox.showerror("Invalid Input", f"Please enter a valid non-negative number for '{key.replace('_', ' ').title()}'.")
                        return
                else:
                     data_to_save[key] = value
            # For the dropdown, always save its value
            elif key == 'morning_juice':
                data_to_save[key] = self.vars['morning_juice'].get()


        self.data_handler.save_data_for_date(selected_date_obj, data_to_save)
        messagebox.showinfo("Success", f"Data saved for {selected_date_obj.strftime('%Y-%m-%d')}.")

    def clear_form(self):
        """Clears all entry fields in the form."""
        for key, var in self.vars.items():
            if key != 'morning_juice':
                var.set("")
        self.vars['morning_juice'].set("No")
        
    def show_analysis(self):
        """Shows a new window with data analysis."""
        AnalysisWindow(self, self.data_handler)


class AnalysisWindow(tk.Toplevel):
    """A window to display monthly and yearly analysis."""
    def __init__(self, master, data_handler):
        super().__init__(master)
        self.title("Data Analysis")
        self.geometry("600x450")
        self.configure(bg=StyleManager.COLOR_BACKGROUND)
        self.data_handler = data_handler
        
        self.transient(master)
        self.grab_set()

        StyleManager.apply_styles()

        # --- Controls ---
        control_frame = ttk.Frame(self, style='Card.TFrame')
        control_frame.pack(pady=10, padx=10, fill='x')

        today = date.today()
        self.year_var = tk.StringVar(value=today.year)
        self.month_var = tk.StringVar(value=today.strftime('%B'))
        
        months = [date(2000, m, 1).strftime('%B') for m in range(1, 13)]
        
        ttk.Label(control_frame, text="Year:", style='Card.TLabel').pack(side='left', padx=5)
        ttk.Combobox(control_frame, textvariable=self.year_var, values=[y for y in range(today.year - 5, today.year + 1)], width=6).pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Month:", style='Card.TLabel').pack(side='left', padx=5)
        ttk.Combobox(control_frame, textvariable=self.month_var, values=["All"] + months, width=10).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Generate Report", command=self.generate_report).pack(side='left', padx=10)

        # --- Display Area ---
        self.report_text = tk.Text(self, wrap='word', height=20, width=70,
                                   bg=StyleManager.COLOR_CARD, fg=StyleManager.COLOR_TEXT,
                                   font=StyleManager.FONT_NORMAL, relief='sunken', borderwidth=1,
                                   highlightbackground=StyleManager.COLOR_BORDER)
        self.report_text.pack(pady=10, padx=10, fill='both', expand=True)
        self.report_text.config(state='disabled')

    def generate_report(self):
        year = int(self.year_var.get())
        month_str = self.month_var.get()
        
        year_data = self.data_handler.load_year_data(year)
        
        if not year_data:
            self.display_report(f"No data found for the year {year}.")
            return

        if month_str == "All":
            self.run_yearly_analysis(year, year_data)
        else:
            month_num = datetime.strptime(month_str, '%B').month
            self.run_monthly_analysis(year, month_num, month_str, year_data)

    def run_monthly_analysis(self, year, month_num, month_str, year_data):
        report_data = {
            'earned': 0, 'spent': 0, 'study_time': 0,
            'improvement_time': 0, 'entries': 0
        }
        
        for date_str, data in year_data.items():
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if entry_date.month == month_num:
                report_data['entries'] += 1
                report_data['earned'] += data.get('money_earned', 0)
                report_data['spent'] += data.get('money_spent', 0)
                report_data['study_time'] += data.get('education_time', 0)
                report_data['improvement_time'] += data.get('self_improvement_time', 0)

        net = report_data['earned'] - report_data['spent']
        total_prod_time = report_data['study_time'] + report_data['improvement_time']
        
        report = (
            f"""--- Monthly Analysis for {month_str} {year} ---

Total Entries: {report_data['entries']}

Financial Summary:
  - Total Earned: ${report_data['earned']:.2f}
  - Total Spent:  ${report_data['spent']:.2f}
  - Net Balance:  ${net:.2f}

Productivity Summary:
  - Total Study Time: {report_data['study_time']} minutes
  - Total Self-Improvement: {report_data['improvement_time']} minutes
  - Combined Total: {total_prod_time} minutes
"""
        )
        self.display_report(report)

    def run_yearly_analysis(self, year, year_data):
        report_data = {
            'earned': 0, 'spent': 0, 'study_time': 0, 'improvement_time': 0,
            'juice_days': 0, 'entries': len(year_data)
        }
        
        for data in year_data.values():
            report_data['earned'] += data.get('money_earned', 0)
            report_data['spent'] += data.get('money_spent', 0)
            report_data['study_time'] += data.get('education_time', 0)
            report_data['improvement_time'] += data.get('self_improvement_time', 0)
            if data.get('morning_juice') == 'Yes':
                report_data['juice_days'] += 1

        net = report_data['earned'] - report_data['spent']
        total_prod_time = report_data['study_time'] + report_data['improvement_time']
        juice_consistency = (report_data['juice_days'] / report_data['entries'] * 100) if report_data['entries'] > 0 else 0
        
        report = (
            f"""--- Yearly Analysis for {year} ---

Total Days with Entries: {report_data['entries']}

Financial Summary:
  - Total Earned: ${report_data['earned']:.2f}
  - Total Spent:  ${report_data['spent']:.2f}
  - Net Balance:  ${net:.2f}

Productivity Summary:
  - Total Study Time: {report_data['study_time']} minutes
  - Total Self-Improvement: {report_data['improvement_time']} minutes
  - Combined Total: {total_prod_time} minutes

Habit Consistency:
  - Morning Healthy Juice: {juice_consistency:.1f}% ({report_data['juice_days']}/{report_data['entries']} days)
"""
        )
        self.display_report(report)

    def display_report(self, report_content):
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report_content)
        self.report_text.config(state='disabled')


if __name__ == "__main__":
    app = HabitTrackerApp()
    app.mainloop()
