import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="IMDb Movie Analytics Dashboard", page_icon="🎬", layout="wide")

CSV_PATH = "imdb_top_250.csv"
CH = 170   # chart height

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {display: none;}
    .block-container {padding-top: .6rem; padding-bottom: .4rem;}
    [data-testid="stVerticalBlock"] {gap: .5rem;}
    .banner {background: linear-gradient(90deg,#4a2511,#1a1a2e 60%,#0f172a);
             border-radius: 12px; padding: 12px 20px; text-align: center; color: white;}
    .banner h1 {margin: 0; font-size: 1.8rem; font-weight: 800; padding: 0;}
    .banner p {margin: 0; font-size: 1rem; opacity: .9;}
    .kpi {display: flex; align-items: center; gap: 14px; padding: 8px 18px;
          border-radius: 12px; color: white;}
    .kpi .ic {font-size: 1.8rem;}
    .kpi .kl {font-size: .8rem; font-weight: 600;}
    .kpi .kv {font-size: 1.5rem; font-weight: 800; line-height: 1.1;}
    .imdb-logo {background:#f5c518; color:#000; font-weight:900; font-size:2rem;
                border-radius:8px; padding:4px 18px; display:inline-block;}
    h3 {padding: 0 !important; font-size: 1rem !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def pick(df, options):
    for c in options:
        if c in df.columns:
            return c
    return None


def split_list(value):
    """"['Drama', 'Crime']" -> ['Drama', 'Crime']"""
    if pd.isna(value):
        return []
    text = str(value).strip().strip("[]")
    items = [v.strip().strip("'\"") for v in text.split(",")]
    return [v for v in items if v]


def kpi(col, icon, label, value, gradient):
    col.markdown(
        f'<div class="kpi" style="background:{gradient}"><div class="ic">{icon}</div>'
        f'<div><div class="kl">{label}</div><div class="kv">{value}</div></div></div>',
        unsafe_allow_html=True,
    )


# ---------- LOAD DATA (Q1 a) ----------
df = pd.read_csv(CSV_PATH)
TITLE = pick(df, ["primaryTitle", "title", "Title", "originalTitle", "name"])
GENRE = pick(df, ["genres", "genre", "Genre"])
COUNTRY = pick(df, ["countriesOfOrigin", "countryOfOrigin", "country", "Country"])
GROSS = pick(df, ["grossWorldwide", "worldwideGross"])

all_genres = sorted(set(df[GENRE].apply(split_list).explode().dropna()))
all_countries = sorted(set(df[COUNTRY].apply(split_list).explode().dropna()))
r_min, r_max = float(df["averageRating"].min()), float(df["averageRating"].max())
show_cols = [c for c in [TITLE, GENRE, COUNTRY, "averageRating", "numVotes", GROSS] if c]

# ---------- SIDEBAR ----------
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown('<span class="imdb-logo">IMDb</span>', unsafe_allow_html=True)
    st.title("Movie Analytics Dashboard")
    st.divider()
    st.markdown("### 🏠 Dashboard")
    st.markdown("### 🔍 [Movie Explorer](#movie-explorer)")
    st.markdown("### 🎥 [Movie Search (Form + Session State)](#movie-search)")
    st.divider()
    with st.expander("Dataset Information", expanded=True):               # Q4 b
        st.write("**Top 250 Movies on IMDb (2026)**")
        st.write("Rows:", len(df))
        st.write("Columns:", len(df.columns))
        st.write("This dataset contains information about the top 250 movies, "
                 "including titles, rating, votes, genres and worldwide gross.")

# ---------- BANNER ----------
if os.path.exists("banner.png"):
    st.image("banner.png", width="stretch")
else:
    st.markdown('<div class="banner"><h1>IMDb Movie Analytics Dashboard</h1>'
                '<p>Explore. Analyze. Discover.</p></div>', unsafe_allow_html=True)

# ---------- Q2 : KPIs ----------
c1, c2, c3, c4 = st.columns(4)                                            # Q2 e
kpi(c1, "🎞️", "Total Movies", len(df), "linear-gradient(90deg,#1d4ed8,#2563eb)")                       # Q2 a
kpi(c2, "⭐", "Average IMDb Rating", round(df["averageRating"].mean(), 2),
    "linear-gradient(90deg,#15803d,#22a35a)")                                                           # Q2 b
kpi(c3, "🏆", "Highest Rating", df["averageRating"].max(), "linear-gradient(90deg,#6d28d9,#7c3aed)")   # Q2 c
kpi(c4, "👥", "Total Votes", f"{df['numVotes'].sum():,}", "linear-gradient(90deg,#ea580c,#f59e0b)")    # Q2 d

st.divider()                                                              # Q4 c

# ---------- Q3 + Q4 a : TABS ----------
genre_counts = df[GENRE].apply(split_list).explode().value_counts().reset_index()
genre_counts.columns = ["Genre", "Movies"]
counts, edges = np.histogram(df["averageRating"].dropna(), bins=10)
hist_df = pd.DataFrame({
    "Rating Range": [f"{edges[i]:.1f}-{edges[i+1]:.1f}" for i in range(len(counts))],
    "Movies": counts,
})
top10 = df.sort_values(GROSS, ascending=False).head(10)


def chart_genre():
    st.subheader("📊 Movies by Genre")                                    # Q3 a
    st.bar_chart(genre_counts.head(8), x="Genre", y="Movies", sort="-Movies", height=CH,
                 x_label="Genre", y_label="Count", color="#2563eb")


def chart_hist():
    st.subheader("📊 IMDb Rating Distribution")                           # Q3 b
    st.bar_chart(hist_df, x="Rating Range", y="Movies", sort=False, height=CH,
                 x_label="IMDb Rating", y_label="Count", color="#3b82f6")


def chart_scatter():
    st.subheader("✨ Rating vs Number of Votes")                          # Q3 c
    st.scatter_chart(df, x="averageRating", y="numVotes", height=CH,
                     x_label="IMDb Rating", y_label="Number of Votes", color="#3b82f6")


def chart_gross():
    st.subheader("🏆 Top 10 Movies by Worldwide Gross")                   # Q3 d
    st.bar_chart(top10, x=TITLE, y=GROSS, sort=f"-{GROSS}", horizontal=True, height=CH,
                 x_label="Worldwide Gross (USD)", y_label="Movie Title", color="#f59e0b")


tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Genre Analysis", "🥧 Rating Analysis", "🪙 Gross Collection", "📂 Dataset Overview"])

with tab1:
    a, b = st.columns(2)
    with a.container(border=True):
        chart_genre()
    with b.container(border=True):
        chart_hist()
    c, d = st.columns(2)
    with c.container(border=True):
        chart_scatter()
    with d.container(border=True):
        chart_gross()

with tab2:
    a, b = st.columns(2)
    with a.container(border=True):
        chart_hist()
    with b.container(border=True):
        chart_scatter()

with tab3:
    with st.container(border=True):
        chart_gross()

with tab4:                                                                # Q1
    st.success("Dataset loaded successfully!")                            # Q1 d
    st.subheader("First 10 records")                                      # Q1 a
    st.dataframe(df.head(10))
    st.subheader("Dataset information")                                   # Q1 b
    st.write("**Total rows:**", df.shape[0], " | **Total columns:**", df.shape[1])
    st.write("**Column names:**", list(df.columns))
    st.dataframe(df.dtypes.astype(str).rename("dtype"))
    st.subheader("Missing values per column")                             # Q1 c
    st.dataframe(df.isnull().sum().rename("missing"))

st.success("Dashboard loaded successfully! Enjoy exploring the top 250 movies on IMDb.")   # Q4 c

# ---------- Q5 (left) + Q6 (right) ----------
left, right = st.columns([2, 1])

with left.container(border=True):
    st.subheader("🔍 Interactive Movie Explorer", anchor="movie-explorer")

    def reset_filters():                                                  # Q5 h
        st.session_state["genre_sel"] = "All"
        st.session_state["country_sel"] = []
        st.session_state["rating_sel"] = (r_min, r_max)
        st.session_state["votes_sel"] = 0
        st.session_state["title_sel"] = ""
        st.session_state["sort_sel"] = "Descending"

    f1, f2, f3, f4, f5, f6 = st.columns(6)
    genre = f1.selectbox("Genre", ["All"] + all_genres, key="genre_sel")                    # Q5 a
    countries = f2.multiselect("Countries", all_countries, key="country_sel")               # Q5 b
    rating_range = f3.slider("IMDb Rating", r_min, r_max, (r_min, r_max),
                             step=0.1, key="rating_sel")                                    # Q5 c
    min_votes = f4.number_input("Min Votes", min_value=0, value=0, step=10000,
                                key="votes_sel")                                            # Q5 d
    search = f5.text_input("Search Title", placeholder="Enter movie title...",
                           key="title_sel")                                                 # Q5 e
    order = f6.radio("Sort Order", ["Ascending", "Descending"], index=1,
                     key="sort_sel")                                                        # Q5 f

    filtered_df = df.copy()
    if genre != "All":
        filtered_df = filtered_df[filtered_df[GENRE].apply(lambda v: genre in split_list(v))]
    if countries:
        filtered_df = filtered_df[
            filtered_df[COUNTRY].apply(lambda v: any(x in split_list(v) for x in countries))]
    filtered_df = filtered_df[(filtered_df["averageRating"] >= rating_range[0])
                              & (filtered_df["averageRating"] <= rating_range[1])]
    filtered_df = filtered_df[filtered_df["numVotes"] >= min_votes]
    if search:
        filtered_df = filtered_df[
            filtered_df[TITLE].astype(str).str.contains(search, case=False, na=False)]
    filtered_df = filtered_df.sort_values("averageRating", ascending=(order == "Ascending"))

    b1, b2, _ = st.columns([1, 1, 3])
    b1.info(f"Filtered Movies: {len(filtered_df)}")                                         # Q5 g
    b2.button("🔄 Reset Filters", on_click=reset_filters)                                   # Q5 h
    st.dataframe(filtered_df[show_cols], width="stretch", height=140)                       # Q5 h

with right.container(border=True):
    st.subheader("🔎 Movie Search (Form + Session State)", anchor="movie-search")

    if "selected_movie" not in st.session_state:                                            # Q6 a
        st.session_state.selected_movie = None

    with st.form("movie_search_form"):                                                      # Q6 b
        f_title = st.text_input("Movie Title", placeholder="e.g. Inception")
        f_genre = st.selectbox("Preferred Genre", ["Any"] + all_genres)
        f_rating = st.slider("Minimum IMDb Rating", r_min, r_max, r_min, step=0.1)
        submitted = st.form_submit_button("🔍 Search Movie", width="stretch")               # Q6 c

    if submitted:
        result = df.copy()
        if f_title:
            result = result[result[TITLE].astype(str).str.contains(f_title, case=False, na=False)]
        if f_genre != "Any":
            result = result[result[GENRE].apply(lambda v: f_genre in split_list(v))]
        result = result[result["averageRating"] >= f_rating]
        if len(result) > 0:
            st.session_state.selected_movie = result.iloc[0].to_dict()
            st.success(f"{len(result)} matching movie(s) found.")                           # Q6 e
        else:
            st.session_state.selected_movie = None
            st.info("No matching movie found. Try different preferences.")                  # Q6 e

    movie = st.session_state.selected_movie                                                 # Q6 d
    if movie:
        p1, p2 = st.columns([1, 3])
        poster = movie.get("primaryImage")
        if isinstance(poster, str) and poster.startswith("http"):
            p1.image(poster, width="stretch")
        p2.success(f"**{movie[TITLE]}**  \n"
                   f"Genre: {', '.join(split_list(movie[GENRE]))}  |  "
                   f"IMDb Rating: {movie['averageRating']}  |  Votes: {int(movie['numVotes']):,}")