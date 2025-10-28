"""
StarCore Resource Core Generator - Streamlit Page
WITH DATABASE PERSISTENCE AND STATE MANAGEMENT
"""

import streamlit as st
import pandas as pd
from resource_core_generator import generate_resource_core, calculate_weight
from card_database import (
    init_database, save_card, load_recent_cards, clear_all_cards,
    update_card_state, can_transition
)

st.title("⚡ Resource Core Generator")

# Initialize database
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Load cards from database
if 'cards_loaded' not in st.session_state:
    db_cards = load_recent_cards(limit=100)
    st.session_state.generated_cards = db_cards
    st.session_state.cards_loaded = True

# ============ GENERATOR SECTION ============
st.header("🎲 Generator")

gen_col1, gen_col2, gen_col3 = st.columns(3)

with gen_col1:
    core_size = st.selectbox("Core Size", ["Random", "Small", "Medium", "Large", "Massive"])

with gen_col2:
    resource_type = st.selectbox("Resource Type", ["Energy", "Matter", "Signal", "Life", "Omni"])

with gen_col3:
    st.write("")  # Spacer
    st.write("")  # Spacer
    if st.button("🎲 Generate", type="primary", use_container_width=True):
        core = generate_resource_core(resource_type)
        
        if core_size != "Random":
            attempts = 0
            while core.size != core_size and attempts < 100:
                core = generate_resource_core(resource_type)
                attempts += 1
        
        # Save with draft state
        if save_card(core, card_type="Resource Core", state="draft", notes="Auto-generated"):
            st.session_state.generated_cards.insert(0, core)
            st.success("✅ Card saved as Draft!")
            st.rerun()

# Most recent card display
if st.session_state.generated_cards:
    st.markdown("---")
    st.subheader("🎴 Most Recent Card")
    
    core = st.session_state.generated_cards[0]
    score = (core.quality * 0.7) + (core.tier * 3)
    
    # State badge
    state_emoji = {
        "draft": "📝",
        "published": "✅",
        "archived": "🗄️"
    }
    state = getattr(core, 'state', 'draft')
    st.markdown(f"### {state_emoji.get(state, '📝')} {state.upper()}")
    
    recent_col1, recent_col2, recent_col3, recent_col4 = st.columns(4)
    
    with recent_col1:
        st.metric("Size", core.size)
        st.metric("Type", core.resource_type)
    
    with recent_col2:
        st.metric("Tier", core.tier)
        st.metric("Quality", core.quality)
    
    with recent_col3:
        st.metric("Rarity", core.rarity)
        st.metric("Score", f"{score:.1f}")
    
    with recent_col4:
        st.metric("Cost", core.cost)
        st.metric("RPT", core.rpt)
    
    st.code(f"ID: {core.card_id}", language=None)
    
    # State transition buttons
    st.markdown("---")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if state == "draft" and can_transition(core.card_id, "published"):
            if st.button("📤 Promote to Published", use_container_width=True, type="primary"):
                if update_card_state(core.card_id, "published"):
                    st.success("✅ Card published!")
                    st.rerun()
    
    with btn_col2:
        if state == "published" and can_transition(core.card_id, "archived"):
            if st.button("🗄️ Archive Card", use_container_width=True):
                if update_card_state(core.card_id, "archived"):
                    st.success("✅ Card archived!")
                    st.rerun()
    
    with btn_col3:
        if state == "draft" and can_transition(core.card_id, "archived"):
            if st.button("🗑️ Skip to Archived", use_container_width=True):
                if update_card_state(core.card_id, "archived"):
                    st.success("✅ Card archived!")
                    st.rerun()

# ============ SEARCH/FILTER SECTION ============
st.markdown("---")
st.header("🔍 Card History")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    search_state = st.multiselect("Filter by State", ["draft", "published", "archived"])

with filter_col2:
    search_rarity = st.multiselect("Filter by Rarity", ["Common", "Uncommon", "Rare", "Epic", "Legendary"])

with filter_col3:
    search_size = st.multiselect("Filter by Size", ["Small", "Medium", "Large", "Massive"])

with filter_col4:
    search_type = st.multiselect("Filter by Type", ["Energy", "Matter", "Signal", "Life", "Omni"])

# Apply filters
filtered_cards = st.session_state.generated_cards

if search_state:
    filtered_cards = [c for c in filtered_cards if getattr(c, 'state', 'draft') in search_state]

if search_rarity:
    filtered_cards = [c for c in filtered_cards if c.rarity in search_rarity]

if search_size:
    filtered_cards = [c for c in filtered_cards if c.size in search_size]

if search_type:
    filtered_cards = [c for c in filtered_cards if c.resource_type in search_type]

st.caption(f"Showing {len(filtered_cards)} of {len(st.session_state.generated_cards)} cards")

# ============ DATA TABLE ============
if filtered_cards:
    data = []
    for core in filtered_cards:
        score = (core.quality * 0.7) + (core.tier * 3)
        state = getattr(core, 'state', 'draft')
        state_emoji = {"draft": "📝", "published": "✅", "archived": "🗄️"}
        
        data.append({
            "State": f"{state_emoji.get(state, '📝')}",
            "Rarity": core.rarity,
            "Size": core.size,
            "Type": core.resource_type,
            "ID": core.card_id[:8],
            "T": core.tier,
            "Q": core.quality,
            "Cost": core.cost,
            "RPT": core.rpt,
            "HP": core.hp,
            "Links": core.links,
            "Score": round(score, 1)
        })
    
    df = pd.DataFrame(data)
    
    st.dataframe(df, use_container_width=True, height=400, hide_index=True)
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="starcore_resources.csv", mime="text/csv", use_container_width=True)
    
    with btn_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if clear_all_cards(card_type="Resource Core"):
                st.session_state.generated_cards = []
                st.success("✅ Cleared!")
                st.rerun()
    
    with btn_col3:
        st.button("🎲 Batch Generate (Soon)", disabled=True, use_container_width=True)

# ============ STATISTICS SECTION ============
if st.session_state.generated_cards:
    st.markdown("---")
    st.header("📈 Statistics")
    
    total = len(st.session_state.generated_cards)
    avg_quality = sum(c.quality for c in st.session_state.generated_cards) / total
    avg_tier = sum(c.tier for c in st.session_state.generated_cards) / total
    epic_plus = len([c for c in st.session_state.generated_cards if c.rarity in ["Epic", "Legendary"]])
    epic_rate = (epic_plus / total) * 100
    
    # Add state counts
    draft_count = len([c for c in st.session_state.generated_cards if getattr(c, 'state', 'draft') == 'draft'])
    published_count = len([c for c in st.session_state.generated_cards if getattr(c, 'state', 'draft') == 'published'])
    archived_count = len([c for c in st.session_state.generated_cards if getattr(c, 'state', 'draft') == 'archived'])
    
    stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
    
    with stat_col1:
        st.metric("Total Cards", total)
    with stat_col2:
        st.metric("📝 Drafts", draft_count)
    with stat_col3:
        st.metric("✅ Published", published_count)
    with stat_col4:
        st.metric("🗄️ Archived", archived_count)
    with stat_col5:
        st.metric("Epic+ Rate", f"{epic_rate:.1f}%")
    
    # Distribution charts
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.subheader("Rarity")
        rarity_counts = {}
        for c in st.session_state.generated_cards:
            rarity_counts[c.rarity] = rarity_counts.get(c.rarity, 0) + 1
        st.bar_chart(pd.DataFrame({"Count": list(rarity_counts.values())}, index=list(rarity_counts.keys())))
    
    with chart_col2:
        st.subheader("Size")
        size_counts = {}
        for c in st.session_state.generated_cards:
            size_counts[c.size] = size_counts.get(c.size, 0) + 1
        st.bar_chart(pd.DataFrame({"Count": list(size_counts.values())}, index=list(size_counts.keys())))
    
    with chart_col3:
        st.subheader("Type")
        type_counts = {}
        for c in st.session_state.generated_cards:
            type_counts[c.resource_type] = type_counts.get(c.resource_type, 0) + 1
        st.bar_chart(pd.DataFrame({"Count": list(type_counts.values())}, index=list(type_counts.keys())))
    
    # Quality histogram
    st.subheader("Quality Distribution")
    quality_brackets = {"Q1-20": 0, "Q21-40": 0, "Q41-60": 0, "Q61-80": 0, "Q81-100": 0}
    
    for c in st.session_state.generated_cards:
        if c.quality <= 20:
            quality_brackets["Q1-20"] += 1
        elif c.quality <= 40:
            quality_brackets["Q21-40"] += 1
        elif c.quality <= 60:
            quality_brackets["Q41-60"] += 1
        elif c.quality <= 80:
            quality_brackets["Q61-80"] += 1
        else:
            quality_brackets["Q81-100"] += 1
    
    st.bar_chart(pd.DataFrame({"Count": list(quality_brackets.values())}, index=list(quality_brackets.keys())))
else:
    st.info("👆 Generate your first card to see statistics!")