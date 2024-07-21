import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
import subprocess
import json
import os

class AzureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Subscription Manager")
        self.root.geometry("600x800")

        self.json_file = ""

        self.frame = ttk.Frame(root)
        self.frame.pack(pady=20, padx=20, fill='x')

        self.login_button = ttk.Button(self.frame, text="Login to Azure", command=self.login_to_azure)
        self.login_button.pack(pady=10, padx=20, fill='x')

        self.get_list_button = ttk.Button(self.frame, text="Get Subscriptions List", command=self.get_subscriptions_list)
        self.get_list_button.pack(pady=10, padx=20, fill='x')

        self.validate_button = ttk.Button(self.frame, text="Validate Subscriptions", command=self.validate_subscriptions)
        self.validate_button.pack(pady=10, padx=20, fill='x')

        self.delete_button = ttk.Button(self.frame, text="Delete Resources", command=self.delete_resources)
        self.delete_button.pack(pady=10, padx=20, fill='x')

        self.generate_button = ttk.Button(self.frame, text="Generate JSON for Non-Empty Subscriptions", command=self.generate_non_empty_subscriptions_json)
        self.generate_button.pack(pady=10, padx=20, fill='x')

        self.cancel_empty_button = ttk.Button(self.frame, text="Cancel Empty Subscriptions", command=self.cancel_empty_subscriptions)
        self.cancel_empty_button.pack(pady=10, padx=20, fill='x')

        self.email_label = ttk.Label(self.frame, text="Admin Email:")
        self.email_label.pack(pady=5, padx=20, fill='x')
        
        self.email_entry = ttk.Entry(self.frame)
        self.email_entry.pack(pady=5, padx=20, fill='x')

        self.file_button = ttk.Button(self.frame, text="Select JSON File", command=self.select_json_file)
        self.file_button.pack(pady=10, padx=20, fill='x')

        self.file_label = ttk.Label(self.frame, text="No JSON file selected")
        self.file_label.pack(pady=5, padx=20, fill='x')

        self.enabled_var = tk.StringVar(value="true")

        self.enabled_true_radio = ttk.Radiobutton(self.frame, text="Enabled=True", variable=self.enabled_var, value="true")
        self.enabled_true_radio.pack(pady=5, padx=20, fill='x')

        self.enabled_false_radio = ttk.Radiobutton(self.frame, text="Enabled=False", variable=self.enabled_var, value="false")
        self.enabled_false_radio.pack(pady=5, padx=20, fill='x')

        self.progress_label = ttk.Label(root, text="")
        self.progress_label.pack(pady=5)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", troughcolor='white', background='green')

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(pady=20)

        self.log_text = scrolledtext.ScrolledText(root, width=70, height=20, state='normal')
        self.log_text.pack(pady=20)
        self.log_text.config(state='disabled')

    def run_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return e.output

    def login_to_azure(self):
        result = self.run_command("az login")
        if "Please open the following website" in result:
            messagebox.showinfo("Info", "Please complete the login in your browser.")
        elif result:
            messagebox.showinfo("Success", "Logged in to Azure successfully.")

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)  # Auto-scroll to the end

    def get_subscriptions_list(self):
        subscriptions = self.run_command("az account list --all --query '[].id' -o tsv")
        if subscriptions:
            subscriptions = subscriptions.split()
            total_subscriptions = len(subscriptions)
            subscriptions_json = []

            for counter, subscription_id in enumerate(subscriptions, start=1):
                self.progress_label.config(text=f"Processing subscription {counter} of {total_subscriptions}: {subscription_id}")
                self.progress_bar["value"] = (counter / total_subscriptions) * 100
                self.root.update_idletasks()

                owner = self.run_command(f"az resource list --subscription {subscription_id} --query '[0].systemData.createdBy' -o tsv").strip()
                enabled = "false" if owner == "null" else "true"

                subscription_json = {
                    "id": subscription_id,
                    "enabled": enabled,
                    "owner": owner
                }
                subscriptions_json.append(subscription_json)

            with open("subscriptions.json", "w") as f:
                json.dump(subscriptions_json, f, indent=2)
            messagebox.showinfo("Success", "JSON data has been saved to subscriptions.json")
            self.progress_label.config(text="")
            self.progress_bar["value"] = 0

    def validate_subscriptions(self):
        json_file = "subscriptions.json"
        if not os.path.isfile(json_file):
            messagebox.showerror("Error", f"JSON file not found: {json_file}")
            return

        backup_file = "subscriptions_backup.json"
        os.rename(json_file, backup_file)
        messagebox.showinfo("Backup", f"Backup of JSON file created: {backup_file}")

        check_all = messagebox.askyesno("Check All", "Validate all subscriptions?")

        with open(backup_file, "r") as f:
            subscriptions = json.load(f)

        total_subscriptions = len(subscriptions)
        updated_subscriptions = []

        for counter, subscription in enumerate(subscriptions, start=1):
            self.progress_label.config(text=f"Validating subscription {counter} of {total_subscriptions}")
            self.progress_bar["value"] = (counter / total_subscriptions) * 100
            self.root.update_idletasks()

            if check_all or subscription['enabled'] == "true":
                output = self.run_command(f"az account show --subscription {subscription['id']}")
                if "SubscriptionNotFound" in output:
                    messagebox.showwarning("Subscription Not Found", f"Subscription not found: {subscription['id']}")
                else:
                    updated_subscriptions.append(subscription)
            else:
                updated_subscriptions.append(subscription)

        if not updated_subscriptions:
            os.rename(backup_file, json_file)
            messagebox.showinfo("Result", "No subscriptions remaining in JSON after validation.")
        else:
            with open(json_file, "w") as f:
                json.dump(updated_subscriptions, f, indent=2)
            messagebox.showinfo("Success", f"Validation completed. Updated JSON saved to {json_file}. Total subscriptions: {len(updated_subscriptions)}")
        self.progress_label.config(text="")
        self.progress_bar["value"] = 0

    def select_json_file(self):
        self.json_file = filedialog.askopenfilename(title="Select JSON File", filetypes=(("JSON Files", "*.json"), ("All Files", "*.*")))
        if self.json_file:
            self.file_label.config(text=f"Selected JSON file: {self.json_file}")
            messagebox.showinfo("Selected File", f"Selected JSON file: {self.json_file}")
        else:
            self.file_label.config(text="No JSON file selected")

    def delete_resources(self):
        json_file = self.json_file
        admin_id = self.email_entry.get()

        if not os.path.isfile(json_file):
            messagebox.showerror("Error", f"JSON file not found: {json_file}")
            return

        if not admin_id:
            messagebox.showerror("Error", "Admin email is required.")
            return

        if os.path.isfile("deletion.log"):
            with open("deletion.log", "w") as f:
                f.write("")

        with open(json_file, "r") as f:
            subscriptions = json.load(f)

        total_subscriptions = len(subscriptions)
        filtered_subscriptions = [sub for sub in subscriptions if sub['enabled'] == self.enabled_var.get()]

        for counter, subscription in enumerate(filtered_subscriptions, start=1):
            self.progress_label.config(text=f"Processing subscription {counter} of {total_subscriptions}")
            self.progress_bar["value"] = (counter / total_subscriptions) * 100
            self.root.update_idletasks()

            subscription_id = subscription['id']

            self.log_message("-----------------------------------------")
            self.log_message(f"Processing subscription: {subscription_id}")

            resources = self.run_command(f"az resource list --subscription {subscription_id} --query '[].id' -o tsv")
            if not resources.strip():
                self.log_message(f"No resources found for subscription: {subscription_id}. Skipping.")
                continue

            self.run_command(f"az role assignment create --role 'Owner' --assignee {admin_id} --subscription {subscription_id} --scope /subscriptions/{subscription_id}")
            self.run_command(f"sleep 5")
            token = self.run_command("az account get-access-token --query accessToken -o tsv").strip()

            for resource_id in resources.splitlines():
                self.log_message(f"Deleting resource: {resource_id}")
                self.run_command(f"az resource delete --ids {resource_id}")

            self.run_command(f"az role assignment delete --role 'Owner' --assignee {admin_id} --scope /subscriptions/{subscription_id}")

            self.log_message("-----------------------------------------")

        messagebox.showinfo("Success", "Processing completed.")
        self.progress_label.config(text="")
        self.progress_bar["value"] = 0

    def generate_non_empty_subscriptions_json(self):
        subscriptions = self.run_command("az account list --all --query '[].id' -o tsv")
        if subscriptions:
            subscriptions = subscriptions.split()
            total_subscriptions = len(subscriptions)
            non_empty_subscriptions = []

            for counter, subscription_id in enumerate(subscriptions, start=1):
                self.progress_label.config(text=f"Checking subscription {counter} of {total_subscriptions}: {subscription_id}")
                self.progress_bar["value"] = (counter / total_subscriptions) * 100
                self.root.update_idletasks()

                resources = self.run_command(f"az resource list --subscription {subscription_id} --query '[].id' -o tsv")
                if resources.strip():
                    status = self.run_command(f"az account show --subscription {subscription_id} --query 'state' -o tsv").strip()
                    enabled = "true" if status == "Enabled" else "false"
                    non_empty_subscriptions.append({
                        "id": subscription_id,
                        "enabled": enabled
                    })

            with open("no_empty_subscriptions.json", "w") as f:
                json.dump(non_empty_subscriptions, f, indent=2)
            messagebox.showinfo("Success", "JSON data has been saved to no_empty_subscriptions.json")
            self.progress_label.config(text="")
            self.progress_bar["value"] = 0

    def cancel_empty_subscriptions(self):
        subscriptions = self.run_command("az account list --all --query '[].id' -o tsv")
        if subscriptions:
            subscriptions = subscriptions.split()
            total_subscriptions = len(subscriptions)
            admin_id = self.email_entry.get()

            if not admin_id:
                messagebox.showerror("Error", "Admin email is required.")
                return

            for counter, subscription_id in enumerate(subscriptions, start=1):
                self.progress_label.config(text=f"Checking subscription {counter} of {total_subscriptions}: {subscription_id}")
                self.progress_bar["value"] = (counter / total_subscriptions) * 100
                self.root.update_idletasks()

                resources = self.run_command(f"az resource list --subscription {subscription_id} --query '[].id' -o tsv")
                if not resources.strip():
                    self.log_message(f"Cancelling empty subscription: {subscription_id}")
                    self.run_command(f"az role assignment create --role 'Owner' --assignee {admin_id} --subscription {subscription_id} --scope /subscriptions/{subscription_id}")
                    self.run_command(f"sleep 5")
                    token = self.run_command("az account get-access-token --query accessToken -o tsv").strip()
                    self.run_command(f"curl -X POST https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Subscription/cancel?api-version=2021-10-01 -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{}}' -H 'Content-Length: 2'")
                    self.run_command(f"az role assignment delete --role 'Owner' --assignee {admin_id} --scope /subscriptions/{subscription_id}")

            messagebox.showinfo("Success", "Empty subscriptions cancelled.")
            self.progress_label.config(text="")
            self.progress_bar["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = AzureApp(root)
    root.mainloop()
