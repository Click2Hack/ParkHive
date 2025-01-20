import tkinter as tk
from tkinter import messagebox
import random
import time
from datetime import datetime, timedelta
import threading

# List of luxury cars
luxury_cars = [
    "Rolls Royce", "Bentley", "Ferrari", "Lamborghini", "Porsche",
    "Maserati", "Aston Martin", "Bugatti", "McLaren", "Tesla"
]

# Global variables
slots = {f"Slot {i + 1}": {"status": "Vacant", "start_time": None, "car_name": None, "reserve_time": None, "coordinates": (0, 0), "reserved_minutes": None} for i in range(100)}

# Function to update slot statuses randomly
def update_slots():
    for slot, data in slots.items():
        if data["status"] == "Occupied":
            # Check if the car has been in the slot for more than 20 minutes
            if datetime.now() - data["start_time"] > timedelta(minutes=20):
                data["status"] = "Vacant"
                data["car_name"] = None
                data["start_time"] = None
                data["reserve_time"] = None
                data["reserved_minutes"] = None
             #   messagebox.showinfo("Car Removed", f"{slot} has been emptied after 20 minutes.")

    # Randomly occupy a space for 10 seconds and vacate it after 3 seconds
    threading.Timer(3, random_occupy_space).start()

    # Refresh the display every second
    threading.Timer(1, update_slots).start()
    update_display()

# Function to randomly occupy a space for 10 seconds
def random_occupy_space():
    vacant_slots = [slot for slot, data in slots.items() if data["status"] == "Vacant"]
    if vacant_slots:
        slot = random.choice(vacant_slots)
        slots[slot]["status"] = "Occupied"
        slots[slot]["car_name"] = random.choice(luxury_cars)
        slots[slot]["start_time"] = datetime.now() - timedelta(minutes=random.randint(1, 20))
        # Vacate the space after 3 seconds
        threading.Timer(25, vacate_random_slot, args=[slot]).start()

# Function to vacate the random slot after 3 seconds
def vacate_random_slot(slot):
    slots[slot]["status"] = "Vacant"
    slots[slot]["car_name"] = None
    slots[slot]["start_time"] = None
    update_display()

# Function to reserve a slot for specific minutes
def reserve_slot(slot, minutes):
    if slots[slot]["status"] == "Vacant":
        slots[slot]["status"] = "Reserved"
        slots[slot]["reserve_time"] = datetime.now() + timedelta(seconds=minutes * 60)  # Reservation time in minutes
        slots[slot]["reserved_minutes"] = minutes
        slots[slot]["car_name"] = None  # Remove car name as it's reserved
        slots[slot]["coordinates"] = get_coordinates(slot)
        update_display()
        messagebox.showinfo("Reservation", f"Slot {slot} reserved for {minutes} minutes at {slots[slot]['coordinates']}")
        start_reservation_timer(slot, minutes)
    else:
        messagebox.showerror("Error", f"{slot} is not available for reservation.")

# Function to modify the occupied time of a slot
def modify_occupied_time(slot):
    if slots[slot]["status"] == "Occupied":
        minutes = simple_input("Modify Occupied Time", "Enter the new parking duration in minutes:")
        if minutes:
            slots[slot]["start_time"] = datetime.now() - timedelta(minutes=minutes)
            update_display()
            messagebox.showinfo("Updated Time", f"Occupied time for {slot} has been updated.")
    else:
        messagebox.showerror("Error", f"{slot} is not currently occupied.")

# Function to automatically unreserve after the specified time
def start_reservation_timer(slot, minutes):
    def timer_thread():
        time_left = minutes * 60
        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            if slots[slot]["status"] == "Occupied":
                return
        # If the slot is not occupied within the reserved time, show vacant again
        if slots[slot]["status"] == "Reserved":
            slots[slot]["status"] = "Vacant"
            slots[slot]["reserve_time"] = None
            update_display()
            messagebox.showinfo("Timeout", f"{slot} reservation time has expired.")
    threading.Thread(target=timer_thread, daemon=True).start()

# Function to confirm arrival and mark as occupied
def confirm_arrival(slot):
    if slots[slot]["status"] == "Reserved":
        slots[slot]["status"] = "Occupied"
        slots[slot]["car_name"] = random.choice(luxury_cars)
        slots[slot]["start_time"] = datetime.now() - timedelta(minutes=random.randint(1, 60))
        update_display()
    else:
        messagebox.showerror("Error", f"{slot} was not reserved.")

# Function to unreserve a slot
def unreserve_slot(slot):
    if slots[slot]["status"] == "Reserved":
        slots[slot]["status"] = "Vacant"
        slots[slot]["reserve_time"] = None
        update_display()
    else:
        messagebox.showerror("Error", f"{slot} is not reserved.")

# Function to calculate parked time
def calculate_parking_time(start_time):
    if start_time:
        elapsed = datetime.now() - start_time
        minutes = divmod(elapsed.total_seconds(), 60)
        return f"{int(minutes[0])} min"
    return "N/A"

# Function to get the coordinates of the slot
def get_coordinates(slot):
    # Coordinates for each slot (randomly for demonstration purposes)
    slot_index = int(slot.split()[1]) - 1
    row = slot_index // 10
    column = slot_index % 10
    return (row + 1, column + 1)

# Function to show simple input dialog box
def simple_input(title, prompt):
    result = tk.simpledialog.askstring(title, prompt)
    return int(result) if result else None

# Function to update the display
def update_display():
    for slot, data in slots.items():
        status = data["status"]
        label = slot_labels[slot]
        if status == "Vacant":
            label["text"] = f"{slot}: {status}"
            label["bg"] = "green"
        elif status == "Occupied":
            parked_time = calculate_parking_time(data["start_time"])
            label["text"] = f"{slot}: {status} ({parked_time})\nCar: {data['car_name']}"
            label["bg"] = "red"
        elif status == "Reserved":
            label["text"] = f"{slot}: {status}\nWaiting for confirmation..."
            label["bg"] = "yellow"

    # Forcefully update and show the list of vacant slots and shortest time occupied slots
    show_vacant_slots()
    show_shortest_time_occupied_slots()

# Function to get the list of vacant slots
def get_vacant_slots():
    return [slot for slot, data in slots.items() if data["status"] == "Vacant"]

# Function to get the shortest time occupied slots
def get_shortest_time_occupied_slots():
    occupied_slots = {slot: data for slot, data in slots.items() if data["status"] == "Occupied"}
    sorted_slots = sorted(occupied_slots.items(), key=lambda x: (datetime.now() - x[1]["start_time"]).total_seconds())
    return sorted_slots[:5]

# Function to show the vacant slots
def show_vacant_slots():
    vacant_slots = get_vacant_slots()
    grid_text = ""
    cols = 5  # Number of columns in the grid
    for i, slot in enumerate(vacant_slots):
        grid_text += f"{slot}  "
        if (i + 1) % cols == 0:  # Break line after every `cols` slots
            grid_text += "\n"
    vacant_list_label.config(text=grid_text)

# Function to show the shortest time occupied slots
def show_shortest_time_occupied_slots():
    shortest_time_slots = get_shortest_time_occupied_slots()
    shortest_time_list_label.config(text="\n".join([f"{slot}: {calculate_parking_time(data['start_time'])}" for slot, data in shortest_time_slots]))

# GUI Setup
root = tk.Tk()
root.title("Smart Parking System Simulation")
root.geometry("800x600")

# Frame for parking slots (Scrollable)
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
frame = tk.Frame(canvas)

canvas.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Labels for slots (100 slots)
slot_labels = {}
for i, slot in enumerate(slots):
    label = tk.Label(frame, text=f"{slot}: {slots[slot]['status']}", font=("Arial", 9), width=14, height=3, bg="green")
    label.grid(row=i % 10, column=(i // 10) * 3, padx=5, pady=5)
    slot_labels[slot] = label

# Frame for buttons and slot interactions
button_frame = tk.Frame(root)
button_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Slot selection dropdown
slot_var = tk.StringVar()
slot_var.set("Select a slot")
slot_dropdown = tk.OptionMenu(button_frame, slot_var, *slots.keys())
slot_dropdown.pack(pady=10)

# Reserve button
reserve_btn = tk.Button(button_frame, text="Reserve Slot", command=lambda: reserve_slot(slot_var.get(), 10))  # Reserve for 10 minutes
reserve_btn.pack(pady=10)

# Unreserve button
unreserve_btn = tk.Button(button_frame, text="Unreserve Slot", command=lambda: unreserve_slot(slot_var.get()))
unreserve_btn.pack(pady=10)

# Refresh button
refresh_btn = tk.Button(button_frame, text="Refresh Slots", command=update_slots, bg="blue", fg="white")
refresh_btn.pack(pady=20)

# List of vacant slots
vacant_slots_label = tk.Label(button_frame, text="Vacant Slots", font=("Arial", 10))
vacant_slots_label.pack(pady=5)

vacant_list_label = tk.Label(button_frame, text="", font=("Arial", 8), width=20, height=10, anchor="nw")
vacant_list_label.pack(pady=5)

# List of shortest time occupied slots
shortest_time_label = tk.Label(button_frame, text="Shortest Time Occupied Slots", font=("Arial", 10))
shortest_time_label.pack(pady=5)

shortest_time_list_label = tk.Label(button_frame, text="", font=("Arial", 8), width=20, height=10, anchor="nw")
shortest_time_list_label.pack(pady=5)

# Start automatic updates
update_slots()

# Run the GUI
root.mainloop()

# Frame for slots
frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")

# Make the frame resizable
frame.rowconfigure(tuple(range(10)), weight=1)  # Rows
frame.columnconfigure(tuple(range(10)), weight=1)  # Columns

# Example slots data
slots = {f"Slot{i}": {"status": "Vacant"} for i in range(100)}

# Labels for slots (100 slots)
slot_labels = {}
for i, slot in enumerate(slots):
    label = tk.Label(frame, text=f"{slot}: {slots[slot]['status']}", font=("Arial", 8), width=10, height=3)
    label.grid(row=i % 10, column=(i // 10) * 3, padx=5, pady=5)
    slot_labels[slot] = label

# Button frame for vacant/occupied lists
button_frame = tk.Frame(root)
button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

vacant_list_label = tk.Label(button_frame, text="", font=("Arial", 8))
vacant_list_label.pack(pady=5, fill=tk.BOTH, expand=True)

shortest_time_list_label = tk.Label(button_frame, text="", font=("Arial", 8))
shortest_time_list_label.pack(pady=5, fill=tk.BOTH, expand=True)

# Allow root to resize dynamically
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Canvas for dynamic content
canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Function to adjust font size dynamically
def adjust_font_size(event):
    width, height = event.width, event.height
    font_size = max(8, int(height / 50))  # Adjust as needed
    for label in slot_labels.values():
        label.config(font=("Arial", font_size))

root.bind("<Configure>", adjust_font_size)

root.mainloop()