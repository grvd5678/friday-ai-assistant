import time
import shutil
import psutil

def get_system_stats() -> str:
    """Fetches comprehensive system hardware diagnostics: CPU, RAM, Disk, and Battery."""
    # Fast CPU sample (interval=0.5s for responsiveness)
    cpu_usage = psutil.cpu_percent(interval=0.5)
    
    # RAM memory
    mem = psutil.virtual_memory()
    ram_used_gb = round(mem.used / (1024 ** 3), 1)
    ram_total_gb = round(mem.total / (1024 ** 3), 1)
    
    # Disk usage for main C: drive
    disk = shutil.disk_usage("C:\\")
    disk_free_gb = round(disk.free / (1024 ** 3), 1)
    disk_total_gb = round(disk.total / (1024 ** 3), 1)
    
    # Battery info
    battery = psutil.sensors_battery()
    if battery:
        plugged = "Plugged in (Charging)" if battery.power_plugged else "Running on Battery"
        bat_str = f"{battery.percent}% ({plugged})"
    else:
        bat_str = "Desktop PC (Continuous AC Power)"
        
    return (
        f"Diagnostic Report: CPU is at {cpu_usage}%. "
        f"RAM: {ram_used_gb} GB used of {ram_total_gb} GB ({mem.percent}%). "
        f"C Drive: {disk_free_gb} GB free of {disk_total_gb} GB. "
        f"Battery: {bat_str}."
    )

def get_battery_status() -> str:
    """Checks battery level and charging state."""
    battery = psutil.sensors_battery()
    if not battery:
        return "System is connected directly to AC power with no battery installed."
    state = "charging" if battery.power_plugged else "discharging"
    return f"Battery is currently at {battery.percent}% and {state}."

def get_datetime_info() -> str:
    """Returns the current date, time, and day of the week."""
    now = time.localtime()
    day_name = time.strftime("%A", now)
    date_str = time.strftime("%B %d, %Y", now)
    time_str = time.strftime("%I:%M %p", now)
    return f"Today is {day_name}, {date_str}, and the time is {time_str}."

if __name__ == "__main__":
    print(get_system_stats())
    print(get_datetime_info())
