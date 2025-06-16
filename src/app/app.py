import tkinter as tk
from tkinter import messagebox
from src.settings.config import get_window_size, get_top_regions_count
from src.core.api_client import search_vacancies
from src.core import data_analysis as da
from src.settings import config
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading


class MainApplication(tk.Tk):
    """
    Main application window that initializes and manages all GUI frames:
    MainMenu, SettingsFrame, and ResultFrame.
    """
    def __init__(self):
        super().__init__()
        width, height = get_window_size()
        self.geometry(f"{width}x{height}")
        self.title("Job Analysis")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenu, SettingsFrame, ResultFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.pack(fill="both", expand=True)
            frame.grid_propagate(False)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame("MainMenu")

    def show_frame(self, name, **kwargs):
        """
        Display the frame with the given name and optional arguments.
        """
        frame = self.frames[name]
        if hasattr(frame, "refresh"):
            frame.refresh(**kwargs)
        frame.tkraise()


class MainMenu(tk.Frame):
    """
    Main menu frame with job title input, and navigation buttons for search,
    settings, and exit.
    """
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        self.entry = tk.Entry(self, fg="gray")
        self.entry.insert(0, "Enter job title")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.place(relx=0.5, rely=0.4, relwidth=0.4, anchor="center")

        self.search_btn = tk.Button(self, text="Search", command=self.search)
        self.search_btn.place(relx=0.5, rely=0.48, relwidth=0.2, anchor="center")

        self.settings_btn = tk.Button(self, text="Settings", command=lambda: controller.show_frame("SettingsFrame"))
        self.exit_btn = tk.Button(self, text="Exit", command=controller.destroy)

        self.settings_btn.place(relx=0.02, rely=0.98, relwidth=0.15, anchor="sw")
        self.exit_btn.place(relx=0.98, rely=0.98, relwidth=0.15, anchor="se")

    def _clear_placeholder(self, event):
        """
        Clear placeholder text when input gains focus.
        """
        if self.entry.get() == "Enter job title":
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")

    def _restore_placeholder(self, event):
        """
        Restore placeholder text if input is empty on focus out.
        """
        if not self.entry.get():
            self.entry.insert(0, "Enter job title")
            self.entry.config(fg="gray")

    def search(self):
        """
        Validate query and trigger transition to ResultFrame with the given query.
        """
        query = self.entry.get().strip()
        if not query or query == "Enter job title":
            messagebox.showwarning("Warning", "Please enter a job title")
            return
        self.controller.show_frame("ResultFrame", query=query)

    def refresh(self, **kwargs):
        """
        Placeholder method for frame refresh logic (if needed).
        """
        pass


class SettingsFrame(tk.Frame):
    """
    Settings frame allowing configuration of salary method, limits, and window size.
    """
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        self.salary_method_var = tk.StringVar()
        self.max_results_var = tk.StringVar()
        self.top_regions_var = tk.StringVar()
        self.top_skills_var = tk.StringVar()
        self.window_size_var = tk.StringVar()

        self.available_resolutions = [
            "800x600", "1024x768", "1280x720", "1280x1024", "1440x900", "1920x1080"
        ]

        self.build_widgets()

    def build_widgets(self):
        """
        Build all widgets for settings interface.
        """
        config_data = config.load_config()
        current_resolution = f"{config_data['window_size'][0]}x{config_data['window_size'][1]}"
        self.salary_method_var.set(config_data.get("salary_calculation_method", "average"))
        self.max_results_var.set(str(config_data.get("max_results_per_request", 10)))
        self.top_regions_var.set(str(config_data.get("top_regions_count", 5)))
        self.top_skills_var.set(str(config_data.get("top_skills_count", 5)))
        self.window_size_var.set(current_resolution)

        start_y = 0.2
        step_y = 0.08
        label_x = 0.05
        input_x = 0.5
        input_width = 0.4

        tk.Label(self, text="Salary calculation method:").place(relx=label_x, rely=start_y, anchor="w")
        tk.OptionMenu(self, self.salary_method_var, "average", "median")\
            .place(relx=input_x, rely=start_y, relwidth=input_width, anchor="w")

        tk.Label(self, text="Max vacancies per request:").place(relx=label_x, rely=start_y + step_y, anchor="w")
        tk.Entry(self, textvariable=self.max_results_var)\
            .place(relx=input_x, rely=start_y + step_y, relwidth=input_width, anchor="w")

        tk.Label(self, text="Top regions:").place(relx=label_x, rely=start_y + 2 * step_y, anchor="w")
        tk.Entry(self, textvariable=self.top_regions_var)\
            .place(relx=input_x, rely=start_y + 2 * step_y, relwidth=input_width, anchor="w")

        tk.Label(self, text="Top skills:").place(relx=label_x, rely=start_y + 3 * step_y, anchor="w")
        tk.Entry(self, textvariable=self.top_skills_var)\
            .place(relx=input_x, rely=start_y + 3 * step_y, relwidth=input_width, anchor="w")

        tk.Label(self, text="Window size:").place(relx=label_x, rely=start_y + 4 * step_y, anchor="w")
        tk.OptionMenu(self, self.window_size_var, *self.available_resolutions)\
            .place(relx=input_x, rely=start_y + 4 * step_y, relwidth=input_width, anchor="w")

        tk.Button(self, text="Save", command=self.save_config)\
            .place(relx=0.5, rely=0.85, relwidth=0.3, anchor="center")

        tk.Button(self, text="Back", command=lambda: self.controller.show_frame("MainMenu"))\
            .place(relx=0.02, rely=0.98, relwidth=0.15, anchor="sw")

    def save_config(self):
        """
        Save all configured settings to config.json.
        """
        try:
            config.save_config({
                "salary_calculation_method": self.salary_method_var.get(),
                "max_results_per_request": int(self.max_results_var.get()),
                "top_regions_count": int(self.top_regions_var.get()),
                "top_skills_count": int(self.top_skills_var.get()),
                "window_size": list(map(int, self.window_size_var.get().split("x")))
            })
            messagebox.showinfo("Success", "Settings saved. Please restart the app to apply window size.")
        except ValueError:
            messagebox.showerror("Error", "Fields must contain positive numbers.")

    def refresh(self, **kwargs):
        """
        Reload all widgets and restore current values from config.
        """
        for widget in self.winfo_children():
            widget.destroy()
        self.build_widgets()

class ResultFrame(tk.Frame):
    """
    Frame that displays job analysis results including:
    salary, top skills, and top regions. Contains a scrollable area
    and a separate bottom navigation area with a 'Back' button.
    """
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        self.top_frame = tk.Frame(self, bg="white")
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.top_frame, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.top_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

        self.bottom_frame = tk.Frame(self, bg="white", height=60)
        self.bottom_frame.pack(side="bottom", fill="x")

        self.back_btn = tk.Button(self.bottom_frame, text="Back", command=lambda: controller.show_frame("MainMenu"))
        self.back_btn.pack(pady=10)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh(self, query):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.scrollable_frame,
            text=f"Query: {query}",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10, anchor="w", padx=100)

        tk.Label(
            self.scrollable_frame,
            text="Loading data...",
            bg="white",
            font=("Arial", 12, "italic")
        ).pack(anchor="w", padx=100)

        threading.Thread(target=self._load_data, args=(query,), daemon=True).start()

    def _load_data(self, query):
        try:
            vacancies = search_vacancies(query)
            skills = da.get_top_skills(vacancies)
            regions = da.get_top_regions(vacancies, get_top_regions_count())
            salary = da.get_salary_statistics(vacancies)
            salary_distribution = da.get_salary_distribution(vacancies)

            self.scrollable_frame.after(
                0, lambda: self._update_ui(salary, skills, regions, salary_distribution)
            )
        except Exception as e:
            self.scrollable_frame.after(
                0,
                lambda e=e: tk.Label(
                    self.scrollable_frame, text=f"Error: {e}", fg="red", font=("Arial", 12)
                ).pack(anchor="w", padx=100, pady=10)
            )

    def _update_ui(self, salary, skills, regions, salary_distribution):
        self._display_salary(salary)
        self._display_salary_histogram(salary_distribution)
        self._display_skills(skills)
        self._display_regions(regions)

    def _display_salary(self, salary):
        tk.Label(self.scrollable_frame, text="Salary", font=("Arial", 14, "bold"), bg="white").pack(
            pady=(10, 5), anchor="w", padx=100
        )
        tk.Label(
            self.scrollable_frame,
            text=f"{round(salary, 2)} RUB",
            font=("Arial", 18),
            bg="white",
            fg="green"
        ).pack(pady=(0, 10), anchor="w", padx=100)

    def _display_salary_histogram(self, salaries):
        if not salaries:
            return

        tk.Label(self.scrollable_frame, text="Salary Distribution", font=("Arial", 14, "bold"), bg="white").pack(
            pady=(10, 5), anchor="w", padx=100
        )

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.hist(salaries, bins=20, color="#4caf50", edgecolor="black")
        ax.set_title("Salary Histogram")
        ax.set_xlabel("Salary (RUB)")
        ax.set_ylabel("Number of Vacancies")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=100, anchor="w")

    def _display_skills(self, skills):
        tk.Label(self.scrollable_frame, text="Skills", font=("Arial", 14, "bold"), bg="white").pack(
            pady=(10, 5), anchor="w", padx=100
        )
        for s, c in skills:
            tk.Label(
                self.scrollable_frame,
                text=f"• {s}: {c}",
                anchor="w",
                bg="white",
                font=("Arial", 12)
            ).pack(fill="x", padx=120)

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh([s for s, _ in reversed(skills)], [c for _, c in reversed(skills)], color="#607d8b")
        ax.set_xlabel("Frequency")
        ax.set_title("Top Skills")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=100, anchor="w")

    def _display_regions(self, regions):
        tk.Label(self.scrollable_frame, text="Regions", font=("Arial", 14, "bold"), bg="white").pack(
            pady=(10, 5), anchor="w", padx=100
        )
        for r, c in regions:
            tk.Label(
                self.scrollable_frame,
                text=f"• {r}: {c}",
                anchor="w",
                bg="white",
                font=("Arial", 12)
            ).pack(fill="x", padx=120)

        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh([r for r, _ in reversed(regions)], [c for _, c in reversed(regions)], color="#3f51b5")
        ax.set_xlabel("Count")
        ax.set_title("Top Regions")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=100, anchor="w")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
