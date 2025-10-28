# 🎴 StarCore TCG Publishing System

## 📋 Complete System Overview

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STARCORE TCG SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────┐
│  CARD GENERATORS     │  │  PUBLISHING SYSTEM   │  │  DATA LAYER  │
├──────────────────────┤  ├──────────────────────┤  ├──────────────┤
│                      │  │                      │  │              │
│  ⚡ Resource Core    │──┤  card_state_manager  │──┤  JSON Store  │
│  👑 Commander        │  │                      │  │              │
│  🎖️ Unit             │  │  - create_state()    │  │  card_states │
│  ✨ Spell            │  │  - transition()      │  │  .json       │
│                      │  │  - query()           │  │              │
│  Each generates:     │  │  - bulk_ops()        │  │              │
│  • Unique hash ID    │  │                      │  │              │
│  • Card data         │  └──────────────────────┘  └──────────────┘
│  • Auto-draft state  │            │
│                      │            │
└──────────────────────┘            ▼
                         ┌──────────────────────┐
                         │  STREAMLIT UI        │
                         ├──────────────────────┤
                         │                      │
                         │  📋 Publisher        │
                         │     Dashboard        │
                         │                      │
                         │  • Filter cards      │
                         │  • Manage states     │
                         │  • Bulk actions      │
                         │  • Export data       │
                         │                      │
                         └──────────────────────┘
```

---

## 🔄 Publishing Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      STATE TRANSITIONS                           │
└─────────────────────────────────────────────────────────────────┘

    📝 DRAFT                    ✅ PUBLISHED                🗄️ ARCHIVED
    ├─────────┐                 ├─────────┐                ├─────────┐
    │ New     │────Promote─────>│ Active  │────Archive────>│ Retired │
    │ Testing │                 │ Balanced│                │ Final   │
    │ WIP     │──┐              │ Live    │                │ State   │
    └─────────┘  │              └─────────┘                └─────────┘
                 │                                               ▲
                 └──────────────Skip Publishing─────────────────┘

Actions Available by State:
┌──────────────────────────────────────────────────────────────────┐
│ DRAFT      → Can promote to Published OR skip to Archived        │
│ PUBLISHED  → Can only move to Archived                          │
│ ARCHIVED   → Terminal state (no further transitions)            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
starcore-tcg/
├── streamlit_apps/
│   ├── main_app.py                      # 🏠 Entry point
│   ├── card_state_manager.py            # 🔧 Core logic
│   │
│   ├── pages/
│   │   ├── 1_resource_generator.py      # ⚡ Resource UI
│   │   ├── 2_publisher_dashboard.py     # 📋 Publisher UI
│   │   ├── 3_commander_generator.py     # 👑 Future
│   │   └── 4_unit_generator.py          # 🎖️ Future
│   │
│   └── data/
│       ├── card_states.json             # 💾 State storage
│       └── backups/                     # 🔄 Auto backups
│
└── docs/
    ├── PUBLISHING_SETUP_GUIDE.md        # 📖 Setup docs
    └── test_publishing_system.py        # 🧪 Tests
```

---

## 🎯 Key Features

### 1. Universal Card State Management
- ✅ Works for ALL card types (resources, commanders, units, spells)
- ✅ Hash ID as primary key (12 chars)
- ✅ Timestamps for all transitions
- ✅ Version tracking

### 2. Publisher Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│  📋 PUBLISHER DASHBOARD                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 Stats Overview                                               │
│  ┌──────┬──────┬──────┬──────┐                                 │
│  │ Total│ Draft│ Pub  │ Arch │                                  │
│  └──────┴──────┴──────┴──────┘                                 │
│                                                                  │
│  🔍 Filters                                                      │
│  [State ▼] [Type ▼] [Search___]                                │
│                                                                  │
│  📚 Card Table (sortable, filterable)                           │
│  ╔════╦══════╦════════╦═══════════╦══════════╗                 │
│  ║ St │ Type │ Card ID│ Created   │ Actions  ║                 │
│  ╠════╬══════╬════════╬═══════════╬══════════╣                 │
│  ║ 📝 │ ⚡   │ abc... │ 2025-10-28│ [→ Pub]  ║                 │
│  ║ ✅ │ 👑   │ def... │ 2025-10-27│ [→ Arc]  ║                 │
│  ║ 📝 │ ⚡   │ ghi... │ 2025-10-28│ [→ Pub]  ║                 │
│  ╚════╩══════╩════════╩═══════════╩══════════╝                 │
│                                                                  │
│  ⚡ Bulk Actions                                                 │
│  [📤 Publish All Drafts] [🗄️ Archive Published] [💾 Export]    │
│                                                                  │
│  🎴 Individual Management                                        │
│  [Select Card ▼] [Details Panel] [State Buttons]               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Auto-Draft Creation
```python
# Generator creates card
card_hash = generate_hash(card_data)

# Automatically creates draft state
manager.create_card_state(
    card_id=card_hash,
    card_type="resource_core",
    notes="Auto-generated"
)
```

### 4. State Validation
```python
# Built-in validation
VALID_TRANSITIONS = {
    "draft": ["published", "archived"],
    "published": ["archived"],
    "archived": []  # Terminal
}

# Can't make invalid transitions
manager.can_transition(card_id, new_state)  # Returns bool
```

---

## 💾 Data Model

```json
{
  "1bbb4b4394f1": {
    "card_id": "1bbb4b4394f1",
    "card_type": "resource_core",
    "state": "published",
    "created_at": "2025-10-28T12:00:00.000000",
    "published_at": "2025-10-28T12:05:00.000000",
    "archived_at": null,
    "version": 1,
    "notes": "Medium Energy Core - Playtested and balanced"
  },
  "8a9f2c3d5e6f": {
    "card_id": "8a9f2c3d5e6f",
    "card_type": "commander",
    "state": "draft",
    "created_at": "2025-10-28T13:00:00.000000",
    "published_at": null,
    "archived_at": null,
    "version": 1,
    "notes": "Testing commander abilities"
  }
}
```

---

## 🚀 Quick Commands

### Setup
```bash
cd /workspaces/starcore-tcg/streamlit_apps
mkdir -p data
python test_publishing_system.py  # Run tests
```

### Run Streamlit
```bash
streamlit run main_app.py --server.port 8501
```

### Test State Manager
```bash
python card_state_manager.py
```

---

## 🎮 Usage Flow

```
USER ACTIONS                    SYSTEM ACTIONS
─────────────                   ──────────────

1. Click "Generate"         →   Generate card data
                                 ↓
2. Card displayed           ←   Create hash ID
   with Draft badge             ↓
                                 Auto-create draft state
                                 ↓
3. Click "Promote"          →   Transition to published
                                 ↓
4. View in Publisher        ←   Add publish timestamp
   Dashboard                     ↓
                                 Update state file
5. Bulk archive set         →   ↓
                                 Transition multiple cards
6. Export CSV               →   ↓
                                 Generate report
```

---

## ✨ Benefits

### For Development
- ✅ Separation of concerns (generation vs. publishing)
- ✅ Reusable across all card types
- ✅ Easy to extend (add new states, rules)
- ✅ JSON storage (no database needed)

### For Design
- ✅ Track card iterations
- ✅ Manage playtest versions
- ✅ Bulk release sets
- ✅ Retire old cards cleanly

### For Users
- ✅ Clear workflow
- ✅ Unified dashboard
- ✅ Search and filter
- ✅ Export capabilities

---

## 🔮 Future Enhancements

1. **Version Control**
   - Track card iterations
   - Rollback to previous versions
   - Compare versions side-by-side

2. **Approval Workflow**
   - Add "review" state
   - Require approval before publishing
   - Assign reviewers

3. **Batch Operations**
   - Tag cards by set/expansion
   - Bulk edit properties
   - Set-level publishing

4. **Analytics**
   - Publishing velocity
   - State duration tracking
   - Type distribution over time

5. **Integrations**
   - Export to TTS (Tabletop Simulator)
   - API for external tools
   - Webhook notifications

---

## 📊 System Stats Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  STARCORE TCG PUBLISHING METRICS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📦 Total Cards: 150                                             │
│  📝 In Draft: 23                                                 │
│  ✅ Published: 112                                               │
│  🗄️ Archived: 15                                                 │
│                                                                  │
│  By Type:                                                        │
│  ⚡ Resource Cores: 45                                           │
│  👑 Commanders: 8                                                │
│  🎖️ Units: 82                                                    │
│  ✨ Spells: 15                                                   │
│                                                                  │
│  Recent Activity:                                                │
│  • 5 cards published today                                      │
│  • 2 cards archived this week                                   │
│  • 12 cards in draft for review                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Built with ❤️ for StarCore TCG**
