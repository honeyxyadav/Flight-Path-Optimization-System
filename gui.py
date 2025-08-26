import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from flight_opt.constraints import RoutingConfig
from flight_opt.data.sample_data import (
    AIRPORTS,
    NO_FLY_ZONES,
    WEATHER_EDGE_PENALTY_KM,
    PREFERRED_HUBS,
)
from flight_opt.routing import find_optimal_route
from flight_opt.visualize import plot_route

class ModernButton(tk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )

class KPICard(tk.Frame):
    def __init__(self, parent, title, value, icon="", color="#3B82F6", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#1F2937", relief="flat", borderwidth=0)
        
        # Icon and title frame
        header_frame = tk.Frame(self, bg="#1F2937")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        if icon:
            icon_label = tk.Label(header_frame, text=icon, font=("Segoe UI", 16), 
                                fg=color, bg="#1F2937")
            icon_label.pack(side="left")
        
        title_label = tk.Label(header_frame, text=title, font=("Segoe UI", 10), 
                              fg="#9CA3AF", bg="#1F2937")
        title_label.pack(side="left", padx=(10, 0))
        
        # Value
        value_label = tk.Label(self, text=value, font=("Segoe UI", 24, "bold"), 
                              fg="white", bg="#1F2937")
        value_label.pack(pady=(0, 15))

class IndianAirspaceGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Indian Airspace Management - Flight Path Optimization System")
        self.geometry("1200x800")
        self.configure(bg="#0F172A")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Custom.TFrame', background='#0F172A')
        self.style.configure('Custom.TNotebook', background='#0F172A')
        self.style.configure('Custom.TNotebook.Tab', background='#1F2937', foreground='white')
        self.style.configure('Custom.TNotebook.Tab', padding=[20, 10])
        
        self.setup_variables()
        self.create_header()
        self.create_notebook()
        self.create_footer()
        
    def setup_variables(self):
        self.origin_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.aircraft_var = tk.StringVar()
        self.max_leg_var = tk.DoubleVar(value=6000.0)
        self.hub_bonus_var = tk.DoubleVar(value=-50.0)
        self.no_fly_var = tk.BooleanVar(value=True)
        self.weather_var = tk.BooleanVar(value=True)
        
        # Sample data for Indian airports
        self.indian_airports = ["DEL", "BOM", "BLR", "MAA", "HYD", "CCU", "AMD", "PNQ", "GOI", "COK"]
        self.aircraft_types = ["Airbus A320", "Boeing 737", "Airbus A350", "Boeing 777", "Airbus A380"]
        
    def create_header(self):
        header_frame = tk.Frame(self, bg="#0F172A", height=100)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_frame, bg="#0F172A")
        left_frame.pack(side="left")
        
        logo_label = tk.Label(left_frame, text="✈️", font=("Segoe UI", 24), 
                             fg="#3B82F6", bg="#0F172A")
        logo_label.pack(side="left")
        
        title_frame = tk.Frame(left_frame, bg="#0F172A")
        title_frame.pack(side="left", padx=15)
        
        main_title = tk.Label(title_frame, text="Indian Airspace Management", 
                             font=("Segoe UI", 20, "bold"), fg="white", bg="#0F172A")
        main_title.pack(anchor="w")
        
        subtitle = tk.Label(title_frame, text="Flight Path Optimization System", 
                           font=("Segoe UI", 12), fg="#9CA3AF", bg="#0F172A")
        subtitle.pack(anchor="w")
        
        # Right side - Status buttons
        right_frame = tk.Frame(header_frame, bg="#0F172A")
        right_frame.pack(side="right")
        
        live_btn = ModernButton(right_frame, text="Live System", 
                               bg="#3B82F6", fg="white", font=("Segoe UI", 10, "bold"))
        live_btn.pack(side="right", padx=(10, 0))
        
        active_flights_btn = ModernButton(right_frame, text="3 Active Flights", 
                                        bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"))
        active_flights_btn.pack(side="right")
        
    def create_notebook(self):
        self.notebook = ttk.Notebook(self, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.overview_frame, text="Overview")
        self.create_overview_tab()
        
        # Optimization tab
        self.optimization_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.optimization_frame, text="Optimization")
        self.create_optimization_tab()
        
        # Analytics tab
        self.analytics_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.analytics_frame, text="Analytics")
        self.create_analytics_tab()
        
    def create_overview_tab(self):
        # Main title and description
        title_frame = tk.Frame(self.overview_frame, bg="#0F172A")
        title_frame.pack(fill="x", pady=(20, 30))
        
        globe_label = tk.Label(title_frame, text="🌍⚡", font=("Segoe UI", 32), 
                              fg="#60A5FA", bg="#0F172A")
        globe_label.pack()
        
        
        # Highlight "Optimization" in blue
        title_text = "Advanced Flight Path Optimization"
        title_label = tk.Label(title_frame, text=title_text, font=("Segoe UI", 28, "bold"), 
                              fg="white", bg="#0F172A")
        title_label.pack()
        
        description = tk.Label(title_frame, 
                              text="Real-time route optimization using A* pathfinding algorithm for Indian airspace.", 
                              font=("Segoe UI", 14), fg="#60A5FA", bg="#0F172A")
        description.pack(pady=(5, 10))
        
        sub_description = tk.Label(title_frame, 
                                 text="Minimize fuel consumption, reduce flight time, and optimize traffic flow.", 
                                 font=("Segoe UI", 12), fg="#9CA3AF", bg="#0F172A")
        sub_description.pack()
        
        # KPI Cards
        kpi_frame = tk.Frame(self.overview_frame, bg="#0F172A")
        kpi_frame.pack(fill="x", pady=30)
        
        # Create 4 KPI cards in a row
        kpi_cards = [
            ("🎯", "95%", "Route Efficiency"),
            ("📈", "15%", "Fuel Savings"),
            ("✈️", "100+", "Daily Flights"),
            ("📊", "₹2.5M", "Cost Savings")
        ]
        
        for i, (icon, value, title) in enumerate(kpi_cards):
            card = KPICard(kpi_frame, title, value, icon, color="#F59E0B" if i == 2 else "#3B82F6")
            card.pack(side="left", fill="both", expand=True, padx=(0, 15))
            
    def create_optimization_tab(self):
        # Title
        title_frame = tk.Frame(self.optimization_frame, bg="#0F172A")
        title_frame.pack(fill="x", pady=(20, 30))
        
        title = tk.Label(title_frame, text="Route Planning & Optimization", 
                        font=("Segoe UI", 24, "bold"), fg="white", bg="#0F172A")
        title.pack(side="left")
        
        gear_label = tk.Label(title_frame, text="⚙️", font=("Segoe UI", 24), 
                             fg="#3B82F6", bg="#0F172A")
        gear_label.pack(side="left", padx=15)
        
        # Input form
        form_frame = tk.Frame(self.optimization_frame, bg="#0F172A")
        form_frame.pack(fill="x", pady=20)
        
        # Origin
        origin_frame = tk.Frame(form_frame, bg="#0F172A")
        origin_frame.pack(fill="x", pady=15)
        
        origin_label = tk.Label(origin_frame, text="Origin", font=("Segoe UI", 12, "bold"), 
                               fg="white", bg="#0F172A")
        origin_label.pack(anchor="w")
        
        self.origin_cb = ttk.Combobox(origin_frame, textvariable=self.origin_var, 
                                     values=self.indian_airports, state="readonly", 
                                     font=("Segoe UI", 12))
        self.origin_cb.pack(fill="x", pady=(5, 0))
        self.origin_cb.set("Select origin airport")
        
        # Destination
        dest_frame = tk.Frame(form_frame, bg="#0F172A")
        dest_frame.pack(fill="x", pady=15)
        
        dest_label = tk.Label(dest_frame, text="Destination", font=("Segoe UI", 12, "bold"), 
                             fg="white", bg="#0F172A")
        dest_label.pack(anchor="w")
        
        self.dest_cb = ttk.Combobox(dest_frame, textvariable=self.dest_var, 
                                   values=self.indian_airports, state="readonly", 
                                   font=("Segoe UI", 12))
        self.dest_cb.pack(fill="x", pady=(5, 0))
        self.dest_cb.set("Select destination airport")
        
        # Aircraft Type
        aircraft_frame = tk.Frame(form_frame, bg="#0F172A")
        aircraft_frame.pack(fill="x", pady=15)
        
        aircraft_label = tk.Label(aircraft_frame, text="Aircraft Type", font=("Segoe UI", 12, "bold"), 
                                 fg="white", bg="#0F172A")
        aircraft_label.pack(anchor="w")
        
        self.aircraft_cb = ttk.Combobox(aircraft_frame, textvariable=self.aircraft_var, 
                                       values=self.aircraft_types, state="readonly", 
                                       font=("Segoe UI", 12))
        self.aircraft_cb.pack(fill="x", pady=(5, 0))
        self.aircraft_cb.set("Select aircraft")
        
        # Optimize button
        button_frame = tk.Frame(self.optimization_frame, bg="#0F172A")
        button_frame.pack(fill="x", pady=30)
        
        optimize_btn = ModernButton(button_frame, text="⚡ Optimize Flight Path", 
                                   bg="#3B82F6", fg="white", font=("Segoe UI", 14, "bold"),
                                   command=self.optimize_flight_path)
        optimize_btn.pack()
        
    def create_analytics_tab(self):
        # Create a matplotlib figure for analytics
        fig = Figure(figsize=(10, 6), facecolor='#0F172A')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0F172A')
        
        # Sample data for Indian cities
        cities = ['Delhi (DEL)', 'Mumbai (BOM)', 'Bangalore (BLR)', 'Chennai (MAA)']
        flights = [25, 22, 18, 15]
        
        bars = ax.bar(cities, flights, color=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
        ax.set_title('Daily Flight Count by City', color='white', fontsize=16, pad=20)
        ax.set_xlabel('Cities', color='white', fontsize=12)
        ax.set_ylabel('Flights per Day', color='white', fontsize=12)
        ax.tick_params(colors='white')
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, flight in zip(bars, flights):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{flight}', ha='center', va='bottom', color='white', fontweight='bold')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.analytics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#0F172A", height=120)
        footer_frame.pack(fill="x", padx=20, pady=20)
        footer_frame.pack_propagate(False)
        
        # System name and description
        left_footer = tk.Frame(footer_frame, bg="#0F172A")
        left_footer.pack(side="left")
        
        footer_logo = tk.Label(left_footer, text="✈️", font=("Segoe UI", 20), 
                              fg="#3B82F6", bg="#0F172A")
        footer_logo.pack(side="left")
        
        footer_text_frame = tk.Frame(left_footer, bg="#0F172A")
        footer_text_frame.pack(side="left", padx=15)
        
        system_name = tk.Label(footer_text_frame, text="Indian Airspace Management System", 
                              font=("Segoe UI", 16, "bold"), fg="white", bg="#0F172A")
        system_name.pack(anchor="w")
        
        system_desc = tk.Label(footer_text_frame, 
                              text="Advanced flight path optimization using AI-powered algorithms for enhanced aviation efficiency", 
                              font=("Segoe UI", 10), fg="#9CA3AF", bg="#0F172A", wraplength=400)
        system_desc.pack(anchor="w", pady=(5, 0))
        
        # Features list
        features_frame = tk.Frame(footer_frame, bg="#0F172A")
        features_frame.pack(side="left", padx=(50, 0))
        
        features = ["Real-time Optimization", "A* Pathfinding Algorithm", "Fuel Efficiency Analysis", "Traffic Flow Management"]
        for feature in features:
            feature_label = tk.Label(features_frame, text=f"• {feature}", 
                                   font=("Segoe UI", 10), fg="#60A5FA", bg="#0F172A")
            feature_label.pack(anchor="w", pady=2)
            
    def optimize_flight_path(self):
        if not self.origin_var.get() or not self.dest_var.get() or not self.aircraft_var.get():
            messagebox.showwarning("Input Required", "Please select origin, destination, and aircraft type.")
            return
            
        try:
            # Use the existing routing logic
            preferred = {c.strip().upper() for c in PREFERRED_HUBS if c.strip()}
            config = RoutingConfig(
                max_leg_km=float(self.max_leg_var.get()),
                preferred_hubs=preferred,
                hub_bonus_km=float(self.hub_bonus_var.get()),
                no_fly_zones=NO_FLY_ZONES if self.no_fly_var.get() else [],
                weather_edge_penalty_km=WEATHER_EDGE_PENALTY_KM if self.weather_var.get() else {},
            )
            
            res = find_optimal_route(
                AIRPORTS,
                self.origin_var.get().upper(),
                self.dest_var.get().upper(),
                config,
            )
            
            # Show results in a new window
            self.show_results(res)
            
        except Exception as e:
            messagebox.showerror("Optimization Error", str(e))
            
    def show_results(self, result):
        results_window = tk.Toplevel(self)
        results_window.title("Flight Path Optimization Results")
        results_window.geometry("600x400")
        results_window.configure(bg="#0F172A")
        
        # Title
        title = tk.Label(results_window, text="Optimization Results", 
                        font=("Segoe UI", 18, "bold"), fg="white", bg="#0F172A")
        title.pack(pady=20)
        
        # Results frame
        results_frame = tk.Frame(results_window, bg="#1F2937", relief="flat", borderwidth=1)
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Path
        path_text = f"Path: {' → '.join(result.path)}"
        path_label = tk.Label(results_frame, text=path_text, font=("Segoe UI", 12, "bold"), 
                             fg="white", bg="#1F2937")
        path_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Metrics
        metrics_frame = tk.Frame(results_frame, bg="#1F2937")
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        total_distance = tk.Label(metrics_frame, text=f"Total Distance: {result.total_distance_km:.0f} km", 
                                 font=("Segoe UI", 11), fg="#9CA3AF", bg="#1F2937")
        total_distance.pack(anchor="w")
        
        total_cost = tk.Label(metrics_frame, text=f"Total Cost: {result.total_cost_km:.0f} km", 
                             font=("Segoe UI", 11), fg="#9CA3AF", bg="#1F2937")
        total_cost.pack(anchor="w")
        
        # Show plot
        try:
            plot_route(
                AIRPORTS,
                result.path,
                NO_FLY_ZONES,
                title=f"{self.origin_var.get().upper()} to {self.dest_var.get().upper()}",
                outfile=None,
                show=True,
            )
        except Exception as e:
            print(f"Error showing plot: {e}")

def main():
    app = IndianAirspaceGUI()
    app.mainloop()

if __name__ == "__main__":
    main()

