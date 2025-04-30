import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Configuración de la página (debe ser el primer comando de Streamlit)
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

# CSS personalizado para modo oscuro y centrado
st.markdown("""
    <style>
        /* Modo oscuro */
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.5);
        }
        .stButton button {
            background-color: #bb86fc;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #9b59b6;
        }
        .stSidebar {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
        }
        .stSidebar h2, .stSidebar h3, .stSidebar p {
            color: #ffffff;
        }
        .stTextInput input {
            background-color: #333333;
            color: #ffffff; /* Cambiado a blanco */
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 10px;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #ffffff; /* Aseguramos que el título sea blanco */
        }
        /* Centrando todos los elementos */
        .main {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

st.title('🖌️ Tablero Inteligente')

# Barra lateral
with st.sidebar:
    st.subheader("📖 Acerca de:")
    st.write("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto.")
    st.write("Dibuja un boceto en el panel y presiona el botón para analizarlo.")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

# Parámetros del lienzo
drawing_mode = "freedraw"
stroke_color = "#FFFFFF"  # Blanco para modo oscuro
bg_color = "#333333"  # Gris oscuro para el fondo del lienzo

# Componente de lienzo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color de relleno con opacidad
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Entrada de clave API
ke = st.text_input('🔑 Ingresa tu Clave API', type="password")
os.environ['OPENAI_API_KEY'] = ke

# Botón para analizar
analyze_button = st.button("📊 Analiza la imagen")

# Lógica de análisis
if canvas_result.image_data is not None and ke and analyze_button:
    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = base64.b64encode(open("img.png", "rb").read()).decode("utf-8")
        prompt_text = "Describe in Spanish briefly the image."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt_text},
                ],
                max_tokens=500,
            )
            st.success("Análisis completado:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
else:
    if not ke:
        st.warning("Por favor ingresa tu API key.")
