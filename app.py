import tkinter as tk
import subprocess
import getpass
import sys

def check_password():
    password = getpass.getpass("Enter your sudo password: ")

    # Check if the password is correct by running a simple command with sudo
    try:
        result = subprocess.run(['sudo', '-S', 'echo', 'Password correct'], 
                                input=password + '\n', 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                universal_newlines=True)
        if 'Password correct' in result.stdout:
            return password
        else:
            print("Incorrect password. Please try again.")
            return check_password()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

class ServerControlApp:
    def __init__(self, root, sudo_password):
        self.root = root
        self.root.title("Server Control")
        self.sudo_password = sudo_password

        self.mysql_status = tk.StringVar()
        self.apache_status = tk.StringVar()
        self.mongodb_status = tk.StringVar()
        self.mysql_disable_startup = tk.BooleanVar()
        self.apache_disable_startup = tk.BooleanVar()
        self.mongodb_disable_startup = tk.BooleanVar()

        # Labels
        tk.Label(root, text="MySQL Server:").grid(row=0, column=0, sticky="w")
        tk.Label(root, text="Apache Server:").grid(row=1, column=0, sticky="w")
        tk.Label(root, text="MongoDB Server:").grid(row=2, column=0, sticky="w")

        # Status
        tk.Label(root, textvariable=self.mysql_status).grid(row=0, column=1)
        tk.Label(root, textvariable=self.apache_status).grid(row=1, column=1)
        tk.Label(root, textvariable=self.mongodb_status).grid(row=2, column=1)

        # Buttons
        tk.Button(root, text="Start MySQL", command=self.start_mysql).grid(row=0, column=2)
        tk.Button(root, text="Stop MySQL", command=self.stop_mysql).grid(row=0, column=3)
        tk.Button(root, text="Start Apache", command=self.start_apache).grid(row=1, column=2)
        tk.Button(root, text="Stop Apache", command=self.stop_apache).grid(row=1, column=3)
        tk.Button(root, text="Start MongoDB", command=self.start_mongodb).grid(row=2, column=2)
        tk.Button(root, text="Stop MongoDB", command=self.stop_mongodb).grid(row=2, column=3)

        # Disable on Startup
        tk.Checkbutton(root, text="Disable MySQL on Startup", variable=self.mysql_disable_startup, command=self.toggle_mysql_startup).grid(row=3, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(root, text="Disable Apache on Startup", variable=self.apache_disable_startup, command=self.toggle_apache_startup).grid(row=4, column=0, columnspan=2, sticky="w")
        tk.Checkbutton(root, text="Disable MongoDB on Startup", variable=self.mongodb_disable_startup, command=self.toggle_mongodb_startup).grid(row=5, column=0, columnspan=2, sticky="w")

        # Check Status Button
        tk.Button(root, text="Check Status", command=self.check_status).grid(row=6, column=0, columnspan=4)

        # Initial Status Check
        self.check_status()
        self.check_startup_status()

    def check_status(self):
        self.mysql_status.set(self.get_service_status("mysql"))
        self.apache_status.set(self.get_service_status("apache2"))
        self.mongodb_status.set(self.get_service_status("mongod"))

    def check_startup_status(self):
        self.mysql_disable_startup.set(not self.is_service_enabled_on_startup("mysql"))
        self.apache_disable_startup.set(not self.is_service_enabled_on_startup("apache2"))
        self.mongodb_disable_startup.set(not self.is_service_enabled_on_startup("mongod"))

    def get_service_status(self, service_name):
        result = subprocess.run(["systemctl", "is-active", service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "Running" if result.stdout.strip() == "active" else "Stopped"

    def is_service_enabled_on_startup(self, service_name):
        result = subprocess.run(["systemctl", "is-enabled", service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip() == "enabled"

    def run_command_with_sudo(self, command):
        result = subprocess.run(['sudo', '-S'] + command, input=self.sudo_password + '\n', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result

    def start_mysql(self):
        self.run_command_with_sudo(["systemctl", "start", "mysql"])
        self.check_status()

    def stop_mysql(self):
        self.run_command_with_sudo(["systemctl", "stop", "mysql"])
        self.check_status()

    def start_apache(self):
        self.run_command_with_sudo(["systemctl", "start", "apache2"])
        self.check_status()

    def stop_apache(self):
        self.run_command_with_sudo(["systemctl", "stop", "apache2"])
        self.check_status()

    def start_mongodb(self):
        self.run_command_with_sudo(["systemctl", "start", "mongod"])
        self.check_status()

    def stop_mongodb(self):
        self.run_command_with_sudo(["systemctl", "stop", "mongod"])
        self.check_status()

    def toggle_mysql_startup(self):
        if self.mysql_disable_startup.get():
            self.run_command_with_sudo(["systemctl", "disable", "mysql"])
        else:
            self.run_command_with_sudo(["systemctl", "enable", "mysql"])
        self.check_startup_status()

    def toggle_apache_startup(self):
        if self.apache_disable_startup.get():
            self.run_command_with_sudo(["systemctl", "disable", "apache2"])
        else:
            self.run_command_with_sudo(["systemctl", "enable", "apache2"])
        self.check_startup_status()

    def toggle_mongodb_startup(self):
        if self.mongodb_disable_startup.get():
            self.run_command_with_sudo(["systemctl", "disable", "mongod"])
        else:
            self.run_command_with_sudo(["systemctl", "enable", "mongod"])
        self.check_startup_status()

if __name__ == "__main__":
    sudo_password = check_password()
    root = tk.Tk()
    app = ServerControlApp(root, sudo_password)
    root.mainloop()
