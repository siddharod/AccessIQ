import os
import datetime
import pandas as pd
import streamlit as st

# ─── Load .env using absolute path relative to this file ────────────────────
# This ensures dotenv works regardless of what cwd Streamlit was launched from.
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    _env_path = os.path.normpath(_env_path)
    load_dotenv(dotenv_path=_env_path, override=False)
except Exception:
    pass  # dotenv is optional; keys may come from OS environment

@st.cache_data
def load_dataset():
    """Load cleaned/engineered accessibility dataset."""
    # Resolve paths relative to this file so Streamlit launch directory doesn't matter
    _base = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(_base, "..", "data", "engineered_accessibility_dataset.csv"),
        os.path.join(_base, "..", "data", "cleaned_accessibility_dataset.csv"),
        os.path.join(_base, "..", "data", "smart_accessibility_analytics_dataset.csv"),
        "data/engineered_accessibility_dataset.csv",
        "data/cleaned_accessibility_dataset.csv",
        "data/smart_accessibility_analytics_dataset.csv",
    ]
    for p in possible_paths:
        p = os.path.normpath(p)
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                df[numeric_cols] = df[numeric_cols].fillna(0)
                return df
            except Exception:
                continue
    return pd.DataFrame()

def inject_custom_css():
    """Inject CSS based on current theme."""
    theme = st.session_state.get("theme", "dark")
    _base = os.path.dirname(os.path.abspath(__file__))
    css_file = os.path.normpath(os.path.join(_base, "..", "assests", "css", f"{theme}.css"))
    if not os.path.exists(css_file):
        css_file = f"assests/css/{theme}.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .kpi-card { background: #1e293b; color: white; padding: 1rem; border-radius: 12px; }
        .glass-card { background: rgba(30,41,59,0.7); padding: 1rem; border-radius: 12px; }
        </style>
        """, unsafe_allow_html=True)

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    if "selected_persona" not in st.session_state:
        st.session_state["selected_persona"] = "Wheelchair User"
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "chatbot_open" not in st.session_state:
        st.session_state["chatbot_open"] = False
    if "chatbot_messages" not in st.session_state:
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["chatbot_messages"] = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm **AccessIQ AI Assistant**. Ask me anything about urban accessibility standards, RPWD/ADA guidelines, platform predictions, or smart city recommendations!",
                "time": now_str
            }
        ]

PERSONAS = {
    "Wheelchair User": {
        "icon": "♿",
        "weights": {
            "Ramp_Available": 3.0,
            "Elevator_Available": 2.5,
            "Wheelchair_Entrance": 3.0,
            "Door_Width_cm": 2.0,
            "Accessible_Washroom": 2.5,
            "Tactile_Path": 0.5,
            "Reserved_Parking": 2.0,
            "Safety_Level": 1.0
        },
        "description": "Requires step-free access, wide doors, ramps, elevators, and accessible washrooms."
    },
    "Senior Citizen": {
        "icon": "👴",
        "weights": {
            "Elevator_Available": 2.5,
            "Ramp_Available": 2.0,
            "Lighting": 2.0,
            "Safety_Level": 2.5,
            "Average_Waiting_Time": -2.0,
            "Crowd_Level": -2.0,
            "Reserved_Parking": 2.0
        },
        "description": "Requires safe footing, low waiting times, elevators, good lighting, and calm environments."
    },
    "Visually Impaired": {
        "icon": "👨‍🦯",
        "weights": {
            "Braille_Signage": 3.5,
            "Audio_Announcements": 3.5,
            "Tactile_Path": 3.5,
            "Lighting": 2.0,
            "Staff_Trained_Accessibility": 2.0
        },
        "description": "Requires tactile paving, audio assistance, Braille signage, and trained supportive staff."
    },
    "Hearing Impaired": {
        "icon": "🧏",
        "weights": {
            "Multilingual_Signage": 3.0,
            "Lighting": 2.5,
            "CCTV_Available": 2.0,
            "Staff_Trained_Accessibility": 2.5
        },
        "description": "Requires clear visual signage, bright lighting, and trained staff proficient in gestures/sign."
    },
    "Pregnant Woman": {
        "icon": "🤰",
        "weights": {
            "Elevator_Available": 2.5,
            "Accessible_Washroom": 2.5,
            "Reserved_Parking": 2.0,
            "Average_Waiting_Time": -2.5,
            "Crowd_Level": -2.0,
            "Public_Transport_Nearby": 2.0
        },
        "description": "Needs resting areas, short queues, clean washrooms, elevator access, and nearby transport."
    },
    "Parent with Stroller": {
        "icon": "👶",
        "weights": {
            "Ramp_Available": 2.5,
            "Elevator_Available": 2.5,
            "Door_Width_cm": 2.0,
            "Accessible_Washroom": 2.0,
            "Parking_Available": 2.0
        },
        "description": "Requires step-free stroller pathways, spacious doorways, and accessible family facilities."
    },
    "Normal User": {
        "icon": "🚶",
        "weights": {
            "Safety_Level": 1.5,
            "User_Rating": 2.0,
            "Public_Transport_Nearby": 1.5,
            "Parking_Available": 1.5,
            "Crowd_Level": -1.0
        },
        "description": "General accessibility focusing on safety, convenience, rating, and public transit."
    }
}
