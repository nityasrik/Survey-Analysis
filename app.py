import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    page_title="Digital Focus Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
# Inject CSS for a cleaner, more professional UI
st.markdown(
    """
<style>
    /* Main app background - simplified */
    .main {
        background-color: #f8f9fa;
        padding: 10px;
    }
    
    /* Sidebar styling - simplified */
    .css-1d391kg {
        background-color: #2c3e50;
        border-right: 2px solid #3498db;
    }
    
    /* KPI Metric styling - simplified */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Insight box styling - simplified */
    .insight-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        border: none;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        font-weight: 500;
    }
    
    .trend-highlight {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        border: none;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        font-weight: 500;
    }
    
    .success-box {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        border: none;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        border: none;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        font-weight: 500;
    }
    
    /* Button styling - simplified */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 20px;
        padding: 8px 20px;
        color: white;
        font-weight: 600;
    }
    
    /* Tab styling - simplified */
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 8px 16px;
        color: #2c3e50;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Text styling */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* Sidebar text */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white;
    }
    
    /* Chart containers - simplified */
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>""",
    unsafe_allow_html=True,
)


# --- Data Loading & Caching ---
@st.cache_data
def load_and_clean_data(file_path):
    """Loads and preprocesses the survey data, cached for performance."""
    try:
        df = pd.read_csv(file_path)
        # Clean column names by stripping leading/trailing whitespace
        df.columns = df.columns.str.strip()

        # --- Data Cleaning Step for 'Occupation' ---
        # Simplify long and combined occupation titles for better readability
        occupation_mapping = {
            "Working Profesional": "Working Professional",  # Correcting typo
            "Working Profesional, Freelancer / Self-Employed": "Hybrid Professional",
            "Student, Freelancer / Self-Employed": "Student & Freelancer",
        }
        df["Occupation"] = df["Occupation"].replace(occupation_mapping)

        return df
    except FileNotFoundError:
        return None


# --- Helper Functions for Insights ---
def get_attention_insight(filtered_df):
    """Generate insights about attention patterns"""
    if filtered_df.empty:
        return "No data available for selected filters."
    
    avg_attention = filtered_df["Attention Rating"].mean()
    
    if avg_attention >= 4:
        return f"High average attention rating: {avg_attention:.1f}/5."
    elif avg_attention >= 3:
        return f"Moderate average attention rating: {avg_attention:.1f}/5."
    else:
        return f"Low average attention rating: {avg_attention:.1f}/5. Consider exploring coping strategies."


def get_distraction_insight(filtered_df):
    """Generate insights about distraction patterns"""
    if filtered_df.empty:
        return "No data available for selected filters."
    
    avg_distraction = filtered_df["Distraction Rating"].mean()
    
    if avg_distraction <= 2:
        return f"Low distraction: {avg_distraction:.1f}/5."
    elif avg_distraction <= 3:
        return f"Moderate distraction: {avg_distraction:.1f}/5."
    else:
        return f"High distraction: {avg_distraction:.1f}/5."


def get_screen_time_insight(filtered_df):
    """Generate insights about screen time patterns"""
    if filtered_df.empty:
        return "No data available for selected filters."
    
    screen_time_dist = filtered_df["Screen TIme"].value_counts()
    most_common = screen_time_dist.idxmax()
    count = screen_time_dist.max()
    
    return f"Most common screen time: {most_common} ({count} respondents)"


def get_platform_insight(platform_counts):
    """Generate insights about platform usage"""
    if not platform_counts:
        return "No platform data available."
    
    top_platform = max(platform_counts.items(), key=lambda x: x[1])
    return f"Most popular platform: {top_platform[0]} ({top_platform[1]} users)"


def get_strategy_insight(strategy_data):
    """Generate insights about coping strategies"""
    if strategy_data.empty:
        return "No strategy data available."
    
    avg_effectiveness = strategy_data["Strategy Affectiveness"].mean()
    most_effective = strategy_data.groupby("Cleaned Strategies")["Strategy Affectiveness"].mean().idxmax()
    
    return f"Average effectiveness is {avg_effectiveness:.1f}/5. '{most_effective}' is rated most effective."


# --- Main Application ---
def main():
    # Load data
    df = load_and_clean_data("survey.csv")
    if df is None:
        st.error("Error: The data file 'survey.csv' was not found.")
        st.info(
            "Please make sure the data file is in the same folder as your Streamlit app script."
        )
        return

    # --- Simple Sidebar for Filters ---
    with st.sidebar:
        # Simple sidebar header
        st.markdown("## 🎛️ Dashboard Controls")
        st.markdown("Use the filters below to explore the data.")
        st.markdown("💡 **Tip:** Select specific groups to see targeted insights!")
        st.markdown("---")

        # Simple filter sections
        st.markdown("### 🎯 Filter Options")
        
        # Age Group Filter
        st.markdown("**Age Groups:**")
        age_options = sorted(df["Age Group"].unique().tolist())
        selected_ages = st.multiselect(
            "Choose age groups to analyze",
            age_options, 
            default=age_options,
            help="Select one or more age groups to filter the data"
        )

        st.markdown("---")

        # Occupation Filter
        st.markdown("**Occupations:**")
        occupation_options = sorted(df["Occupation"].unique().tolist())
        selected_occupations = st.multiselect(
            "Choose occupations to analyze",
            occupation_options, 
            default=occupation_options,
            help="Select one or more occupations to filter the data"
        )

        st.markdown("---")

        # Reset Filters Button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()

        # Quick Stats in Sidebar
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        total_respondents = df.shape[0]
        st.metric("📈 Total Respondents", total_respondents)
        
        # Show filtered count
        filtered_df = df[
            df["Age Group"].isin(selected_ages)
            & df["Occupation"].isin(selected_occupations)
        ]
        
        filtered_count = filtered_df.shape[0]
        percentage = (filtered_count / total_respondents * 100) if total_respondents > 0 else 0
        
        st.metric(
            "🎯 Selected Respondents", 
            filtered_count,
            f"{percentage:.1f}% of total"
        )
        
        # Add a visual indicator
        if filtered_count > 0:
            st.progress(filtered_count / total_respondents)
            st.caption(f"Showing {filtered_count} out of {total_respondents} respondents")
        
        # Add helpful tips
        st.markdown("---")
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        - Use specific filters for targeted insights
        - Compare different demographics
        - Check the Summary tab for recommendations
        """)

    # Filter DataFrame based on selections
    if not selected_ages or not selected_occupations:
        st.warning(
            "Please select at least one Age Group and Occupation to display the data."
        )
        return

    filtered_df = df[
        df["Age Group"].isin(selected_ages)
        & df["Occupation"].isin(selected_occupations)
    ]

    # --- Main Panel ---
    # Create a simple but beautiful header
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h1 style="color: white; margin: 0; font-size: 2em; font-weight: 700;">
                🧠 Digital Behavior & Focus Dashboard
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                An interactive analysis of post-COVID attention spans and digital habits
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add a progress indicator
    if filtered_df.empty:
        st.warning("⚠️ Please select at least one Age Group and Occupation to display the data.")
        return

    # Show data loading progress
    with st.spinner("🔄 Loading your personalized insights..."):
        pass

    # --- KPI Metrics with Simple Styling ---
    st.markdown("## 📊 Key Performance Indicators")
    
    total_respondents = filtered_df.shape[0]
    avg_attention = (
        round(filtered_df["Attention Rating"].mean(), 1) if not filtered_df.empty else 0
    )
    avg_distraction = (
        round(filtered_df["Distraction Rating"].mean(), 1)
        if not filtered_df.empty
        else 0
    )

    # Simple KPI layout
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric(
            label="👥 Selected Respondents", 
            value=total_respondents,
            help="Number of people matching your selected filters"
        )
    
    with kpi2:
        attention_color = "🟢" if avg_attention >= 4 else "🟡" if avg_attention >= 3 else "🔴"
        st.metric(
            label="🎯 Avg. Attention Rating (1-5)", 
            value=f"{avg_attention} {attention_color}",
            help="Average self-reported attention span rating"
        )
    
    with kpi3:
        distraction_color = "🟢" if avg_distraction <= 2 else "🟡" if avg_distraction <= 3 else "🔴"
        st.metric(
            label="⚠️ Avg. Distraction Rating (1-5)", 
            value=f"{avg_distraction} {distraction_color}",
            help="Average self-reported distraction level"
        )

    # Simple KPI Insights
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="insight-box">{get_attention_insight(filtered_df)}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="insight-box">{get_distraction_insight(filtered_df)}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Simple Tabbed Interface ---
    st.markdown("## Explore Your Data")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Demographics", "Digital Habits", "Coping Strategies", "NLP Analysis", "Summary"]
    )

    with tab1:
        st.header("Respondent Demographics")
        st.markdown(
            "This section shows the age and occupation breakdown of survey respondents. "
            "Understanding demographics helps contextualize digital behavior patterns and identify "
            "which groups might need more support with focus and digital wellness."
        )
        
        if filtered_df.empty:
            st.info("No data available for the selected filters.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                age_counts = filtered_df["Age Group"].value_counts()
                fig_age = px.pie(
                    names=age_counts.index,
                    values=age_counts.values,
                    title="Age Group Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_age.update_traces(
                    hovertemplate="<b>Age Group:</b> %{label}<br><b>Respondents:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>",
                    textinfo='label+percent',
                    textfont_size=12,
                    marker=dict(line=dict(color='white', width=2))
                )
                fig_age.update_layout(
                    showlegend=False,
                    title_font_size=18,
                    title_font_color="#2c3e50",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=50, b=50, l=50, r=50)
                )
                st.plotly_chart(fig_age, use_container_width=True)
                
                # Age insights
                dominant_age = age_counts.idxmax()
                dominant_count = age_counts.max()
                st.caption(
                    f"Key finding: {dominant_age} age group dominates with {dominant_count} respondents "
                    f"({(dominant_count/total_respondents)*100:.1f}% of selected group)."
                )

            with col2:
                occupation_counts = filtered_df["Occupation"].value_counts()
                fig_occ = px.bar(
                    x=occupation_counts.values,
                    y=occupation_counts.index,
                    orientation="h",
                    title="Occupation Distribution",
                    labels={"x": "Number of Respondents", "y": ""},
                    color=occupation_counts.values,
                    color_continuous_scale=px.colors.sequential.Blues_r,
                )
                fig_occ.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_occ, use_container_width=True)
                
                # Occupation insights
                dominant_occ = occupation_counts.idxmax()
                dominant_occ_count = occupation_counts.max()
                st.caption(
                    f"Key finding: {dominant_occ} is the most common occupation "
                    f"with {dominant_occ_count} respondents."
                )

            # Cross-demographic insight
            st.markdown(f'<div class="trend-highlight">'
                       f'<b>Demographic Insight:</b> The {dominant_age} age group and {dominant_occ} occupation '
                       f'combination represents the largest segment in your selected data.'
                       f'</div>', unsafe_allow_html=True)

    with tab2:
        st.header("Digital Usage Habits")
        st.markdown(
            "Explore which platforms are most popular and how screen time relates to distraction levels. "
            "This helps identify potential digital wellness interventions and understand "
            "the relationship between usage patterns and focus challenges."
        )
        
        if filtered_df.empty:
            st.info("No data available for the selected filters.")
        else:
            # Platform usage analysis
            platform_column = "Platforms used"
            platforms = filtered_df[platform_column].dropna().str.split(", ")
            platform_counts = Counter(
                item.strip() for sublist in platforms for item in sublist
            )
            platform_df = pd.DataFrame(
                platform_counts.items(), columns=["Platform", "Count"]
            ).sort_values("Count", ascending=True)
            platform_df = platform_df[
                ~platform_df["Platform"].str.contains("etc.", na=False)
            ]

            fig_plat = px.bar(
                platform_df,
                x="Count",
                y="Platform",
                orientation="h",
                title="Most Commonly Used Digital Platforms",
                color="Count",
                color_continuous_scale=px.colors.sequential.Tealgrn_r,
            )
            fig_plat.update_layout(coloraxis_showscale=False, yaxis_title=None)
            st.plotly_chart(fig_plat, use_container_width=True)
            
            # Platform insight
            st.caption(get_platform_insight(platform_counts))

            # Screen time vs distraction analysis
            screen_time_order = [
                "Less than 3 hours",
                "3–5 hours",
                "6–8 hours",
                "9+ hours",
            ]

            # New: Toggle between 'Box plot (distribution)' and 'Average bar chart'
            view_type = st.radio(
                "Chart view",
                ["Average (easier)", "Distribution (box plot)"],
                index=0,
                help="Switch between a simple average bar chart and the detailed distribution view",
                horizontal=True,
                key="screen_time_view",
            )

            if view_type == "Average (easier)":
                avg_by_time = (
                    filtered_df.groupby("Screen TIme")["Distraction Rating"].mean().reindex(screen_time_order)
                )
                count_by_time = (
                    filtered_df.groupby("Screen TIme")["Distraction Rating"].count().reindex(screen_time_order)
                )
                avg_df = (
                    pd.DataFrame({"Screen TIme": avg_by_time.index, "Avg Distraction": avg_by_time.values, "N": count_by_time.values})
                    .dropna()
                )
                fig_dist = px.bar(
                    avg_df,
                    x="Screen TIme",
                    y="Avg Distraction",
                    color="Avg Distraction",
                    color_continuous_scale=px.colors.sequential.OrRd,
                    text=avg_df["Avg Distraction"].round(2),
                    title="Average Distraction Rating by Daily Screen Time",
                    category_orders={"Screen TIme": screen_time_order},
                    labels={"Screen TIme": "Screen Time", "Avg Distraction": "Average Distraction (1-5)"},
                )
                fig_dist.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Avg: %{y:.2f} / 5<br>N: %{customdata[0]}<extra></extra>", customdata=avg_df[["N"]])
                fig_dist.update_layout(yaxis_range=[0,5], coloraxis_showscale=False)
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                fig_dist = px.box(
                    filtered_df,
                    x="Screen TIme",
                    y="Distraction Rating",
                    title="Self-Rated Distraction by Daily Screen Time",
                    category_orders={"Screen TIme": screen_time_order},
                    labels={"Screen TIme": "Screen Time", "Distraction Rating": "Distraction Rating (1-5)"},
                )
                fig_dist.update_traces(
                    hovertemplate="<b>Screen Time:</b> %{x}<br><b>Distraction Rating:</b> %{y}<extra></extra>",
                    marker_color="#FF6347",
                )
                fig_dist.update_layout(showlegend=False)
                st.plotly_chart(fig_dist, use_container_width=True)
            
            # Screen time insight (aligned to selected view)
            st.caption(get_screen_time_insight(filtered_df))

            # Trend analysis based on averages for clarity
            screen_time_distraction = filtered_df.groupby("Screen TIme")["Distraction Rating"].mean()
            if len(screen_time_distraction) > 1:
                screen_time_distraction = screen_time_distraction.reindex(screen_time_order).dropna()
                highest_distraction_time = screen_time_distraction.idxmax()
                highest_distraction_value = screen_time_distraction.max()
                st.markdown(f'<div class="trend-highlight">'
                           f'<b>Key Trend:</b> Users with "{highest_distraction_time}" screen time report '
                           f'the highest <b>average</b> distraction rating ({highest_distraction_value:.1f}/5). '
                           f'This suggests a correlation between excessive screen time and reduced focus.'
                           f'</div>', unsafe_allow_html=True)

    with tab3:
        st.header("Analysis of Coping Strategies")
        st.markdown(
            "Discover which strategies people use to manage digital distractions and how effective they find them. "
            "This information can help identify the most successful approaches for improving focus "
            "and digital wellness across different demographics."
        )
        
        if filtered_df.empty:
            st.info("No data available for the selected filters.")
        else:
            strategy_col = "Cleaned Strategies"
            effectiveness_col = "Strategy Affectiveness"
            strategy_data = filtered_df[[strategy_col, effectiveness_col]].dropna()

            if not strategy_data.empty:
                strategy_data = strategy_data.assign(
                    **{strategy_col: strategy_data[strategy_col].str.split(", ")}
                ).explode(strategy_col)
                strategy_data[strategy_col] = strategy_data[strategy_col].str.strip()
                unwanted_strategies = [
                    "Na",
                    "which is often on-screen",
                    "recenter on chosen task",
                ]
                strategy_data = strategy_data[
                    ~strategy_data[strategy_col].isin(unwanted_strategies)
                ]
                strategy_data = strategy_data[
                    strategy_data[strategy_col].str.len() < 35
                ]

                # New: toggle for easier average view vs distribution
                strat_view = st.radio(
                    "Chart view",
                    ["Average (easier)", "Distribution (box plot)"],
                    index=0,
                    horizontal=True,
                    help="Switch between a simple average bar chart and the detailed distribution view",
                    key="strategy_view",
                )

                if strat_view == "Average (easier)":
                    mean_effect = (
                        strategy_data.groupby("Cleaned Strategies")["Strategy Affectiveness"].agg(["mean", "count"]).reset_index()
                    )
                    mean_effect = mean_effect.sort_values("mean", ascending=True)
                    fig_strat = px.bar(
                        mean_effect,
                        x="mean",
                        y="Cleaned Strategies",
                        orientation="h",
                        text=mean_effect["mean"].round(2),
                        color="mean",
                        color_continuous_scale=px.colors.sequential.Tealgrn,
                        labels={"mean": "Average Effectiveness (1-5)", "Cleaned Strategies": ""},
                        title="Average Effectiveness of Coping Strategies",
                    )
                    fig_strat.update_traces(textposition="outside", hovertemplate="<b>%{y}</b><br>Avg: %{x:.2f} / 5<br>N: %{customdata[0]}<extra></extra>", customdata=mean_effect[["count"]])
                    fig_strat.update_layout(coloraxis_showscale=False, xaxis_range=[0,5])
                    st.plotly_chart(fig_strat, use_container_width=True)
                else:
                    fig_strat = px.box(
                        strategy_data,
                        x="Strategy Affectiveness",
                        y="Cleaned Strategies",
                        title="Effectiveness of Different Coping Strategies",
                    )
                    fig_strat.update_traces(
                        hovertemplate="<b>Strategy:</b> %{y}<br><b>Effectiveness:</b> %{x}<extra></extra>",
                        marker_color="#20B2AA",
                    )
                    fig_strat.update_layout(
                        showlegend=False,
                        yaxis={"categoryorder": "total ascending"},
                        yaxis_title=None,
                        xaxis_title="Self-Rated Effectiveness (1-5)",
                    )
                    st.plotly_chart(fig_strat, use_container_width=True)

                # Strategy insight (no emoji)
                st.caption(get_strategy_insight(strategy_data))

                # Most effective strategy recommendation (no emoji)
                strategy_effectiveness = strategy_data.groupby("Cleaned Strategies")["Strategy Affectiveness"].mean()
                if not strategy_effectiveness.empty:
                    best_strategy = strategy_effectiveness.idxmax()
                    best_rating = strategy_effectiveness.max()
                    st.markdown(f'<div class="trend-highlight">'
                               f'<b>Top recommendation:</b> "{best_strategy}" is rated most effective '
                               f'({best_rating:.1f}/5) among your selected group.'
                               f'</div>', unsafe_allow_html=True)
            else:
                st.info("No coping strategy data available for the selected filters.")

    with tab4:
        st.header("Relationship with Technology Word Cloud")
        st.markdown(
            "This word cloud visualizes the most common terms respondents use to describe their relationship with technology. "
            "It reveals emotional patterns, concerns, and attitudes toward digital devices, "
            "helping understand the psychological impact of technology on daily life."
        )
        
        if filtered_df.empty:
            st.info("No data available for the selected filters.")
        else:
            st.write(
                "**What this shows:** The larger the word, the more frequently it appears in responses. "
                "This helps identify common themes in how people perceive their tech relationship."
            )

            nlp_column = "Tech Relationship"
            text_data = " ".join(
                str(feedback) for feedback in filtered_df[nlp_column].dropna()
            )

            if text_data.strip():
                wordcloud = WordCloud(
                    width=1200,
                    height=600,
                    background_color="#FFFFFF",
                    colormap="plasma",
                    collocations=False,
                ).generate(text_data)

                fig_wc, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig_wc)
                
                # Word cloud insights
                st.caption(
                    "Sentiment note: The word cloud reveals common themes in how people describe "
                    "their relationship with technology. Look for patterns in emotional language and concerns."
                )
            else:
                st.info(
                    "No text data available to generate a word cloud for the selected filters."
                )

    with tab5:
        st.header("Executive Summary")
        st.markdown(
            "A comprehensive overview of key findings and actionable insights from the digital behavior analysis."
        )
        
        if filtered_df.empty:
            st.info("No data available for the selected filters.")
        else:
            # Key metrics summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Key Metrics")
                st.metric("Average Attention Rating", f"{avg_attention}/5")
                st.metric("Average Distraction Rating", f"{avg_distraction}/5")
                st.metric("Total Respondents Analyzed", total_respondents)
                
                # Screen time distribution
                screen_time_dist = filtered_df["Screen TIme"].value_counts()
                most_common_screen_time = screen_time_dist.idxmax()
                st.metric("Most Common Screen Time", most_common_screen_time)
            
            with col2:
                st.subheader("Demographics Summary")
                age_dist = filtered_df["Age Group"].value_counts()
                dominant_age_group = age_dist.idxmax()
                st.metric("Dominant Age Group", dominant_age_group)
                
                occ_dist = filtered_df["Occupation"].value_counts()
                dominant_occupation = occ_dist.idxmax()
                st.metric("Dominant Occupation", dominant_occupation)
                
                # Focus duration
                focus_dist = filtered_df["Focus Duration"].value_counts()
                most_common_focus = focus_dist.idxmax()
                st.metric("Most Common Focus Duration", most_common_focus)
            
            # Key insights summary
            st.subheader("Key Insights")

            # Correlation and relationships
            # Encode screen time as ordinal for simple correlation
            screen_time_map = {
                "Less than 3 hours": 1,
                "3–5 hours": 2,
                "6–8 hours": 3,
                "9+ hours": 4,
            }
            df_corr = filtered_df.copy()
            df_corr = df_corr[df_corr["Screen TIme"].isin(screen_time_map.keys())]
            df_corr["screen_time_num"] = df_corr["Screen TIme"].map(screen_time_map)

            corr_distraction = None
            corr_attention = None
            if not df_corr.empty:
                try:
                    corr_distraction = df_corr[["screen_time_num", "Distraction Rating"]].corr().iloc[0,1]
                    corr_attention = df_corr[["screen_time_num", "Attention Rating"]].corr().iloc[0,1]
                except Exception:
                    pass

            if corr_distraction is not None:
                st.caption(f"Correlation (screen time vs distraction): {corr_distraction:.2f} (positive means more screen time, more distraction)")
            if corr_attention is not None:
                st.caption(f"Correlation (screen time vs attention): {corr_attention:.2f} (negative means more screen time, less attention)")

            # Insight 1: Attention vs Distraction
            attention_distraction_ratio = avg_attention / avg_distraction if avg_distraction > 0 else 0
            if attention_distraction_ratio > 1.2:
                insight1 = "Positive focus balance: Attention rating exceeds distraction rating, indicating good digital wellness."
            elif attention_distraction_ratio > 0.8:
                insight1 = "Moderate focus challenge: Attention and distraction are closely balanced, suggesting room for improvement."
            else:
                insight1 = "Focus challenge: Distraction rating exceeds attention rating, indicating significant digital wellness concerns."
            st.markdown(f'<div class="insight-box">{insight1}</div>', unsafe_allow_html=True)

            # Insight 2: Screen time impact (averages)
            high_screen_time = filtered_df[filtered_df["Screen TIme"] == "9+ hours"]
            if not high_screen_time.empty:
                high_screen_distraction = high_screen_time["Distraction Rating"].mean()
                if high_screen_distraction > 3:
                    insight2 = f"Screen Time Impact: Users with 9+ hours screen time report high distraction ({high_screen_distraction:.1f}/5), suggesting excessive usage affects focus."
                else:
                    insight2 = f"Screen Time Management: Users with 9+ hours screen time manage distraction well ({high_screen_distraction:.1f}/5), indicating effective coping strategies."
                st.markdown(f'<div class="insight-box">{insight2}</div>', unsafe_allow_html=True)

            # Emotional well-being snapshot
            st.subheader("Emotional Well-being Snapshot")
            # Use 'Digital Guilt' and 'Emotional Impact' if available
            guilt_col = "Digital Guilt"
            impact_col = "Emotional Impact"
            if guilt_col in filtered_df.columns:
                guilt_counts = filtered_df[guilt_col].value_counts(dropna=True).to_dict()
                top_guilt = max(guilt_counts, key=guilt_counts.get) if guilt_counts else None
                if top_guilt is not None:
                    st.caption(f"Most common digital guilt frequency: {top_guilt}")
            if impact_col in filtered_df.columns:
                impact_counts = filtered_df[impact_col].value_counts(dropna=True).to_dict()
                top_impact = max(impact_counts, key=impact_counts.get) if impact_counts else None
                if top_impact is not None:
                    st.caption(f"Most cited emotional impacts: {top_impact}")

            # Insight 3: Strategy effectiveness
            strategy_data = filtered_df[["Cleaned Strategies", "Strategy Affectiveness"]].dropna()
            if not strategy_data.empty:
                strategy_data = strategy_data.assign(
                    **{"Cleaned Strategies": strategy_data["Cleaned Strategies"].str.split(", ")}
                ).explode("Cleaned Strategies")
                strategy_data["Cleaned Strategies"] = strategy_data["Cleaned Strategies"].str.strip()
                strategy_effectiveness = strategy_data.groupby("Cleaned Strategies")["Strategy Affectiveness"].mean()
                if not strategy_effectiveness.empty:
                    best_strategy = strategy_effectiveness.idxmax()
                    best_rating = strategy_effectiveness.max()
                    insight3 = f"Best Strategy: '{best_strategy}' is most effective ({best_rating:.1f}/5) for this group."
                    st.markdown(f'<div class="insight-box">{insight3}</div>', unsafe_allow_html=True)
            
            # Recommendations
            st.subheader("Recommendations")
            
            if avg_distraction > 3:
                st.markdown("""
                **For High Distraction Groups:**
                - Implement app timers and screen time limits
                - Try Pomodoro technique for focused work sessions
                - Consider digital detox periods
                - Use Do Not Disturb mode during important tasks
                """)
            
            if avg_attention < 3:
                st.markdown("""
                **For Low Attention Groups:**
                - Practice mindfulness and meditation
                - Create distraction-free work environments
                - Set clear goals and time boundaries
                - Use focus-enhancing tools and techniques
                """)
            
            st.markdown("""
            **General Digital Wellness Tips:**
            - Take regular breaks from screens
            - Set specific times for checking social media
            - Use technology intentionally rather than habitually
            - Balance online and offline activities
            - Monitor and reflect on digital habits regularly
            """)

    # --- Beautiful Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 30px;
            border-radius: 15px;
            margin-top: 40px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        ">
            <h3 style="color: white; margin: 0 0 15px 0;">🎯 Take Action Today</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 0 0 20px 0; font-size: 1.1em;">
                Use these insights to improve your digital wellness and focus habits
            </p>
            <div style="
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            ">
                <div style="
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 10px;
                    min-width: 200px;
                ">
                    <h4 style="color: #74b9ff; margin: 0 0 10px 0;">📱 Set Limits</h4>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9em;">
                        Use app timers and screen time limits
                    </p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 10px;
                    min-width: 200px;
                ">
                    <h4 style="color: #00b894; margin: 0 0 10px 0;">🧘 Practice Mindfulness</h4>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9em;">
                        Take regular breaks and practice focus techniques
                    </p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 10px;
                    min-width: 200px;
                ">
                    <h4 style="color: #fdcb6e; margin: 0 0 10px 0;">⚖️ Find Balance</h4>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9em;">
                        Balance online and offline activities
                    </p>
                </div>
            </div>
            <p style="color: rgba(255,255,255,0.6); margin: 20px 0 0 0; font-size: 0.8em;">
                🧠 Digital Behavior & Focus Dashboard | Built with Streamlit & ❤️
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
