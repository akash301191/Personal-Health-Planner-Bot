import json
import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def display_dietary_plan(plan: dict) -> None:
    """
    Display the dietary plan in an expander with two columns:
      - Column 1: Meal Plan
      - Column 2: Nutritional Breakdown, Rationale, Meal Preparation Tips, and Important Considerations.
    
    Expects the plan to be a dictionary with the following keys:
      - meal_plan: A markdown-formatted string for the detailed meal plan.
      - nutritional_breakdown: A markdown-formatted string summarizing key nutritional metrics.
      - rationale: A markdown-formatted string explaining why the plan supports the user's goals.
      - meal_preparation_tips: A markdown-formatted string with practical meal prep tips.
      - important_considerations: A markdown-formatted string listing additional dietary tips.
    """
    with st.expander("📋 Your Personalized Dietary Plan", expanded=True):
        col1, col2 = st.columns(2)
        
        # Column 1: Meal Plan
        with col1:
            st.markdown("## Meal Plan")
            st.markdown(plan.get("meal_plan", "Meal plan not available"))


        # Column 2: Other sections
        with col2:
            st.markdown("## Meal Preparation Tips")
            st.markdown(plan.get("meal_preparation_tips", "Meal preparation tips not provided"))
            st.markdown("## Nutritional Breakdown")
            st.markdown(plan.get("nutritional_breakdown", "Nutritional breakdown not available"))
            st.markdown("## Rationale")
            st.markdown(plan.get("rationale", "Rationale not provided"))
            st.markdown("## Important Considerations")
            st.markdown(plan.get("important_considerations", "Important considerations not provided"))


def display_fitness_plan(plan: dict) -> None:
    """
    Display the fitness plan in an expander with a visually appealing layout.
    The layout includes:
      - Three columns for Warm-up, Main Workout, and Cool-down.
      - Full-width sections for Benefits and Safety Guidelines.
    
    Expects the plan to be a dictionary with the following keys:
      - warmup: Plain string with the warm-up routine.
      - main_workout: Plain string with the main workout details.
      - cooldown: Plain string with the cool-down routine.
      - benefits: Plain string explaining the benefits of the plan.
      - safety_guidelines: Plain string with essential safety tips.
    """
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        # Create three columns for the workout phases.
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("## Warm-up")
            st.markdown(plan.get("warmup", "Warm-up routine not available."))
        with col2:
            st.markdown("## Main Workout")
            st.markdown(plan.get("main_workout", "Main workout details not available."))
        with col3:
            st.markdown("## Cool-down")
            st.markdown(plan.get("cooldown", "Cool-down routine not available."))
        
        # Display Benefits and Safety Guidelines spanning the full width.
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("## Benefits")
            st.markdown(plan.get("benefits", "Benefits not provided."))
        with col2:
            st.markdown("## Safety Guidelines")
            st.markdown(plan.get("safety_guidelines", "Safety guidelines not provided."))

def extract_json_from_string(text: str) -> dict:
    # Split the text into lines
    lines = text.splitlines()
    # Filter out lines that start with the code fence (``` or ```json)
    json_lines = [line for line in lines if not line.strip().startswith("```")]
    # Join the remaining lines back into a single string
    json_str = "\n".join(json_lines)
    # Parse the JSON string into a dictionary
    return json.loads(json_str)

def initialize_openai_model():
    try:
        api_key = st.session_state.openai_api_key
        return OpenAIChat(id='gpt-4o', api_key=api_key)
    except Exception as e:
        st.error(f"❌ Error initializing OpenAI Model: {e}")
        return None

def generate_dietary_plan(openai_model, user_profile: str) -> dict:
    dietary_agent = Agent(
        name="Dietary Expert",
        role="Provides personalized dietary recommendations",
        model=openai_model,
        instructions = [
            "Consider the user's profile, including any dietary restrictions and preferences.",
            "Generate a detailed daily meal plan that includes exactly one section for each meal: Breakfast, Lunch, Snacks, and Dinner, each with portion recommendations.",
            "Within the 'meal_plan' value, format the meal headings (Breakfast, Lunch, Snacks, Dinner) using markdown, for example '### Breakfast'.",
            "Include a section for Nutritional Breakdown summarizing key nutritional metrics (e.g., total calories, protein, carbohydrates, fats) as a bulleted list. For instance:\n- Total Calories: 2500 kcal\n- Protein: 150g\n- Carbohydrates: 300g\n- Fats: 100g",
            "Include a section for Rationale explaining why the plan supports the user's health and fitness goals.",
            "Include a section for Meal Preparation Tips with practical advice for prepping and cooking the meals.",
            "Include a section for Important Considerations listing additional tips (e.g., hydration, fiber intake, electrolyte balance).",
            "Return your response as a valid JSON object with the keys: 'meal_plan', 'nutritional_breakdown', 'rationale', 'meal_preparation_tips', and 'important_considerations'.",
            "Each value must be a plain string (single-depth) that can include multiple lines and markdown formatting, with no nested objects.",
            "Ensure that there is exactly ONE section for each meal (Breakfast, Lunch, Snacks, and Dinner) in the 'meal_plan' value, and avoid repeating any section headings."
        ]
    )

    response = dietary_agent.run(user_profile)
    try:
        plan = extract_json_from_string(response.content)
    except Exception as e:
        st.error(f"Failed to parse JSON response: {e}")
        plan = {
            "meal_plan": "Plan not available",
            "nutritional_breakdown": "Not available",
            "rationale": "Not provided",
            "meal_preparation_tips": "Not provided",
            "important_considerations": "Not provided"
        }
    return plan

def generate_fitness_plan(openai_model, user_profile: str) -> dict:
    """
    Generate a personalized fitness plan based on the user's profile.
    
    The agent is instructed to return a valid JSON object with the following keys:
      - warmup: A recommended warm-up routine.
      - main_workout: A detailed main workout routine.
      - cooldown: A cool-down routine with stretching or relaxation exercises.
      - benefits: A brief explanation of how this workout supports the user's fitness goals.
      - safety_guidelines: Essential safety tips and any suggested modifications.
    
    Each value should be a plain string that may include markdown formatting and multiple lines.
    """
    fitness_agent = Agent(
        name="Fitness Expert",
        role="Provides personalized fitness recommendations",
        model=openai_model,
        instructions=[
            "Consider the user's profile, including their fitness goals, current activity level, and personal preferences.",
            "Generate a comprehensive fitness plan that covers warm-up, main workout, cool-down, benefits, and safety guidelines. Do NOT include headings like 'Warm-up:', 'Main Workout:', 'Cool-down:', 'Benefits:', or 'Safety Guidelines:' in the text itself. Instead, just provide the text for each section.",
            "Include a section for Warm-up that provides a brief routine with dynamic stretches or light exercises to prepare the body.",
            "Include a section for Main Workout that details specific exercises along with recommended sets, repetitions, or durations.",
            "Include a section for Cool-down that describes static stretches or relaxation exercises to aid recovery.",
            "Include a section for Benefits that explains how this workout plan supports the user's fitness goals.",
            "Include a section for Safety Guidelines that lists essential tips and modifications to ensure a safe and effective workout.",
            "Return your response as a valid JSON object with the keys: 'warmup', 'main_workout', 'cooldown', 'benefits', and 'safety_guidelines'.",
            "Each value must be a plain string (single-depth) that can include multiple lines and markdown formatting, with no nested objects."
        ]
    )

    response = fitness_agent.run(user_profile)
    try:
        plan = extract_json_from_string(response.content)
    except Exception as e:
        st.error(f"Failed to parse JSON response: {e}")
        plan = {
            "warmup": "Not available",
            "main_workout": "Not available",
            "cooldown": "Not available",
            "benefits": "Not provided",
            "safety_guidelines": "Not provided"
        }
    return plan

def render_profile() -> str:
    st.header("👤 Your Profile")
    # Create three columns for different groups of fields.
    col1, col2, col3 = st.columns(3)

    # Column 1: Basic Info
    with col1:
        st.subheader("Basic Info")
        age = st.number_input("Age", min_value=10, max_value=100, step=1, help="Enter your age")
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1, help="Enter your height in centimeters")
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1, help="Enter your weight in kilograms")
        sex = st.selectbox("Sex", options=["Male", "Female", "Other"])

    # Column 2: Lifestyle & Goals
    with col2:
        st.subheader("Lifestyle & Goals")
        sleep_quality = st.selectbox("Sleep Quality", options=["Poor", "Average", "Good"], help="How would you rate your typical sleep quality?")
        stress_level = st.selectbox("Stress Level", options=["Low", "Moderate", "High"], help="How would you rate your current stress level?")      
        fitness_goals = st.selectbox(
            "Fitness Goals",
            options=["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"],
            help="What do you want to achieve"
        )
        dietary_preferences = st.selectbox(
            "Dietary Preferences",
            options=["Vegetarian", "Keto", "Gluten Free", "Low Carb", "Dairy Free", "Omnivore"],
            help="Select your dietary preference"
        )

    # Column 3: Additional Details
    with col3:
        st.subheader("Additional Details")

        activity_level = st.selectbox(
            "Activity Level", 
            options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
            help="Choose your typical activity level"
        )
        medical_conditions = st.text_area("Medical Conditions (optional)", placeholder="e.g., asthma, allergies")
        food_allergies = st.text_area("Food Allergies (optional)", placeholder="List any food allergies")

    # Construct a profile summary string to display
    profile = f"""
        **Basic Info:**
        - Age: {age}
        - Height: {height} cm
        - Weight: {weight} kg

        **Lifestyle & Goals:**
        - Sex: {sex}
        - Activity Level: {activity_level}
        - Fitness Goals: {fitness_goals}
        - Dietary Preferences: {dietary_preferences}

        **Additional Details:**
        - Sleep Quality: {sleep_quality}
        - Stress Level: {stress_level}
        - Medical Conditions: {medical_conditions if medical_conditions.strip() else 'None'}
        - Food Allergies: {food_allergies if food_allergies.strip() else 'None'}
    """

    return profile



def main() -> None:
    st.set_page_config(page_title="Personal Health Planner Bot", page_icon="🏋️‍♂️", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='font-size: 2.5rem;'>🏋️‍♂️ Personal Health Planner Bot</h1>", unsafe_allow_html=True)
    st.markdown(
        "Welcome to Personal Health Planner Bot — an innovative Streamlit application that leverages your personal health metrics to deliver customized nutrition and exercise plans designed to help you achieve your wellness objectives.",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        /* Center and adjust the width of all text inputs */
        div[data-testid="stTextInput"] {
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Get the OpenAI API key
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Don't have an API key? Get one [here](https://platform.openai.com/account/api-keys)."
    )
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.success("✅ API key updated!")

    user_profile = render_profile()

    # If plans are already generated, display them regardless of the button click.
    if "dietary_plan" in st.session_state and "fitness_plan" in st.session_state:
        display_dietary_plan(st.session_state.dietary_plan)
        display_fitness_plan(st.session_state.fitness_plan)

    if st.button("🎯 Generate My Personalized Health Plan", use_container_width=True):
        if not hasattr(st.session_state, "openai_api_key"):
            st.error("Please provide openai_api_key")
        else:
            openai_model = initialize_openai_model()
            with st.spinner("Creating your customized Health Plan ..."):
                try:
                    # Generate dietary plan using dietary agent.
                    dietary_plan = generate_dietary_plan(openai_model, user_profile)
                    st.session_state.dietary_plan = dietary_plan
                    display_dietary_plan(dietary_plan)
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

            with st.spinner("Creating your customized Fitness Plan ..."):
                try:
                    # Generate fitness plan using fitness agent.
                    fitness_plan = generate_fitness_plan(openai_model, user_profile)
                    st.session_state.fitness_plan = fitness_plan
                    display_fitness_plan(fitness_plan)
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

            st.session_state.plans_generated = True
            st.session_state.qa_pairs = []

            # Disclaimer about seeking a second opinion
            st.markdown("""
            **Disclaimer:** The health and fitness plans provided by this application are generated by an AI model and are intended for informational purposes only. For a comprehensive evaluation and personalized advice, please consult a certified health or fitness expert.
            """)

            # Combine recommendations into a single text block.
            combined_recommendations = (
                "### Dietary Plan\n" +
                "**Meal Plan:**\n" + st.session_state.dietary_plan.get("meal_plan", "Plan not available") + "\n\n" +
                "**Nutritional Breakdown:**\n" + st.session_state.dietary_plan.get("nutritional_breakdown", "Not available") + "\n\n" +
                "**Rationale:**\n" + st.session_state.dietary_plan.get("rationale", "Not provided") + "\n\n" +
                "**Meal Preparation Tips:**\n" + st.session_state.dietary_plan.get("meal_preparation_tips", "Not provided") + "\n\n" +
                "**Important Considerations:**\n" + st.session_state.dietary_plan.get("important_considerations", "Not provided") + "\n\n" +
                "### Fitness Plan\n" +
                "**Warm-up:**\n" + st.session_state.fitness_plan.get("warmup", "Not available") + "\n\n" +
                "**Main Workout:**\n" + st.session_state.fitness_plan.get("main_workout", "Not available") + "\n\n" +
                "**Cool-down:**\n" + st.session_state.fitness_plan.get("cooldown", "Not available") + "\n\n" +
                "**Benefits:**\n" + st.session_state.fitness_plan.get("benefits", "Not provided") + "\n\n" +
                "**Safety Guidelines:**\n" + st.session_state.fitness_plan.get("safety_guidelines", "Not provided")
            )

            st.download_button(
                "💾 Download Recommendations",
                data=combined_recommendations,
                file_name="personal_health_plan.txt",
                mime="text/plain"
            )


if __name__ == "__main__":
    main()