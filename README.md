# Obsidian Agent - Setup Guide

An AI agent that automatically generates notes for your Obsidian vault using Ollama and local LLMs.

## Prerequisites

### 1. Install Docker Desktop

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop/
- Install and restart your computer
- Open Docker Desktop and wait for it to say "Docker Desktop is running"
- You should see a whale icon 🐳 in your system tray

**Mac:**
- Download from: https://www.docker.com/products/docker-desktop/
- Install and open Docker Desktop
- Wait for it to start

**Linux:**
- Install Docker Engine: https://docs.docker.com/engine/install/
- Install Docker Compose: `sudo apt install docker-compose`

### 2. Install Git (Optional)

If you want to clone the repo:
- Windows: https://git-scm.com/download/win
- Mac: `brew install git`
- Linux: `sudo apt install git`

## Installation

### Option 1: Clone the Repository

```bash
git clone https://github.com/tmehta0405/obsidian-agent.git
cd obsidian-agent
```

### Option 2: Manual Setup

1. Create a new folder called `obsidian-agent`
2. Download these files into it:
   - `agent.py`
   - `requirements.txt`
   - `Dockerfile`
   - `docker-compose.yaml`
   - `.env`
3. Create a `texts/` folder with:
   - `questions.txt`
   - `question_template.txt`
   - `obsidian_template.txt`

## Configuration

### Edit the `.env` file

All configuration is done in the `.env` file. Update these values:

```dotenv
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
OBSIDIAN_DIR=C:/Users/YourName/Documents/YourVault
```

**Important:** 
- Don't use quotes around the paths
- Use forward slashes `/` even on Windows
- Make sure the path exists before running

**For Windows:**
```dotenv
OBSIDIAN_DIR=C:/Users/YourName/Documents/Obsidian Vault/YourVault
```

**For Mac:**
```dotenv
OBSIDIAN_DIR=/Users/YourName/Documents/YourVault
```

**For Linux:**
```dotenv
OBSIDIAN_DIR=/home/YourName/Documents/YourVault
```

### Available Models

Change `OLLAMA_MODEL` in `.env` to any model from: https://ollama.com/library

**Popular options:**
- `llama3.2:3b` - Fast and efficient (recommended, default)
- `llama3.2:1b` - Very fast, smaller
- `llama3.3:70b` - Most capable, but slower
- `mistral` - Good balance
- `codellama` - Better for technical content
- `gemma2` - Fast and capable
- `qwen2.5` - Great for reasoning

**After changing the model in `.env`, you need to pull it:**

```bash
# Change OLLAMA_MODEL in .env to your desired model
# Then pull it:
docker exec -it ollama ollama pull <model-name>

# Example for mistral:
docker exec -it ollama ollama pull mistral

# Then restart the agent:
docker-compose restart agent
```

**Pro tip:** You can have multiple models downloaded and just switch between them by changing `.env` - no need to re-download!

## First Time Setup (Need Good Internet!)

This will download ~4GB of data, so make sure you have a good internet connection.

### Step 0: Configure Your Environment

Edit `.env` and set your vault path:
```dotenv
OBSIDIAN_DIR=C:/Users/YourName/Documents/YourVault
```

Remember: No quotes, use forward slashes!

### Step 1: Start Ollama

```bash
docker-compose up -d ollama
```

Wait about 10 seconds for Ollama to start.

### Step 2: Download the AI Model

Download the model specified in your `.env` file (default is `llama3.2:3b`):

```bash
docker exec -it ollama ollama pull llama3.2:3b
```

**Want a different model?** Change `OLLAMA_MODEL` in `.env` first, then pull that model instead:
```bash
# For example, to use mistral:
docker exec -it ollama ollama pull mistral
```

This downloads the language model (~2GB for llama3.2:3b). Wait for it to complete.

**See all available models:** https://ollama.com/library

### Step 3: Run the Agent

```bash
docker-compose up --build agent
```

You should see the agent start generating notes!

## Daily Use

After the first setup, you only need:

```bash
docker-compose up agent
```

That's it! No downloads, no building (unless you change the code).

### Run in Background

```bash
docker-compose up -d agent
```

### Stop Everything

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f agent
```

## Troubleshooting

### Docker Desktop not running

**Error:** `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**Fix:** Open Docker Desktop and wait for it to start.

---

### Can't connect to Ollama

**Error:** Connection refused or timeout errors

**Fix:**
```bash
# Check if Ollama is running
docker ps

# Should see a container named "ollama"
# If not, start it:
docker-compose up -d ollama
```

---

### Model not found

**Error:** `model 'llama3.2:3b' not found`

**Fix:**
```bash
# Pull the model
docker exec -it ollama ollama pull llama3.2:3b

# Verify it's there
docker exec -it ollama ollama list
```

---

### pywin32 error when building

**Error:** `No matching distribution found for pywin32==311`

**Fix:** Your `requirements.txt` should only have:
```
ollama
python-dotenv
duckduckgo-search
```

Remove any Windows-specific packages.

---

### Path not found / Volume mount issues

**Error:** Can't find vault directory or files not appearing

**Fix:** 
1. Check your `.env` file - make sure `OBSIDIAN_DIR` has no quotes
2. Use forward slashes `/` even on Windows
3. Make sure the path actually exists
4. Restart Docker:
   ```bash
   docker-compose down
   docker-compose up --build agent
   ```

**Example working `.env`:**
```dotenv
OBSIDIAN_DIR=C:/Users/tirth/Documents/MyVault
```

**NOT this:**
```dotenv
OBSIDIAN_DIR="C:\Users\tirth\Documents\MyVault"  # WRONG!
```

---

### Agent stuck on "Attaching to obsidian-agent"

This is normal! It means it's running. The agent is processing in the background. Press `Ctrl+C` to stop it, or run in detached mode with `-d` flag.

---

### Permission denied (Linux)

**Error:** Can't write to vault directory

**Fix:**
```bash
sudo chown -R $USER:$USER /path/to/your/vault
```

---

### Port already in use

**Error:** `Bind for 0.0.0.0:11434 failed: port is already allocated`

**Fix:** You already have Ollama running somewhere. Either:
1. Stop the other Ollama: `docker stop $(docker ps -q --filter ancestor=ollama/ollama)`
2. Or change the port in `docker-compose.yaml`

## File Structure

```
obsidian-agent/
├── agent.py                 # Main agent script
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yaml     # Multi-container setup
├── .env                    # Environment variables (REQUIRED - configure this!)
├── texts/                  # Question templates
│   ├── questions.txt
│   ├── question_template.txt
│   └── obsidian_template.txt
└── test_vault/            # Your vault gets mounted here (auto-created)
```

**Before running, make sure to configure your `.env` file!**

## Useful Commands

```bash
# Start everything
docker-compose up

# Start in background
docker-compose up -d

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up --build agent

# Restart agent (after changing .env)
docker-compose restart agent

# View logs
docker-compose logs -f agent

# Check what's running
docker ps

# Enter Ollama container
docker exec -it ollama bash

# List available models
docker exec -it ollama ollama list

# Pull a new model
docker exec -it ollama ollama pull <model-name>

# Remove a model (to save space)
docker exec -it ollama ollama rm <model-name>

# Test a model manually
docker exec -it ollama ollama run llama3.2:3b "Hello, how are you?"

# Remove everything (fresh start)
docker-compose down -v
```

## Updating

### Update the Agent Code

```bash
git pull  # If using git
docker-compose up --build agent
```

### Switch to a Different Model

1. Edit `.env` and change `OLLAMA_MODEL`:
   ```dotenv
   OLLAMA_MODEL=mistral
   ```

2. Pull the new model:
   ```bash
   docker exec -it ollama ollama pull mistral
   ```

3. Restart:
   ```bash
   docker-compose restart agent
   ```

### Update Ollama

```bash
docker-compose down
docker-compose pull ollama
docker-compose up -d ollama
```

### Update a Model (get latest version)

```bash
docker exec -it ollama ollama pull llama3.2:3b
```

## Advanced Configuration

### Run on a Schedule

**Windows Task Scheduler:**
1. Create a new task
2. Trigger: Daily at specific time
3. Action: Start a program
4. Program: `docker-compose`
5. Arguments: `-f "C:\path\to\obsidian-agent\docker-compose.yaml" up agent`

**Mac/Linux Cron:**
```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /path/to/obsidian-agent && docker-compose up agent
```

### Use Multiple Models

Edit `docker-compose.yaml` to run different agents with different models:

```yaml
services:
  ollama:
    # ... same as before

  agent-creative:
    build: .
    environment:
      - OLLAMA_MODEL=llama3.2:3b
    volumes:
      - ./vault1:/app/test_vault

  agent-technical:
    build: .
    environment:
      - OLLAMA_MODEL=codellama
    volumes:
      - ./vault2:/app/test_vault
```

## Getting Help

1. Check the logs: `docker-compose logs agent`
2. Verify Ollama is running: `docker ps`
3. Test Ollama manually: `docker exec -it ollama ollama run llama3.2:3b "Hello"`
4. Open an issue on GitHub

## License

MIT