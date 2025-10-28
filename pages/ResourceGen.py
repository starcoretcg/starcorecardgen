"""
StarCore Resource Core Generator - Streamlit Page
Adds ResourceGen to existing Streamlit app
"""

import streamlit as st
from resource_core_generator import generate_resource_core, calculate_weight

st.title("⚡ Resource Core Generator")

# Resource type selector
resource_type = st.selectbox(
    "Resource Type",
    ["Energy", "Matter", "Signal", "Life", "Omni"]
)

# Initialize session state
if 'generated_cards' not in st.session_state:
    st.session_state.generated_cards = []

# Generate button
if st.button("🎲 Generate Resource Core", type="primary", use_container_width=True):
    core = generate_resource_core(resource_type)
    st.session_state.generated_cards.insert(0, core)
    if len(st.session_state.generated_cards) > 10:
        st.session_state.generated_cards = st.session_state.generated_cards[:10]

# Display cards
if st.session_state.generated_cards:
    st.markdown("---")
    
    for core in st.session_state.generated_cards:
        rarity_emojis = {
            "Common": "⚪",
            "Uncommon": "🔵",
            "Rare": "🔵",
            "Epic": "🟣",
            "Legendary": "🟡"
        }
        
        emoji = rarity_emojis.get(core.rarity, "")
        score = (core.quality * 0.7) + (core.tier * 3)
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {emoji} {core.size} {core.resource_type} Core")
                st.code(f"ID: {core.card_id}")
                st.caption(f"{core.rarity} | T{core.tier} Q{core.quality} | Score: {score:.1f}")
            
            with col2:
                st.metric("RPT", core.rpt)
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("Cost", core.cost)
            with stat_col2:
                st.metric("HP", core.hp)
            with stat_col3:
                st.metric("Links", core.links)
            
            st.markdown("---")
else:
    st.info("👆 Click the button to generate your first resource core!")