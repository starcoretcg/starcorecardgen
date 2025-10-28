"""
StarCore Resource Core Generator - Streamlit UI with Publishing
Integrated with card state management system
"""

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from card_state_manager import CardStateManager

# You'll need to import your existing resource_core_generator
# from resource_core_generator import generate_resource_core, calculate_weight

st.set_page_config(page_title="Resource Generator", page_icon="⚡", layout="wide")

# Initialize state manager
@st.cache_resource
def get_state_manager():
    return CardStateManager(data_dir="data")

manager = get_state_manager()

# Header
st.title("⚡ Resource Core Generator")
st.markdown("Generate resource cores with integrated publishing workflow")

# Two column layout
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("🎲 Generator")
    
    # Size selector
    core_size = st.selectbox(
        "Core Size",
        ["Small", "Medium", "Large", "Massive"]
    )
    
    # Resource type selector
    resource_type = st.selectbox(
        "Resource Type",
        ["Energy", "Matter", "Signal", "Life", "Omni"]
    )
    
    # Generate button
    if st.button("🎲 Generate Resource Core", use_container_width=True, type="primary"):
        # TODO: Replace with your actual generation function
        # core = generate_resource_core(core_size, resource_type)
        
        # For now, creating mock data structure
        core_data = {
            "size": core_size,
            "resource_type": resource_type,
            "tier": 5,  # Mock
            "quality": 68,  # Mock
            "cost": 3,  # Mock
            "rpt": 2,  # Mock
            "hp": 5,  # Mock
            "links": 2,  # Mock
            "rarity": "Uncommon"  # Mock
        }
        
        # Generate hash ID
        hash_input = f"{core_data['size']}{core_data['tier']}{core_data['quality']}{core_data['cost']}{core_data['rpt']}{core_data['hp']}{core_data['links']}{core_data['resource_type']}{datetime.now().isoformat()}"
        card_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        
        # Store in session
        if 'generated_cards' not in st.session_state:
            st.session_state.generated_cards = []
        
        card_with_id = {**core_data, "card_id": card_hash, "created_at": datetime.now().isoformat()}
        st.session_state.generated_cards.insert(0, card_with_id)
        
        # Auto-create draft state
        manager.create_card_state(
            card_id=card_hash,
            card_type="resource_core",
            notes=f"{core_size} {resource_type} Core - Auto-generated"
        )
        
        st.success(f"✅ Generated card: {card_hash}")
        st.rerun()
    
    # Most recent card display
    if 'generated_cards' in st.session_state and st.session_state.generated_cards:
        st.markdown("---")
        st.subheader("🎴 Most Recent")
        
        recent = st.session_state.generated_cards[0]
        
        # Get state
        card_state = manager.get_card_state(recent['card_id'])
        state_emoji = {
            "draft": "📝",
            "published": "✅",
            "archived": "🗄️"
        }
        
        rarity_emoji = {
            "Common": "⚪",
            "Uncommon": "🔵",
            "Rare": "🔵",
            "Epic": "🟣",
            "Legendary": "🟡"
        }
        
        # Card display
        st.markdown(f"**{rarity_emoji.get(recent['rarity'], '')} {recent['size']} {recent['resource_type']} Core**")
        st.text(f"ID: {recent['card_id']}")
        st.text(f"State: {state_emoji.get(card_state.state if card_state else 'draft', '📝')} {card_state.state.title() if card_state else 'Draft'}")
        st.text(f"{recent['rarity']} | T{recent['tier']} Q{recent['quality']}")
        
        st.markdown("**Stats**")
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.text(f"💰 Cost: {recent['cost']}")
            st.text(f"⚡ RPT: {recent['rpt']}")
        with stat_col2:
            st.text(f"❤️ HP: {recent['hp']}")
            st.text(f"🔗 Links: {recent['links']}")
        
        # Quick publish button
        st.markdown("---")
        if card_state and card_state.state == "draft":
            if st.button("📤 Promote to Published", use_container_width=True):
                if manager.transition_state(recent['card_id'], "published"):
                    st.success("✅ Card published!")
                    st.rerun()
        elif card_state and card_state.state == "published":
            st.success("✅ This card is published")
            if st.button("🗄️ Archive", use_container_width=True):
                if manager.transition_state(recent['card_id'], "archived"):
                    st.success("✅ Card archived!")
                    st.rerun()

with right_col:
    st.subheader("📊 Generation History")
    
    # Show session history
    if 'generated_cards' in st.session_state and st.session_state.generated_cards:
        # Create DataFrame
        history_data = []
        for card in st.session_state.generated_cards[:50]:  # Last 50
            card_state = manager.get_card_state(card['card_id'])
            
            rarity_emoji = {
                "Common": "⚪",
                "Uncommon": "🔵",
                "Rare": "🔵",
                "Epic": "🟣",
                "Legendary": "🟡"
            }
            
            state_emoji = {
                "draft": "📝",
                "published": "✅",
                "archived": "🗄️"
            }
            
            history_data.append({
                "State": f"{state_emoji.get(card_state.state if card_state else 'draft', '📝')}",
                "Rarity": f"{rarity_emoji.get(card['rarity'], '')}",
                "Size": card['size'],
                "Type": card['resource_type'],
                "ID": card['card_id'][:8] + "...",
                "T": card['tier'],
                "Q": card['quality'],
                "Cost": card['cost'],
                "RPT": card['rpt'],
                "HP": card['hp'],
                "Links": card['links']
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Actions
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("🗑️ Clear History"):
                st.session_state.generated_cards = []
                st.rerun()
        
        with action_col2:
            if st.button("💾 Download CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download",
                    data=csv,
                    file_name=f"resource_cores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No cards generated yet. Click the generate button to create your first resource core!")

# Sidebar with stats
with st.sidebar:
    st.header("📈 Statistics")
    
    if 'generated_cards' in st.session_state and st.session_state.generated_cards:
        cards = st.session_state.generated_cards
        
        # Rarity breakdown
        st.subheader("Rarity Distribution")
        rarity_counts = {}
        for card in cards:
            rarity = card['rarity']
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        for rarity, count in sorted(rarity_counts.items()):
            rarity_emoji = {
                "Common": "⚪",
                "Uncommon": "🔵",
                "Rare": "🔵",
                "Epic": "🟣",
                "Legendary": "🟡"
            }
            st.text(f"{rarity_emoji.get(rarity, '')} {rarity}: {count}")
        
        # State breakdown
        st.subheader("Publishing States")
        state_counts = {"draft": 0, "published": 0, "archived": 0}
        for card in cards:
            card_state = manager.get_card_state(card['card_id'])
            if card_state:
                state_counts[card_state.state] += 1
        
        st.text(f"📝 Draft: {state_counts['draft']}")
        st.text(f"✅ Published: {state_counts['published']}")
        st.text(f"🗄️ Archived: {state_counts['archived']}")
        
        # Resource type breakdown
        st.subheader("Resource Types")
        type_counts = {}
        for card in cards:
            res_type = card['resource_type']
            type_counts[res_type] = type_counts.get(res_type, 0) + 1
        
        for res_type, count in sorted(type_counts.items()):
            st.text(f"⚡ {res_type}: {count}")
    else:
        st.info("Generate cards to see statistics")
    
    st.markdown("---")
    st.markdown("💡 **Tip:** Cards are automatically created in Draft state. Use the Publisher Dashboard to manage states across all card types.")
