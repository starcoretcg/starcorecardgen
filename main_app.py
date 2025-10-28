"""
StarCore TCG - Main Streamlit App
Entry point for multi-page card generation system
"""

import streamlit as st

st.set_page_config(
    page_title="StarCore TCG - Card Generator",
    page_icon="🎴",
    layout="wide"
)

st.title("🎴 StarCore TCG Card Generation System")

st.markdown("""
Welcome to the StarCore TCG card generation and publishing system!

## 📚 Available Tools

### Card Generators
- **⚡ Resource Generator** - Create resource cores with automatic state management
- **👑 Commander Generator** *(coming soon)*
- **🎖️ Unit Generator** *(coming soon)*
- **✨ Spell Generator** *(coming soon)*

### Publishing Tools
- **📋 Publisher Dashboard** - Manage publishing workflow for all cards

## 🔄 Publishing Workflow

All generated cards follow this workflow:

```
📝 DRAFT ──────> ✅ PUBLISHED ──────> 🗄️ ARCHIVED
```

1. **Draft**: New cards start here - test and iterate
2. **Published**: Balanced and ready for gameplay
3. **Archived**: Retired or replaced cards

## 🚀 Quick Start

1. Navigate to a **Generator** page from the sidebar
2. Generate your cards - they automatically start in **Draft** state
3. Use the quick promote button or visit the **Publisher Dashboard**
4. Manage all cards across all types in one place!

## 💡 Tips

- Cards get unique 12-character hash IDs
- Use bulk actions for releasing full sets
- Filter and search in the Publisher Dashboard
- Export to CSV for analysis
- Add notes during playtesting

---

**Select a page from the sidebar to get started! →**
""")

# Stats overview
st.markdown("---")
st.subheader("📊 System Stats")

try:
    from card_state_manager import CardStateManager
    manager = CardStateManager(data_dir="data")
    stats = manager.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Cards", stats["total"])
    with col2:
        st.metric("📝 Drafts", stats["draft"])
    with col3:
        st.metric("✅ Published", stats["published"])
    with col4:
        st.metric("🗄️ Archived", stats["archived"])
    
    if stats["by_type"]:
        st.markdown("### Cards by Type")
        type_cols = st.columns(len(stats["by_type"]))
        for idx, (card_type, count) in enumerate(sorted(stats["by_type"].items())):
            with type_cols[idx]:
                type_emoji = {
                    "resource_core": "⚡",
                    "commander": "👑",
                    "unit": "🎖️",
                    "spell": "✨"
                }
                st.metric(
                    f"{type_emoji.get(card_type, '📦')} {card_type.replace('_', ' ').title()}",
                    count
                )
except:
    st.info("No cards generated yet. Start by generating some cards!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>StarCore TCG Card Generation System v1.0</p>
    <p>Built with Streamlit | Powered by Python</p>
</div>
""", unsafe_allow_html=True)
