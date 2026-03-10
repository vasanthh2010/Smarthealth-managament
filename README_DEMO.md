# Smart Hospital System Demo Guide

To see the full demo of the project, follow these steps:

1.  **Open a Terminal** in the project root directory (`c:\Users\HP\Desktop\antiproject`).
2.  **Run the start script**:
    ```bash
    .\start.bat
    ```
    This script will install dependencies, setup the database, and start the Flask backend.

3.  **Access the Demo**:
    Once the backend is running, open your browser and go to:
    [http://localhost:5000](http://localhost:5000)

## Demo Credentials
- **Super Admin**: `superadmin` / `Admin@123`
- **Hospital**: `HOSP001` / `Admin@123`
- **Patient**: Register at the signup page.

> [!IMPORTANT]
> **Data Persistence**: The system now preserves all data between restarts. Newly registered patients and approved hospitals are permanently stored in the `app.db` file.

> [!TIP]
> **Finding Credentials**: If you register a new hospital and approve it as Super Admin, the automatically generated **Login ID** and **Password** will be visible in the Super Admin dashboard under the **Hospitals** list.

> [!NOTE]
> Ensure Python 3.8+ is installed on your system.
