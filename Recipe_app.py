# recipe_finder.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import time
import base64

# ===== CORE FUNCTIONALITY =====
def initialize_data():
    """Load initial recipe data with improved structure"""
    if 'recipes' not in st.session_state:
        st.session_state.recipes = pd.DataFrame({
            'Spaghetti Carbonara': ['Italian', ['Pasta', 'Eggs', 'Cheese', 'Bacon'], 20, 'Medium', 4.5],
            'Chicken Tikka Masala': ['Indian', ['Chicken', 'Yogurt', 'Spices', 'Tomato Sauce'], 45, 'Hard', 4.8],
            'Avocado Toast': ['American', ['Bread', 'Avocado', 'Salt', 'Pepper'], 5, 'Easy', 3.7]
        }, index=['Cuisine', 'Ingredients', 'Prep Time', 'Difficulty', 'Rating']).T

# ===== UNIQUE VISUALIZATIONS =====
def create_ingredient_cloud(df):
    """Generate word cloud from ingredients"""
    ingredients = ' '.join([' '.join(items) for items in df['Ingredients']])
    cloud = WordCloud(width=800, height=400, background_color='white').generate(ingredients)
    return cloud.to_image()

def create_time_distribution(df):
    """Interactive prep time histogram"""
    fig, ax = plt.subplots()
    df['Prep Time'].plot(kind='hist', bins=8, ax=ax, color='#00f2ff')
    ax.set_title('⏱️ Cooking Time Distribution')
    return fig

# ===== AI-ENHANCED FEATURES =====
def generate_recipe_card(name, data):
    """Create animated recipe cards"""
    card = f"""
    <div style="padding:15px;margin:10px;background:#fff3e6;border-radius:15px;box-shadow:0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="color:#ff6b6b;">🍳 {name}</h3>
        <p>🌍 <b>Cuisine:</b> {data['Cuisine']}</p>
        <p>⏱️ <b>Prep Time:</b> {data['Prep Time']} mins</p>
        <p>🎚️ <b>Difficulty:</b> {data['Difficulty']}</p>
        <p>⭐ <b>Rating:</b> {data['Rating']}/5</p>
        <details>
            <summary>🛒 Ingredients</summary>
            {', '.join(data['Ingredients'])}
        </details>
    </div>
    """
    return card

# ===== MAIN INTERFACE =====
def main():
    st.set_page_config(
        page_title="✨ Culinary Compass",
        page_icon="🍳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for animations
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    .recipe-card {
        animation: fadeIn 0.5s ease-in;
    }
    </style>
    """, unsafe_allow_html=True)

    initialize_data()

    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/706/706164.png", width=100)
        st.title("Culinary Compass")
        mode = st.radio("Navigation", [
            "🔍 Recipe Explorer", 
            "✨ Smart Search", 
            "🍳 Add Recipe",
            "📊 Food Analytics"
        ])

    # Main Content Areas
    if mode == "🔍 Recipe Explorer":
        handle_recipe_explorer()
    elif mode == "✨ Smart Search":
        handle_smart_search()
    elif mode == "🍳 Add Recipe":
        handle_add_recipe()
    elif mode == "📊 Food Analytics":
        handle_analytics()

# ===== MODE HANDLERS =====
def handle_recipe_explorer():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("🌍 Cuisine Explorer")
        selected_cuisine = st.selectbox(
            "Choose a cuisine:",
            options=sorted(st.session_state.recipes['Cuisine'].unique()),
            index=0
        )
        
        filtered = st.session_state.recipes[
            st.session_state.recipes['Cuisine'] == selected_cuisine
        ]
        
        for name, data in filtered.iterrows():
            st.markdown(generate_recipe_card(name, data), unsafe_allow_html=True)
    
    with col2:
        st.header("📈 Ingredient Cloud")
        st.image(create_ingredient_cloud(st.session_state.recipes))

def handle_smart_search():
    st.header("🔍 Advanced Search")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_time = st.slider("Maximum Prep Time (mins)", 5, 120, 60)
    
    with col2:
        min_rating = st.slider("Minimum Rating", 1.0, 5.0, 3.0)
    
    with col3:
        difficulty = st.multiselect(
            "Difficulty Level",
            options=['Easy', 'Medium', 'Hard'],
            default=['Easy', 'Medium']
        )
    
    filtered = st.session_state.recipes[
        (st.session_state.recipes['Prep Time'] <= max_time) &
        (st.session_state.recipes['Rating'] >= min_rating) &
        (st.session_state.recipes['Difficulty'].isin(difficulty))
    ]
    
    if not filtered.empty:
        st.subheader(f"🍳 Found {len(filtered)} Matching Recipes")
        for name, data in filtered.iterrows():
            st.markdown(generate_recipe_card(name, data), unsafe_allow_html=True)
    else:
        st.warning("No recipes match these criteria. Try adjusting your filters!")

def handle_add_recipe():
    st.header("🍳 Share Your Creation")
    
    with st.form("recipe_form"):
        name = st.text_input("Recipe Name")
        cuisine = st.text_input("Cuisine Type")
        ingredients = st.text_area("Ingredients (comma-separated)")
        prep_time = st.number_input("Prep Time (minutes)", 1, 240)
        difficulty = st.selectbox("Difficulty", ['Easy', 'Medium', 'Hard'])
        rating = st.slider("Rating", 1.0, 5.0, 3.0)
        
        if st.form_submit_button("Submit Recipe"):
            if name and cuisine:
                new_recipe = {
                    'Cuisine': cuisine,
                    'Ingredients': [i.strip() for i in ingredients.split(',')],
                    'Prep Time': prep_time,
                    'Difficulty': difficulty,
                    'Rating': rating
                }
                st.session_state.recipes.loc[name] = new_recipe
                st.success("Recipe added successfully! 🎉")
            else:
                st.error("Please provide at least a recipe name and cuisine type")

def handle_analytics():
    st.header("📊 Culinary Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Distribution", "Timings", "Ingredients"])
    
    with tab1:
        st.pyplot(create_time_distribution(st.session_state.recipes))
    
    with tab2:
        cuisine_counts = st.session_state.recipes['Cuisine'].value_counts()
        st.bar_chart(cuisine_counts)
    
    with tab3:
        st.image(create_ingredient_cloud(st.session_state.recipes))

if __name__ == "__main__":
    main()
