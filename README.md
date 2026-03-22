# WTicket (v1.0.1)
A Discord ticket bot with slash commands, supporting bug reports, feedback, and support requests. Configured entirely through Discord without touching any config files.

## ⚠️ If you only want to add the bot to your server, use this link and ignore the steps below: [![Discord Invite](https://img.shields.io/badge/Discord-Add_to_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1485006350265090239&permissions=8&integration_type=0&scope=bot)

---
# Installation

Follow the steps according to your OS.

## Configuration
After completing step one of the installation section, follow these steps:

The bot needs a **Discord Bot Token** to run. If you don't know how to get one, go to the [Discord Developer Portal](https://discord.com/developers/applications), create an application, and copy your token from the **Bot** tab.

### Step-by-Step Token Setup:

1. **Show Hidden Files:**
   - **Windows:** In the folder, click the "View" tab and check "Hidden Items".
   - **Linux / macOS:** Press `Ctrl + H` inside the folder to reveal the `.env.example` file.

2. **Prepare the File:**
   - Right-click on `.env.example` and select "Rename".
   - Remove the `.example` part. The file should now be named just `.env`.

3. **Paste Your Token:**
   - Open the `.env` file with Notepad or any text editor.
   - Replace `BOT_TOKEN=` with your token: `BOT_TOKEN=your_token_here`
   - Save and close the file.

> All other settings (ticket channel, staff role, ping role) are configured directly in Discord via the `/setup` command. No need to edit any files.

---

## Linux

Python is usually pre-installed on Linux. Open your terminal and follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kDaejungg/wticket.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```bash
   cd wticket
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```bash
   python3 bot.py
   ```

---

## Windows

You can use PowerShell or Command Prompt (CMD). Make sure Python is added to your system PATH.

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/kDaejungg/wticket.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```powershell
   cd wticket
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\activate
   ```

4. **Install requirements:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```powershell
   python bot.py
   ```

---

## macOS

Mac users can follow these steps using the Terminal app:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kDaejungg/wticket.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```bash
   cd wticket
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```bash
   python3 bot.py
   ```

---

## Adding the Bot to Your Server

After running the bot, follow these steps to invite it to your server:

### 1. Generate an OAuth2 Link
1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)** and select your application.
2. In the left menu, click **OAuth2** → **URL Generator**.
3. Under **Scopes**, check the following:
   - [x] `bot`
   - [x] `applications.commands` (required for slash commands)

### 2. Select Required Permissions
Under **Bot Permissions**, check exactly the following:

**General Permissions**
✅ Manage Channels

**Text Permissions**
✅ Send Messages

✅ Create Public Threads

✅ Create Private Threads

✅ Send Messages in Threads

✅ Send TTS Messages

✅ Manage Messages

✅ Manage Threads

✅ Embed Links

✅ Attach Files

✅ Read Message History

✅ Add Reactions

✅ Use Slash Commands

✅ Use External Apps

✅ Create Polls

✅ Bypass Slow Mode

### 3. Invite
4. Copy the **Generated URL** at the bottom of the page.
5. Paste it into your browser and invite the bot to your server.

> **⚠️ Note:** If slash commands don't appear after adding the bot, restart your Discord client or make sure the bot has the "Use Application Commands" permission.

### 4. First-Time Setup in Discord
Once the bot is in your server, run the following command as an Administrator:

```
/setup ticket_channel:#your-channel staff_role:@YourRole
```

---

## 📂 File Structure

- `bot.py`: Main bot engine and Discord commands.
- `config.py`: Token loader and settings manager.
- `settings.json`: Saved bot configuration (auto-generated after `/setup`).
- `about.json`: Bot identity info (version, developer).
- `requirements.txt`: Required Python libraries.
- `.env`: Your bot token (never share this).
- `.gitignore`: Prevents token and unnecessary files from being pushed to GitHub.

## ⚠️ Important Security Note
Never share your `.env` file or commit it to a public repository. The `.gitignore` file already excludes it, but always double-check before pushing.

---
*Made by Enes Ramazan Whitelineage*

#### Contact & feedback: [Discord](https://discord.gg/vV8gEpHDXH)
