from craiyon import Craiyon
import streamlit as st
from PIL import Image
from PIL import ImageDraw, ImageFont
import requests
from io import BytesIO
import time
import os
import base64
import requests
 
# Instantiate Craiyon API wrapper
generator = Craiyon()
 
st.set_page_config(page_title="Apparel Design Generator", page_icon="🧥", layout="wide")
 
# Custom CSS for the page styling
st.markdown(
    """
    <style>
        .banner {
            background-color: #641975;  /* Violet */
            padding: 20px;
            text-align: center;
            border-radius: 10px;
        }
        .banner h1 {
            color: white;
            font-size: 36px;
        }
        .banner p {
            color: white;
            font-size: 18px;
        }
        .button-style {
            background-color: #8A2BE2; /* Violet */
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
        }
        .button-style:hover {
            background-color: #6A1FA3; /* Darker violet */
        }
        .input-label {
            font-size: 24px;
            font-weight: bold;
            color: #641975;  /* Violet */
        }
        .stTextInput>div>input {
            font-size: 20px;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #641975;
        }
    </style>
    """, unsafe_allow_html=True
)
 
# HTML structure for the landing page without the Get Started button
st.markdown(
    """
    <div class="banner">
        <h1>👕 Welcome to the AI-Powered Apparel Design Generator 🎨</h1>
        <p>🌟 Create your own custom apparel designs with the power of AI! 🤖✨</p>
    </div>
    """, unsafe_allow_html=True
)
 
# Sidebar navigation
option = st.sidebar.radio("🛠️ Select Section", ("Generate Images", "Customize T-Shirt"))
 
# Session state
if "images" not in st.session_state:
    st.session_state.images = []
    st.session_state.image_objects = []
    st.session_state.edited_images = {}
    st.session_state.selected_image_idx = None
 
if "design_size" not in st.session_state:
    st.session_state.design_size = 0.5
 
if "cached_design" not in st.session_state:
    st.session_state.cached_design = {}
 
if "x_offset" not in st.session_state:
    st.session_state.x_offset = 0
 
if "y_offset" not in st.session_state:
    st.session_state.y_offset = 0
 
@st.cache_data
def fetch_and_resize_image(url, width, height):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception for non-200 status codes
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)  # Updated for newer versions of Pillow
        return resized_img
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching image: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing the image: {e}")
        return None
 
# T-shirt options and images
tshirt_images = {
    "White": "images/white_tshirt.png",
    "Black": "images/black_tshirt.png",
    "Red": "images/red_tshirt.png",
    "Blue": "images/blue_tshirt.png"
}
 
# Generate Images Section
if option == "Generate Images":
    # User Prompt
    st.write("###")
    st.markdown('<div class="input-label">🖌️ Enter a design prompt (e.g., "Floral pattern, abstract art"): </div>', unsafe_allow_html=True)
    prompt = st.text_input("Enter Prompt")
 
    # Generate Images
    if st.button("🎨 Generate Images"):
        start_time = time.time()
        with st.spinner("🌀 Generating Images... Please wait."):
            result = generator.generate(prompt)
        end_time = time.time()
        st.success(f"✅ Images generated in {end_time - start_time:.2f} seconds!")
 
        st.session_state.images = result.images[:4]
        st.session_state.image_objects = []
        st.session_state.edited_images = {}
        st.session_state.selected_image_idx = None
 
        # Fetch and store images
        for img_url in st.session_state.images:
            response = requests.get(img_url)
            if response.status_code == 200:
                try:
                    img = Image.open(BytesIO(response.content))
                    st.session_state.image_objects.append(img)
                except Exception as e:
                    st.error(f"Failed to open image from URL: {img_url}. Error: {e}")
            else:
                st.error(f"Failed to retrieve image from URL: {img_url}. Status code: {response.status_code}")
 
    # Display images
    if st.session_state.image_objects:
        st.write("### Generated Images:")
        cols = st.columns(4, gap="large")
 
        for idx, img in enumerate(st.session_state.image_objects):
            col = cols[idx % 4]
            with col:
                st.image(img, use_container_width=True)
                if st.button(f"✨ Select Image {idx + 1}", key=f"select_{idx}"):
                    st.session_state.selected_image_idx = idx
 
# Customize T-Shirt Section
elif option == "Customize T-Shirt":
    if st.session_state.selected_image_idx is not None:
        left_col, right_col = st.columns(2, gap="large")
    
        with left_col:
            st.write("###")
            st.write("## 🧵 Customize T-Shirt 👕")
    
            # Overlay the selected design on the T-shirt
            t_shirt_base = None  # Initialize t_shirt_base to avoid undefined errors
            if st.session_state.selected_image_idx is not None:
                try:
                    tshirt_options = list(tshirt_images.keys())
                    with st.expander("🎨 Select T-Shirt Colour:"):
                        selection = st.selectbox(label="Select:", options=tshirt_options)
                        tshirt_image_path = tshirt_images.get(selection)
                    t_shirt_base = Image.open(tshirt_image_path)  # Load the selected T-shirt image
                except Exception as e:
                    st.error(f"Failed to load the T-shirt image: {e}")
                    t_shirt_base = None
    
                if t_shirt_base:
                    selected_img_url = st.session_state.images[st.session_state.selected_image_idx]
    
                    # Size options for the design
                    size_options = {
                        "Small": 0.2,
                        "Medium": 0.35,
                        "Large": 0.45
                    }
    
                    with st.expander("⚙️ Adjust Image: "):
                        selected_size = st.radio("🔧 Select Design Size:", options=list(size_options.keys()), index=2)
                        st.session_state.design_size = size_options[selected_size]
    
                        design_width = int(t_shirt_base.width * st.session_state.design_size)
                        design_height = int(t_shirt_base.height * st.session_state.design_size)
    
                        cache_key = f"{selected_img_url}_{design_width}_{design_height}"
                        if cache_key not in st.session_state.cached_design:
                            design_image_resized = fetch_and_resize_image(selected_img_url, design_width, design_height)
                            if design_image_resized:
                                st.session_state.cached_design[cache_key] = design_image_resized
                        else:
                            design_image_resized = st.session_state.cached_design[cache_key]
    
                        if design_image_resized:
                            x_offset = (t_shirt_base.width - design_image_resized.width) // 2
                            y_offset = (t_shirt_base.height - design_image_resized.height) // 2
    
                            # Shape selection
                            shape = st.selectbox("🔲 Select Image Shape:", ["Square", "Circle"])
    
                            if shape == "Circle":
                                mask = Image.new("L", design_image_resized.size, 0)
                                draw = ImageDraw.Draw(mask)
                                draw.ellipse((0, 0, design_image_resized.width, design_image_resized.height), fill=255)
                                design_image_resized.putalpha(mask)
                            elif shape == "Square":
                                mask = Image.new("L", design_image_resized.size, 255)  # Full opacity mask
                                design_image_resized.putalpha(mask)
    
                            # Apply offsets to design placement
                            x_offset += st.session_state.x_offset
                            y_offset += st.session_state.y_offset
    
                            # Overlay the design
                            t_shirt_base.paste(
                                design_image_resized,
                                (x_offset, y_offset),
                                design_image_resized.convert("RGBA").split()[3]  # Alpha channel for transparency
                            )
    
                        # Display shift buttons
                        st.write("🔁 Shift Design:")
                        col3, col4 = st.columns(2)
    
                        with col3:
                            if st.button("⬅️ Shift Left"):
                                st.session_state.x_offset -= 10  # Move 10px to the left
                            if st.button("➡️ Shift Right"):
                                st.session_state.x_offset += 10  # Move 10px to the right
    
                        with col4:
                            if st.button("⬆️ Shift Up"):
                                st.session_state.y_offset -= 10  # Move 10px upwards
                            if st.button("⬇️ Shift Down"):
                                st.session_state.y_offset += 10  # Move 10px downwards
    
                    with st.expander("📝 Add Text Customization"):
                        user_text = st.text_input(label="Enter Text:")
                
                        if user_text:
                            # Font options
                            font_options = {
                                "Lato" : "fonts/Lato-Black.ttf",
                                "Roboto" : "fonts/Roboto-Black.ttf",
                                "Arizonia" : "fonts/Arizonia-Regular.ttf",
                                "BungeeShade" : "fonts/BungeeShade-Regular.ttf"
                            }
                            font_choice = st.selectbox("Select Font:", options=list(font_options.keys()), index=0)
                            
                            font_size = st.slider("Font Size", min_value=10, max_value=50, value=30)
                            text_color = st.color_picker("Select Text Color:", value="#000000")  # Default black
                            text_position_y = st.slider("Y Position", min_value=0, max_value= 400, value=t_shirt_base.height // 2)


                            if user_text:
                                draw = ImageDraw.Draw(t_shirt_base)
                                try:
                                    font = ImageFont.truetype(font_options[font_choice], font_size)
                                except IOError:
                                    font = ImageFont.load_default()  # Fallback to default font

                                # Calculate text dimensions
                                text_bbox = draw.textbbox((0, 0), user_text, font=font)
                                text_width = text_bbox[2] - text_bbox[0]
                                text_height = text_bbox[3] - text_bbox[1]

                                # Center text horizontally
                                text_position_x = (t_shirt_base.width - text_width) // 2
                                text_position = (text_position_x, text_position_y - text_height // 2)

                                # Draw text on the image
                                draw.text(text_position, user_text, fill=text_color, font=font)

    
        # Display final T-shirt
        with right_col:
            st.write("###")
            st.write("###")
            st.write("###")
            st.image(t_shirt_base, caption="🎉 Your Custom T-Shirt", use_container_width=True)
    
    else:
        st.write("###")
        st.warning("Please select an image to customize the T-Shirt")
    