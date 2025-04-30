import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import io

# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

# CSS personalizado para tema moderno y centrado
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Tema moderno */
        body {
            background-color: #f4f7fa;
            color: #1a202c;
            font-family: 'Inter', sans-serif;
        }
        .stApp {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        }
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 20px;
            text-align: center;
        }
        .stButton button {
            background: linear-gradient(90deg, #2b6cb0, #3182ce);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .stSidebar {
            background-color: #edf2f7;
            border-radius: 12px;
            padding: 20px;
        }
        .stSidebar h2, .stSidebar h3, .stSidebar p {
            color: #1a202c;
        }
        .stTextInput input {
            background-color: #f7fafc;
            color: #1a202c;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .stTextInput input:focus {
            border-color: #3182ce;
            box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
        }
        .stMarkdown h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 16px;
        }
        .stMarkdown h2, .stMarkdown h3 {
            color: #1a202c;
        }
        .canvas-container {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        .stSpinner {
            display: flex;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

# Contenedor principal para centrar elementos
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.title('🖌️ Tablero Inteligente')

    # Barra lateral
    with st.sidebar:
        st.subheader("📖 Acerca de:")
        st.write("Dibuja un boceto en el panel y presiona el botón para que una IA lo analice y describa.")
        stroke_width = st.slider('Ancho de línea', 1, 30, 5)

    # Parámetros del lienzo
    drawing_mode = "freedraw"
    stroke_color = "#1a202c"  # Color oscuro para el trazo
    bg_color = "#f7fafc"  # Fondo claro para el lienzo

    # Componente de lienzo con contenedor estilizado
    st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
    canvas_result = st_canvas(
        fill_color="rgba(49, 130, 206, 0.2)",  # Color de relleno suave
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Entrada de clave API
    ke = st.text_input('🔑 Ingresa tu Clave API', type="password")

    # Botón para analizar
    analyze_button = st.button("📊 Analiza la imagen")

    # Lógica de análisis
    if canvas_result.image_data is not None and ke and analyze_button:
        with st.spinner("Analizando ..."):
            try:
                # Inicializar el cliente de OpenAI
                client = OpenAI(api_key=ke)

                # Convertir la imagen del lienzo a PIL
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')

                # Convertir la imagen a base64 directamente desde memoria
                buffered = io.BytesIO()
                input_image.save(buffered, format="PNG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

                # Configurar el prompt para la descripción
                prompt_text = "Describe brevemente la imagen en español."

                # Hacer la solicitud a la API de OpenAI con soporte para imágenes
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                # Mostrar el resultado
                st.success("Análisis completado:")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Error al analizar la imagen: {str(e)}")
    else:
        if not ke and analyze_button:
            st.warning("Por favor ingresa tu API key.")
        if canvas_result.image_data is None and analyze_button:
            st.warning("Por favor dibuja algo en el lienzo antes de analizar.")

    st.markdown('</div>', unsafe_allow_html=True)
