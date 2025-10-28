# 📋 Publishing System Setup Guide

## 🎯 What You Just Got

A complete card publishing workflow system that works across ALL card types!

### Files Created:

1. **`card_state_manager.py`** - Core state management logic
2. **`publisher_dashboard.py`** - Streamlit dashboard for managing cards
3. **`resource_generator_ui.py`** - Updated generator with publishing integration

---

## 🚀 Quick Start

### Step 1: Copy Files to Your Codespace

```bash
# In your Codespace terminal
cd /workspaces/starcore-tcg/streamlit_apps

# The files are already in /mnt/user-data/outputs/
# Copy them to your streamlit directory
cp /mnt/user-data/outputs/card_state_manager.py .
cp /mnt/user-data/outputs/publisher_dashboard.py .
cp /mnt/user-data/outputs/resource_generator_ui.py .
```

### Step 2: Create Data Directory

```bash
# Create the data directory for state storage
mkdir -p data
```

### Step 3: Test the State Manager

```bash
# Test the core functionality
python card_state_manager.py
```

You should see:
```
🧪 Testing Card State Manager

Creating test cards...
✅ Created 3 cards

Testing state transitions...
Card 1 can publish? True
✅ Card 1 promoted to published

📊 Current Stats:
Total cards: 3
Drafts: 2
Published: 1
Archived: 0
```

### Step 4: Add to Your Streamlit Multi-Page App

If you have a multi-page Streamlit app structure:

```
streamlit_apps/
├── main_app.py
├── pages/
│   ├── 1_resource_generator.py  # Your existing page
│   ├── 2_publisher_dashboard.py  # NEW!
│   └── 3_commander_generator.py  # Future
├── card_state_manager.py  # NEW!
└── data/
    └── card_states.json  # Auto-created
```

Move files to pages:
```bash
mv publisher_dashboard.py pages/2_publisher_dashboard.py
```

### Step 5: Run Streamlit

```bash
cd /workspaces/starcore-tcg/streamlit_apps
streamlit run main_app.py --server.port 8501
```

---

## 🎮 How to Use

### Generating Cards with Publishing

1. **Generate a card** (Resource, Commander, etc.)
2. Card automatically gets `card_id` hash and `draft` state
3. See state badge on the card display
4. Quick promote button right in the generator

### Publisher Dashboard

Navigate to the Publisher Dashboard page:

1. **View all cards** across all types
2. **Filter by state** (draft/published/archived)
3. **Filter by type** (resource_core, commander, etc.)
4. **Search by ID**
5. **Bulk actions**: Publish all drafts, Archive all published
6. **Individual management**: Select a card and promote/archive

### State Workflow

```
📝 DRAFT
  ↓ (Promote)
✅ PUBLISHED
  ↓ (Archive)
🗄️ ARCHIVED (Terminal)
```

**Shortcuts:**
- Draft → Archived (skip publishing)
- Can't un-archive (terminal state)

---

## 🔧 Integration with Existing Generators

### For Your Current Resource Generator

If you already have `resource_core_generator.py`, update your UI to include:

```python
from card_state_manager import CardStateManager

# After generating a card
manager = CardStateManager(data_dir="data")
manager.create_card_state(
    card_id=card_hash,
    card_type="resource_core",
    notes=f"{size} {type} Core"
)
```

### For Future Card Types

When you create Commander/Unit/Spell generators:

```python
# Just change the card_type parameter
manager.create_card_state(
    card_id=card_hash,
    card_type="commander",  # or "unit", "spell", etc.
    notes="Auto-generated commander"
)
```

---

## 📊 Data Storage

All state data is stored in:
```
data/card_states.json
```

Example structure:
```json
{
  "1bbb4b4394f1": {
    "card_id": "1bbb4b4394f1",
    "card_type": "resource_core",
    "state": "published",
    "created_at": "2025-10-28T12:00:00",
    "published_at": "2025-10-28T12:05:00",
    "archived_at": null,
    "version": 1,
    "notes": "Medium Energy Core - Auto-generated"
  }
}
```

---

## 🎨 Customization Ideas

### Add More States
Edit `card_state_manager.py`:
```python
VALID_STATES = ["draft", "review", "published", "archived"]
```

### Add Approval Workflow
```python
# Require review before publishing
VALID_TRANSITIONS = {
    "draft": ["review"],
    "review": ["published", "draft"],
    "published": ["archived"]
}
```

### Add Version Control
Already built in! The `version` field tracks card iterations.

### Add Notes/Comments
Use the `notes` field for playtesting feedback, balance changes, etc.

---

## 🐛 Troubleshooting

### "Module not found: card_state_manager"
Make sure `card_state_manager.py` is in the same directory as your Streamlit pages.

### "Data directory not found"
Run: `mkdir -p data` in your streamlit_apps directory

### States not persisting
Check that `data/card_states.json` exists and is writable

### Can't transition state
Check the workflow rules - archived is terminal, can't go backward

---

## ✅ Next Steps

1. ✅ Copy files to Codespace
2. ✅ Test the state manager
3. ✅ Run Streamlit and generate a card
4. ✅ Open Publisher Dashboard
5. ✅ Promote your first card!

Then integrate with:
- Commander generator (coming soon)
- Unit generator (future)
- Spell generator (future)

---

## 💡 Pro Tips

- Use **Bulk Promote** when releasing a new set
- Use **Search** to find specific cards during playtesting
- **Filter by state** to see what needs review
- **Export CSV** for spreadsheet analysis
- Keep **notes** for playtesting feedback

The publishing system is now ready! Every card you generate will automatically get state tracking. 🎉
