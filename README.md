# Azure Subscriptions & Resources Manager
[![generate C code && binary](https://github.com/dzhunli/azure_resources_manager/actions/workflows/build-gui.yml/badge.svg)](https://github.com/dzhunli/azure_resources_manager/actions/workflows/build-gui.yml)


License
-------
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

Why is this necessary?
----------------------

Managing Azure subscriptions and resources can be a complex and time-consuming task. The Azure Subscription Manager simplifies this process by providing a user-friendly interface to manage subscriptions, validate their status, delete resources, and handle subscriptions with or without resources. This tool is essential for administrators who need to maintain control over multiple Azure subscriptions efficiently.

Usage
-----

1.  **Login to Azure**: Click the "Login to Azure" button to authenticate your Azure account.
    
2.  **Get Subscriptions List**: Click "Get Subscriptions List" to retrieve a list of all Azure subscriptions. The subscriptions will be saved to subscriptions.json.
    
3.  **Validate Subscriptions**: Click "Validate Subscriptions" to check the validity of the subscriptions in subscriptions.json. It will create a backup file and update the JSON with validated subscriptions.
    
4.  **Delete Resources**:
    
    *   Enter the admin email in the "Admin Email" field.
        
    *   Select the JSON file containing subscriptions using "Select JSON File".
        
    *   Choose whether you want to use enable or disable subscriptions using the radio buttons.
        
    *   Click "Delete Resources" to delete resources for subscriptions based on the selected criteria.
        
5.  **Generate JSON for Non-Empty Subscriptions**: Click "Generate JSON for Non-Empty Subscriptions" to create a JSON file (non\_empty\_subscriptions.json) containing only subscriptions that have resources.
    
6.  **Cancel Empty Subscriptions**: Click "Cancel Empty Subscriptions" to cancel subscriptions that do not contain any resources.
    

### GUI Features

*   **Login to Azure**: Authenticate to Azure using az login.
    
*   **Get Subscriptions List**: Fetches and saves the list of subscriptions.
    
*   **Validate Subscriptions**: Validates the subscriptions and updates the JSON file.
    
*   **Delete Resources**: Deletes resources based on selected criteria.
    
*   **Generate JSON for Non-Empty Subscriptions**: Creates a JSON file for subscriptions that have resources.
    
*   **Cancel Empty Subscriptions**: Cancels subscriptions with no resources.
    

### Note

*   Ensure you have the Azure CLI installed and configured on your machine.
    
*   Make sure you have the necessary rights in your account.
