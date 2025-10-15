# Setup Instructions

## 📁 File Locations

### Environment File

**Location:** You need to create `.env` in this directory  
**Template:** `env_example.txt` (provided)  
**Status:** `.env` is in `.gitignore` (won't be committed to git)

### Git Ignore File

**Location:** `/Users/satyananda/Desktop/code/EAG_V2/Assignment_6/pydantic/.gitignore`  
**Status:** ✅ Created  
**Also:** Root `.gitignore` exists at `/Users/satyananda/Desktop/code/EAG_V2/.gitignore`

---

## 🔧 Setup Steps

### Step 1: Create Environment File

```bash
# Copy the template
cp env_example.txt .env

# Edit with your API key
nano .env
```

Or manually create `.env` with:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 2: Get Your API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste into `.env` file

### Step 3: Install Dependencies

```bash
pip install pydantic python-dotenv google-generativeai mcp
```

### Step 4: Verify Setup

```bash
python verify_setup.py
```

You should see:
```
✅ .env file exists
✅ GEMINI_API_KEY appears to be set
✅ All checks passed!
```

---

## 📂 Current File Structure

```
pydantic/
├── .gitignore              # ← Git ignore rules
├── env_example.txt         # ← Environment template
├── .env                    # ← YOU CREATE THIS (not in git)
├── models.py
├── perception.py
├── memory.py
├── decision_making.py
├── action.py
├── main.py
├── mcp_browser_server.py
├── verify_setup.py
└── ... (documentation files)
```

---

## 🔒 Security Notes

### What's in `.gitignore`

The `.gitignore` file ensures these are **NOT** committed to git:
- `.env` - Your API key (sensitive!)
- `__pycache__/` - Python bytecode
- `*.pyc` - Compiled Python files
- `.vscode/`, `.idea/` - IDE settings
- `agent_canvas_*.html` - Generated HTML files
- `*.log` - Log files

### What's Safe to Commit

Everything else is safe to commit:
- `env_example.txt` - Template (no real key)
- All `.py` files - Source code
- All `.md` files - Documentation
- `pyproject.toml` - Dependencies

---

## 🐛 Troubleshooting

### Issue: `.env` file not found

**Solution:**
```bash
cp env_example.txt .env
nano .env  # Add your API key
```

### Issue: GEMINI_API_KEY not working

**Check:**
1. Is `.env` in the correct directory?
   ```bash
   ls -la .env
   ```

2. Does it contain your actual key?
   ```bash
   cat .env | grep GEMINI_API_KEY
   ```

3. No quotes needed:
   ```bash
   # ✅ Correct
   GEMINI_API_KEY=AIzaSyAbc123...
   
   # ❌ Wrong
   GEMINI_API_KEY="AIzaSyAbc123..."
   ```

### Issue: python-dotenv not loading

**Solution:**
```bash
pip install python-dotenv
# Or
pip install -e .
```

---

## 📝 Quick Reference

```bash
# Create .env from template
cp env_example.txt .env

# Edit .env
nano .env

# Verify setup
python verify_setup.py

# Run the agent
python main.py

# Check if .env exists
ls -la .env

# View .gitignore rules
cat .gitignore

# Check what's being ignored by git
git status --ignored
```

---

## ✅ Verification Checklist

- [ ] `.env` file created in `pydantic/` directory
- [ ] `GEMINI_API_KEY` added to `.env`
- [ ] No quotes around the API key
- [ ] Dependencies installed (`pip install ...`)
- [ ] `verify_setup.py` runs successfully
- [ ] `.env` is listed in `.gitignore`
- [ ] Git doesn't show `.env` in `git status`

---

## 🎯 Ready to Run?

Once all checkboxes are complete:

```bash
python main.py
```

Enjoy your cognitive agent! 🚀

