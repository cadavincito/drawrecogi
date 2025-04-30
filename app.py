import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import io

# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente', layout="wide", page_icon="🎨")

# CSS personalizado - Tema Moderno Mejorado
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Tema principal */
        body {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Poppins', sans-serif;
        }
        .stApp {
            background-color: #1e293b;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
            margin: 1rem auto;
            max-width: 1200px;
        }
        
        /* Encabezados */
        .stMarkdown h1 {
            color: white !important;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Textos específicos en blanco */
        .stTextInput label p {
            color: white !important;
        }
        .stCaption {
            color: white !important;
        }
        
        /* Botones */
        .stButton button {
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
            background: linear-gradient(135deg, #6366f1, #3b82f6);
        }
        
        /* Barra lateral */
        .stSidebar {
            background: linear-gradient(180deg, #1e293b, #0f172a);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        .stSidebar h2 {
            color: #7dd3fc;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #334155;
            padding-bottom: 0.5rem;
        }
        .stSidebar p {
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* Campos de entrada */
        .stTextInput input {
            background-color: #334155;
            color: #f8fafc;
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 1rem;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        .stTextInput input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
            outline: none;
        }
        
        /* Lienzo de dibujo */
        .canvas-container {
            border: 2px solid #475569;
            border-radius: 16px;
            padding: 1rem;
            background-color: #334155;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            margin: 1.5rem 0;
            display: flex;
            justify-content: center;
        }
        
        /* Slider */
        .stSlider {
            margin: 1.5rem 0;
        }
        .stSlider .st-ae {
            color: #3b82f6 !important;
        }
        .stSlider .st-af {
            background-color: #3b82f6 !important;
        }
        
        /* Mensajes */
        .stSuccess {
            background-color: #10b981 !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-top: 1rem !important;
        }
        .stWarning, .stError {
            border-radius: 12px !important;
            padding: 1rem !important;
        }
        
        /* Spinner */
        .stSpinner {
            color: #3b82f6 !important;
        }
        .stSpinner div {
            border-color: #3b82f6 transparent transparent transparent !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title('🎨 Tablero Inteligente')

# Barra lateral
with st.sidebar:
    st.subheader("📖 Acerca de")
    st.write("Esta aplicación utiliza inteligencia artificial para interpretar tus dibujos. Dibuja algo en el panel y presiona el botón para analizarlo.")
    st.write("La IA describirá lo que reconoce en tu boceto.")
    
    stroke_width = st.slider('Ancho del pincel', 1, 30, 5, help="Ajusta el grosor del trazo al dibujar")
    
    st.markdown("---")
    st.markdown("**Configuración avanzada**")
    drawing_mode = st.selectbox(
        "Modo de dibujo",
        ("freedraw", "line", "rect", "circle", "transform"),
        index=0,
        help="Selecciona el tipo de herramienta de dibujo"
    )
    stroke_color = st.color_picker("Color del pincel", "#FFFFFF")

# Parámetros del lienzo
bg_color = "#334155"  # Color de fondo del lienzo

# Componente de lienzo con contenedor estilizado
st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
canvas_result = st_canvas(
    fill_color="rgba(59, 130, 246, 0.3)",  # Color de relleno azul suave
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=400,
    width=600,
    drawing_mode=drawing_mode,
    key="canvas",
    update_streamlit=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# Sección principal
col1, col2 = st.columns([3, 1])

with col1:
    # Entrada de clave API
    api_key = st.text_input('🔑 Ingresa tu Clave API de OpenAI', type="password", 
                          help="Necesitas una clave API válida de OpenAI para usar esta función")

with col2:
    # Botón para analizar
    analyze_button = st.button("✨ Analizar Dibujo", use_container_width=True)

# Lógica de análisis
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando tu dibujo..."):
        try:
            # Inicializar el cliente de OpenAI
            client = OpenAI(api_key=api_key)

            # Convertir la imagen del lienzo a PIL
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')

            # Convertir la imagen a base64
            buffered = io.BytesIO()
            input_image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Configurar el prompt para la descripción
            prompt_text = "Describe en detalle lo que aparece en este dibujo. Sé específico sobre los elementos reconocibles, formas y cualquier objeto que puedas identificar. Responde en español con un lenguaje natural."

            # Hacer la solicitud a la API de OpenAI
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
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
            st.success("**Análisis completado:**")
            st.markdown(f"```\n{response.choices[0].message.content}\n```")
            
            # Sugerencia para continuar
            st.info("💡 ¿Quieres intentar con otro dibujo? Borra el lienzo y dibuja algo nuevo.")

        except Exception as e:
            st.error(f"❌ Error al analizar la imagen: {str(e)}")
            st.warning("Por favor verifica tu clave API e intenta nuevamente.")
else:
    if not api_key and analyze_button:
        st.warning("⚠️ Por favor ingresa tu API key de OpenAI")
    if canvas_result.image_data is None and analyze_button:
        st.warning("🖌️ Por favor dibuja algo en el lienzo antes de analizar")

# Pie de página
st.markdown("---")
st.caption("Aplicación desarrollada con Streamlit y OpenAI GPT-4 Vision | © 2023 Tablero Inteligente")
