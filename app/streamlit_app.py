import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

engine = create_engine(os.getenv("DB_URL"))

@st.cache_data
def load_monsters():
    query = """
        SELECT m.id, m.slug, m.category, m.shape, m.stage, m.height, m.weight, m.catch_rate,
               ARRAY_AGG(DISTINCT t.name) AS types,
               ARRAY_AGG(DISTINCT tg.name) AS tags,
               ARRAY_AGG(DISTINCT tr.name) AS terrains
        FROM monsters m
        LEFT JOIN monster_types mt ON m.id = mt.monster_id
        LEFT JOIN types t ON mt.type_id = t.id
        LEFT JOIN monster_tags mtg ON m.id = mtg.monster_id
        LEFT JOIN tags tg ON mtg.tag_id = tg.id
        LEFT JOIN monster_terrains mtr ON m.id = mtr.monster_id
        LEFT JOIN terrains tr ON mtr.terrain_id = tr.id
        GROUP BY m.id
        ORDER BY m.slug
    """
    return pd.read_sql(query, engine)

df = load_monsters()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Browse Tuxemon", "Build a Team"])

if page == "Browse Tuxemon":
    st.title("Tuxemon Browser")

    type_filter = st.sidebar.multiselect("Filter by Type", sorted({t for sublist in df["types"] for t in sublist}))
    tag_filter = st.sidebar.multiselect("Filter by Tag", sorted({t for sublist in df["tags"] for t in sublist}))
    terrain_filter = st.sidebar.multiselect("Filter by Terrain", sorted({t for sublist in df["terrains"] for t in sublist}))

    filtered_df = df.copy()
    if type_filter:
        filtered_df = filtered_df[filtered_df["types"].apply(lambda x: any(t in x for t in type_filter))]
    if tag_filter:
        filtered_df = filtered_df[filtered_df["tags"].apply(lambda x: any(t in x for t in tag_filter))]
    if terrain_filter:
        filtered_df = filtered_df[filtered_df["terrains"].apply(lambda x: any(t in x for t in terrain_filter))]

    st.write(f"Showing {len(filtered_df)} of {len(df)} monsters")

    for _, row in filtered_df.iterrows():
        with st.expander(f" {row['slug'].capitalize()}"):
            st.markdown(f"**Category:** {row['category']}")
            st.markdown(f"**Shape:** {row['shape']}")
            st.markdown(f"**Stage:** {row['stage']}")
            st.markdown(f"**Height:** {row['height']} cm")
            st.markdown(f"**Weight:** {row['weight']} kg")
            st.markdown(f"**Catch Rate:** {row['catch_rate']}")
            st.markdown(f"**Types:** {', '.join(row['types'])}")
            st.markdown(f"**Tags:** {', '.join(row['tags'])}")
            st.markdown(f"**Terrains:** {', '.join(row['terrains'])}")

elif page == "Build a Team":
    st.title("Tuxemon Team Builder")

    team_options = df["slug"].tolist()
    selected_team = st.multiselect("Choose up to 6 Tuxemon", team_options, max_selections=6)

    if selected_team:
        team_df = df[df["slug"].isin(selected_team)]

        st.subheader("Team Overview")
        st.markdown(f"- **Average Height:** {team_df['height'].mean():.1f} cm")
        st.markdown(f"- **Average Weight:** {team_df['weight'].mean():.1f} kg")
        st.markdown(f"- **Average Catch Rate:** {team_df['catch_rate'].mean():.1f}")

        st.subheader("Team Members")
        for _, row in team_df.iterrows():
            st.markdown(f"**{row['slug'].capitalize()}** — {', '.join(row['types'])}")

        # Save team
        st.subheader("Save This Team")
        team_name = st.text_input("Team Name")
        if st.button("Save Team") and team_name:
            with engine.begin() as conn:
                result = conn.execute(
                    "INSERT INTO teams (team_name, created_at) VALUES (%s, %s) RETURNING id",
                    (team_name, datetime.now())
                )
                team_id = result.fetchone()[0]
                for slug in selected_team:
                    monster_id = df[df["slug"] == slug]["id"].values[0]
                    conn.execute(
                        "INSERT INTO team_members (team_id, tuxemon_id) VALUES (%s, %s)",
                        (team_id, monster_id)
                    )
            st.success(f"Team '{team_name}' saved!")

    # Load saved teams
    st.subheader("Load a Saved Team")
    saved_teams = pd.read_sql("SELECT id, team_name FROM teams ORDER BY created_at DESC", engine)
    team_lookup = dict(zip(saved_teams["team_name"], saved_teams["id"]))
    selected_saved = st.selectbox("Select a team", [""] + list(team_lookup.keys()))

    if selected_saved:
        team_id = team_lookup[selected_saved]
        query = f"""
            SELECT m.slug FROM team_members tm
            JOIN monsters m ON tm.tuxemon_id = m.id
            WHERE tm.team_id = {team_id}
        """
        saved_slugs = pd.read_sql(query, engine)["slug"].tolist()
        saved_df = df[df["slug"].isin(saved_slugs)]

        st.markdown(f"### Team: {selected_saved}")
        for _, row in saved_df.iterrows():
            st.markdown(f"**{row['slug'].capitalize()}** — {', '.join(row['types'])}")
