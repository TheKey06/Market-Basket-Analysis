import streamlit as st

# para las cartas

def card_preview(titulo, descripcion, icono, pagina):
    st.markdown(f"""
    <div style="
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background: #f9f9f9;
        transition: transform 0.2s;
        cursor: pointer;
    ">
        <h1>{icono}</h1>
        <h3>{titulo}</h3>
        <p style="color: gray;">{descripcion}</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link(pagina, label=f"Ir a {titulo} →")

