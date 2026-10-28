import streamlit as st
import replicate
import os
import requests
from streamlit_oauth import OAuth2Component

# --- STEP 1: PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Video Style Generator", page_icon="🎬", layout="centered")

# --- STEP 2: CREDENTIALS CONFIGURATION ---
# Apne credentials yahan dalein ya Environment Variables ka use karein
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_://googleusercontent.com"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
REPLICATE_API_TOKEN = "YOUR_REPLICATE_API_TOKEN"

# Replicate API ko configure karein
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

AUTHORIZE_URL = "https://google.com"
TOKEN_URL = "https://googleapis.com"
REVOKE_URL = "https://googleapis.com"

# --- STEP 3: LOGIN SYSTEM (GOOGLE OAUTH) ---
if "auth" not in st.session_state:
    st.session_state.auth = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# OAuth Component Initialize karein
oauth2 = OAuth2Component(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

if st.session_state.auth is None:
    st.title("🎬 Welcome to AI Video Styler")
    st.write("Please login with your Gmail account to start generating videos for free.")
    
    # Login Button
    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://wikimedia.org",
        redirect_uri="http://localhost:8501/",
        scope="openid email profile",
        key="google_auth"
    )
    
    if result:
        st.session_state.auth = result
        # User details fetch karein
        token = result['token']['access_token']
        user_info_resp = requests.get(
            "https://googleapis.com",
            headers={"Authorization": f"Bearer {token}"}
        )
        st.session_state.user_info = user_info_resp.json()
        st.rerun()

# --- STEP 4: MAIN APP (AFTER LOGIN) ---
else:
    user = st.session_state.user_info
    
    # Sidebar with User Info & Logout
    st.sidebar.image(user.get("picture", "https://placeholder.com"), width=80)
    st.sidebar.markdown(f"### Hello, **{user.get('name')}**")
    st.sidebar.caption(user.get("email"))
    
    if st.sidebar.button("Logout", type="primary"):
        st.session_state.auth = None
        st.session_state.user_info = None
        st.rerun()

    # Main Application Interface
    st.title("🎨 AI Video Style Generator")
    st.markdown("Upload your video, select a style, and let the AI transform it!")

    # 1. Video Upload
    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        st.video(uploaded_file)
        
        # Temp file save karna padega Replicate API ko dene ke liye
        with open("temp_input_video.mp4", "wb") as f:
            f.write(uploaded_file.read())

        # 2. Style Selection
        style = st.selectbox(
            "Select Video Style:",
            ["Anime Style", "Cyberpunk / Neon-Glow", "3D Pixar Animation", "Oil Painting / Van Gogh", "Vintage 1930s Cartoon", "Hyper-Realistic Cinematic"]
        )
        
        # Additional Prompt Modification
        custom_prompt = st.text_input("Any extra details? (e.g., 'adding dramatic lightning, heavy rain')", "")

        # 3. Generate Button
        if st.button("🚀 Transform Video Now", type="secondary"):
            with st.spinner("AI is processing your video... This might take a couple of minutes."):
                try:
                    # Final Prompt engineering based on selection
                    final_prompt = f"Transform this video into a {style}. {custom_prompt}"
                    
                    # Replicate API call (Using standard video-to-video / image-to-video model placeholder)
                    # Note: Aap model string ko specific current state models se badal sakte hain
                    output = replicate.run(
                        "cjwbw/videocrafter:029d6674437138540c19e34a61d609e44b8d3bbfbb77f5f616d2111e967a6e9d",
                        input={
                            "video": open("temp_input_video.mp4", "rb"),
                            "prompt": final_prompt,
                            "save_fps": 8
                        }
                    )
                    
                    # Output URL show aur download karna
                    if output:
                        st.success("🎉 Video Generated Successfully!")
                        st.video(output)
                        
                        # Download Button
                        video_bytes = requests.get(output).content
                        st.download_button(
                            label="📥 Download Styled Video",
                            data=video_bytes,
                            file_name="ai_styled_video.mp4",
                            mime="video/mp4"
                        )
                
                except Exception as e:
                    st.error(f"Error generating video: {e}")
                    st.info("Tip: Make sure your Replicate API token is active and valid.")
