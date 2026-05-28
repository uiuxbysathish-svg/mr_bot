# MR Assistant Bot 🤖💼

**MR Assistant Bot** is a production-level, lightweight Pharma CRM + POB (Product Order Booking) Tracking System + DCR (Daily Call Report) Automation Tool built directly inside Telegram. It is designed specifically for Pharmaceutical Medical Representatives (MRs), Area Sales Managers (ASMs), and Regional Managers (RMs) to log details quickly in the field with minimal typing, generate copyable order summaries for WhatsApp, and run reports.

---

## 🛠 Features

1. **Telegram-Based Profile Registry (`/start`)**:
   * Uses Telegram User IDs for secure, password-less authentication.
   * Auto-detects registration status.
   * Prompts new users for Name, Employee Code, HQ, and Division.
2. **Territory Doctor Registry (`/adddoctor`)**:
   * Saves doctor profiles (Name, Speciality, Hospital/Clinic) linked to specific MRs.
   * Minimises typing by presenting Inline Keyboard buttons for common specialities.
3. **Product Order Booking (`/pob`)**:
   * MRs select doctors from dynamic inline buttons (no typing required).
   * Guides inputs for Product Name, Quantity, and Order Value.
4. **Auto-Generated copy-pasteable WhatsApp Receipts**:
   * Generates a beautifully formatted, copyable summary instantly after booking:
     ```text
     🏥 POB ORDER
     👨‍⚕️ Doctor: Dr. Kumar
     💊 Product: Zerapod CV
     📦 Quantity: 30 Strips
     💰 Order Value: ₹12,500
     📅 Date: 16 May 2026
     ```
5. **Real-time Analytics**:
   * `/todaypob`: Total booked orders today, breakdown by doctor, and product-wise sum.
   * `/monthpob`: Monthly cumulative sales, average order sizes, top contributing doctors, and top products.
   * `/topdoctors`: Ranks doctors by cumulative order booking value.
6. **Reminders & Job Scheduling (`/reminders`, `/setrevisit`)**:
   * Schedule reminders to revisit specific doctors (e.g., in 3, 7, 14, 30 days).
   * Toggle daily evening alarms (at 8:00 PM) prompting the MR to record their bookings.

---

## 📂 Project Structure

```text
mr_bot/
│
├── bot.py                  # Main bot script (orchestrates all components)
├── database.py             # SQLite connection wrapper & initial schema setup
├── config.py               # Env loader & configuration parameters
├── requirements.txt        # PIP packages list
├── README.md               # Setup and deployment manual
│
├── database/
│   └── mr_database.db      # Local SQLite database file (created automatically)
│
├── handlers/
│   ├── start_handler.py        # /start and MR registration flows
│   ├── doctor_handler.py       # /adddoctor profile creation flow
│   ├── pob_handler.py          # /pob order booking flow
│   ├── report_handler.py       # /todaypob, /monthpob, and /topdoctors handlers
│   └── reminder_handler.py     # /reminders and /setrevisit handler
│
├── services/
│   ├── user_service.py         # DB helpers for users
│   ├── doctor_service.py       # DB helpers for doctor profiles
│   ├── pob_service.py          # DB helpers for order logs
│   └── message_formatter.py    # Formats lists & orders into clean text
│
└── utils/
    ├── helpers.py              # Middleware checking for MR authentication
    └── validators.py           # Validates numeric amounts & inputs
```

---

## 🚀 Setup & Installation (Local Machine)

### STEP 1: Install Python
* Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/).
* **Windows Users**: Make sure to check **"Add Python to PATH"** during installation.

### STEP 2: Create a Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send the command `/newbot`.
3. Follow the instructions to give your bot a Name (e.g., `MR Assistant Bot`) and a unique Username (e.g., `mr_assistant_crm_bot`).
4. Copy the **HTTP API Token** provided by BotFather.

### STEP 3: Setup the Project Folder
1. Open your terminal or Command Prompt (CMD).
2. Clone or navigate to the project directory:
   ```bash
   cd c:/Users/sathi/OneDrive/Desktop/ANTIGRAVITY/mr_bot
   ```

### STEP 4: Install Dependencies
Install all required libraries using python package manager `pip`:
```bash
pip install -r requirements.txt
```

### STEP 5: Configure the Environment (`.env`)
1. Open the `.env` file in the `mr_bot` directory.
2. Replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` with the token you copied from BotFather.
3. Save the file.

### STEP 6: Run the Bot
Execute the main script:
```bash
python bot.py
```
If successfully running, you will see:
```text
🚀 Initializing SQLite database...
Database initialized successfully.
🤖 Building Telegram Bot Application...
✨ MR Assistant Bot is now running! Press Ctrl+C to stop.
```

---

## 🏗️ SQLite Database Schemas

### users
* `telegram_id` (Primary Key, unique Telegram ID)
* `mr_name` (Name of Medical Representative)
* `employee_code` (Unique Employee code)
* `hq` (Headquarters, e.g. Coimbatore)
* `division` (Division, e.g. Ortho)
* `created_at` (Timestamp)

### doctors
* `id` (Auto-incrementing ID)
* `user_id` (Foreign Key linked to users.telegram_id)
* `doctor_name` (Name of the Doctor)
* `speciality` (Speciality of the Doctor)
* `hospital` (Clinic or Hospital Name)

### pob_entries
* `id` (Auto-incrementing ID)
* `user_id` (Foreign Key linked to users.telegram_id)
* `doctor_id` (Foreign Key linked to doctors.id)
* `product_name` (Name of booked product)
* `quantity` (Quantity, e.g. 30 Strips)
* `order_value` (Booked Order Value, float)
* `entry_date` (Date, e.g. YYYY-MM-DD)
* `timestamp` (Exact log timestamp)

---

## ☁️ Free Hosting & Deployment (24/7 Online)

Since the bot uses a local SQLite database, you need hosting that either **supports persistent disk volumes** (so your database isn't deleted on restart) or **runs webhooks** that wake the bot up. Here are the 3 best options to host this bot for **100% Free**:

---

### Option 1: Fly.io (Recommended - Free 24/7 with Persistent SQLite)
Fly.io offers a free tier containing up to 3 shared-cpu-1x VMs and **3GB of persistent volume storage**. This is the perfect option for SQLite bots because your database is stored on a persistent SSD volume and never deleted.

#### STEP 1: Install Flyctl
* **Windows (PowerShell)**:
  ```powershell
  pwsh -Command "iwr https://fly.io/install.ps1 | iex"
  ```
* **macOS/Linux**:
  ```bash
  curl -L https://fly.io/install.sh | sh
  ```

#### STEP 2: Authenticate
Create a free account or login:
```bash
fly auth signup
# or
fly auth login
```

#### STEP 3: Configure Project (`fly.toml`)
Run the launch wizard inside your project directory (`mr_bot`):
```bash
fly launch
```
* Choose a unique app name (e.g., `mr-assistant-crm-bot`).
* Select your closest region.
* **Do you want to tweak settings?** Yes.
* Under **Database**, select **None** (we will use our local SQLite on a volume).
* Under **Storage**, add a mount point:
  * Name: `mr_data`
  * Path: `/data`
  * Size: `1GB` (which is within the free tier).

This will generate a `fly.toml` file. Ensure the `[mounts]` and `[env]` section in `fly.toml` looks like this:
```toml
[env]
  DATABASE_PATH = "/data/mr_database.db"

[mounts]
  source = "mr_data"
  destination = "/data"
```

#### STEP 4: Set Secrets & Deploy
Set your Telegram Token as a secure secret:
```bash
fly secrets set TELEGRAM_BOT_TOKEN="your_actual_bot_token"
```
Deploy the application:
```bash
fly deploy
```
Your bot is now running 24/7 for free, and the SQLite database `/data/mr_database.db` will persist forever.

---

### Option 2: Render (Free Web Service - Webhook Mode)
Render's free tier allows you to deploy Web Services. By setting up webhooks, Telegram will send messages directly to Render. This wakes up your bot when a message is received.

> [!WARNING]
> Render's free tier has an ephemeral disk. The SQLite database will reset to empty whenever the bot is redeployed or restarted. Use this for testing/demos.

#### STEP 1: Push Code to GitHub
1. Create a new repository on GitHub.
2. Initialize Git and push your project:
   ```bash
   git init
   git add .
   git commit -m "Configure MR Bot"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPOSITORY_URL
   git push -u origin main
   ```

#### STEP 2: Configure Render Web Service
1. Register on [Render.com](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Link your GitHub repository.
4. Input configuration:
   * **Name**: `mr-assistant-bot`
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python bot.py`
   * **Plan**: `Free`
5. Click **Advanced** and add **Environment Variables**:
   * `TELEGRAM_BOT_TOKEN` = `your_actual_bot_token`
   * `WEBHOOK_URL` = `https://mr-assistant-bot.onrender.com` (replace with your actual Render URL)
   * `PORT` = `8000` (Render will automatically pass this, but you can define it to be safe)
6. Click **Deploy Web Service**.

When a user messages the bot, Render spins up the application, processes the message, and goes back to sleep after 15 minutes of inactivity.

---

### Option 3: Glitch (Free App - Persistent SQLite + Webhook)
Glitch has a persistent filesystem (meaning your SQLite database is safe) and runs web services that sleep after 5 minutes. Using webhooks, the bot wakes up instantly when users send messages.

1. Go to [Glitch.com](https://glitch.com/) and create a free account.
2. Click **New Project** -> **Import from GitHub** and paste your GitHub repository link.
3. In the `.env` configuration file on Glitch, add:
   * `TELEGRAM_BOT_TOKEN` = `your_actual_bot_token`
   * `WEBHOOK_URL` = `https://your-glitch-project-name.glitch.me`
4. Glitch will automatically run your project using `start` script defined in your package.json, or you can create a simple `glitch.json` configuration to run `python bot.py`.

