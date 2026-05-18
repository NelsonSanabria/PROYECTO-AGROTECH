"""
AgroTech Analytics - Sistema de Gestión y Fertilización de Precisión.

Este módulo despliega una aplicación web interactiva utilizando Streamlit.
Se conecta a una base de datos relacional MySQL para leer, registrar, actualizar
y eliminar información sobre el inventario de árboles frutales y análisis de suelos,
calculando de forma automática los requerimientos óptimos de Nitrógeno y Potasio.

Autor: Nelson Enrique Sanabria Díaz
Fecha: Mayo 2026
Versión: 1.1
"""
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración global de la aplicación web
st.set_page_config(page_title="AgroTech Analytics", page_icon="🌱", layout="wide")

st.title("🌱 Sistema de Analítica Agrícola y Gestión de Precisión")
st.markdown("Panel de control conectado en tiempo real con **MySQL**.")

# =================================================================
# 1. FUNCIÓN DE CONEXIÓN A MYSQL
# =================================================================
def obtener_conexion():
    """
    Establece una conexión activa con el servidor local de MySQL.

    Utiliza las credenciales del sistema para acceder a la base de datos
    'agrotech_analytics' encargada de la persistencia del inventario.

    Returns:
        mysql.connector.connection_cext.CMySQLConnection: Objeto de conexión a la BD.
    
    Raises:
        mysql.connector.Error: Si las credenciales son incorrectas o el servidor está apagado.
    """
# ... resto del código
    return mysql.connector.connect(
        host='localhost',
        user='root',          
        password='Nesd123*/',  # ⚠️ REEMPLAZA CON TU CONTRASEÑA REAL
        database='agrotech_analytics'
    )

# =================================================================
# 2. REGLA LÓGICA DE FERTILIZACIÓN (INCLUYE PLÁTANO Y GUANÁBANA)
# =================================================================
def calcular_dosis_individual(row):
    """
    Calcula la demanda nutricional teórica (N y K) por árbol individual de forma anual.

    Aplica reglas de negocio personalizadas según la especie del cultivo y su 
    etapa de desarrollo (edad en años). Especialmente optimizado para Naranja, 
    Aguacate, Plátano y Guanábana.

    Args:
        row (pandas.Series): Una fila del DataFrame 'arboles' que debe contener obligatoriamente 
                            las columnas 'tipo_fruta' (str) y 'edad_anos' (int).

    Returns:
        pandas.Series: Una serie con dos índices:
            - 'N_g': Gramos de Nitrógeno recomendados por árbol.
            - 'K_g': Gramos de Potasio recomendados por árbol.
    """
    fruta = row['tipo_fruta']
    # ... resto del código
    fruta = row['tipo_fruta']
    edad = row['edad_anos']
    
    if fruta == 'Naranja':
        return pd.Series([600, 500] if edad >= 4 else [300, 250], index=['N_g', 'K_g'])
    elif fruta == 'Aguacate':
        return pd.Series([800, 600] if edad >= 4 else [400, 300], index=['N_g', 'K_g'])
    elif fruta == 'Plátano':
        return pd.Series([400, 800] if edad >= 2 else [200, 400], index=['N_g', 'K_g'])
    elif fruta == 'Guanábana':
        return pd.Series([500, 450] if edad >= 3 else [250, 200], index=['N_g', 'K_g'])
    else: # Mango, Limón, Mandarina, etc.
        return pd.Series([400, 400] if edad >= 4 else [200, 200], index=['N_g', 'K_g'])

# =================================================================
# 3. CREACIÓN DE PESTAÑAS (TABS)
# =================================================================
tab_reporte, tab_ingreso = st.tabs(["📊 Reporte y Gráficos", "➕ Registrar y Modificar Datos"])

# =================================================================
# PESTAÑA 1: REPORTE Y VISUALIZACIÓN
# =================================================================
with tab_reporte:
    try:
        conexion = obtener_conexion()
        df_arboles = pd.read_sql("SELECT tipo_fruta, cantidad, edad_anos FROM arboles;", conexion)
        conexion.close()
        
        if not df_arboles.empty:
            # Procesamiento de datos con Pandas
            df_analisis = df_arboles.apply(calcular_dosis_individual, axis=1)
            df_final = pd.concat([df_arboles, df_analisis], axis=1)
            df_final['Total_Nitrogeno_Kg'] = (df_final['cantidad'] * df_final['N_g']) / 1000
            df_final['Total_Potasio_Kg'] = (df_final['cantidad'] * df_final['K_g']) / 1000

            # Indicadores Clave superiores (Metrics)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Árboles en la Finca", value=int(df_final['cantidad'].sum()))
            with col2:
                st.metric(label="Nitrógeno Total Requerido", value=f"{df_final['Total_Nitrogeno_Kg'].sum():.1f} Kg")
            with col3:
                st.metric(label="Potasio Total Requerido", value=f"{df_final['Total_Potasio_Kg'].sum():.1f} Kg")

            st.write("---")

            # Filtro Dinámico
            opciones_frutas = ['Todos'] + list(df_final['tipo_fruta'].unique())
            fruta_seleccionada = st.selectbox("Filtrar visualización por cultivo:", opciones_frutas)

            df_filtrado = df_final if fruta_seleccionada == 'Todos' else df_final[df_final['tipo_fruta'] == fruta_seleccionada]

            # Distribución de Tablas y Gráficos
            col_izq, col_der = st.columns(2)
            with col_izq:
                st.subheader("📋 Inventario y Diagnóstico Nutricional")
                st.dataframe(df_filtrado[['tipo_fruta', 'cantidad', 'edad_anos', 'Total_Nitrogeno_Kg', 'Total_Potasio_Kg']], use_container_width=True)
            with col_der:
                st.subheader("📉 Balance de Insumos")
                fig = px.bar(df_filtrado, x='tipo_fruta', y=['Total_Nitrogeno_Kg', 'Total_Potasio_Kg'], 
                            barmode='group', labels={'value': 'Kilos (Kg)', 'tipo_fruta': 'Cultivo'})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("La base de datos está vacía. Añade registros en la pestaña de gestión.")
            
    except Exception as e:
        st.error(f"Error al cargar el reporte: {e}")

# =================================================================
# PESTAÑA 2: GESTIÓN DE DATOS (MÓDULOS DE ESCRITURA EN MYSQL)
# =================================================================
with tab_ingreso:
    st.subheader("📝 Panel de Control de Inventario y Suelos")
    
    col_form1, col_form2, col_form3 = st.columns(3)
    
    # --- FORMULARIO 1: REGISTRAR NUEVOS CULTIVOS ---
    with col_form1:
        st.info("Añadir Nuevos Lotes")
        with st.form("form_registro_nuevo_arbol", clear_on_submit=True):
            tipo_fruta = st.selectbox("Tipo de Fruta", ["Naranja", "Limón", "Aguacate", "Plátano", "Guanábana", "Mango"])
            cantidad = st.number_input("Cantidad de árboles", min_value=1, step=1, value=10)
            edad = st.number_input("Edad promedio (Anos)", min_value=0, step=1, value=2)
            estado = st.text_input("Estado de Salud", value="Óptimo")
            
            btn_guardar_arbol = st.form_submit_button("Guardar Árboles")
            
            if btn_guardar_arbol:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    query = "INSERT INTO arboles (tipo_fruta, cantidad, edad_anos, estado_salud) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (tipo_fruta, cantidad, edad, estado))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"✅ ¡Se registraron {cantidad} árboles de {tipo_fruta}!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al guardar en MySQL: {ex}")

    # --- FORMULARIO 2: ACTUALIZAR O ELIMINAR CULTIVOS EXISTENTES ---
    with col_form2:
        st.warning("Modificar o Eliminar")
        with st.form("form_modificar_arbol_existente", clear_on_submit=False):
            fruta_a_modificar = st.selectbox("Selecciona el Cultivo", ["Naranja", "Limón", "Aguacate", "Plátano", "Guanábana", "Mango"])
            
            st.markdown("**Nuevos valores (para actualización):**")
            nueva_cantidad = st.number_input("Nueva cantidad total", min_value=1, step=1, value=120)
            nueva_edad = st.number_input("Nueva edad promedio", min_value=0, step=1, value=5)
            nuevo_estado = st.text_input("Nuevo Estado", value="Óptimo")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                btn_actualizar = st.form_submit_button("Actualizar")
            with col_btn2:
                btn_eliminar = st.form_submit_button("🚨 Eliminar")
            
            if btn_actualizar:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    query = """
                        UPDATE arboles 
                        SET cantidad = %s, edad_anos = %s, estado_salud = %s 
                        WHERE tipo_fruta = %s
                    """
                    cursor.execute(query, (nueva_cantidad, nueva_edad, nuevo_estado, fruta_a_modificar))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"🔄 ¡Datos de {fruta_a_modificar} actualizados!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al actualizar: {ex}")

            if btn_eliminar:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    query = "DELETE FROM arboles WHERE tipo_fruta = %s"
                    cursor.execute(query, (fruta_a_modificar,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"🗑️ ¡Registro de {fruta_a_modificar} eliminado!")
                    st.rerun()
                except Exception as ex: Exception:
                st.error(f"Error al eliminar: {ex}")

    # --- FORMULARIO 3: REGISTRAR ANÁLISIS DE SUELO ---
    with col_form3:
        st.info("Análisis del Suelo")
        with st.form("form_registro_analisis_suelo", clear_on_submit=True):
            fecha = st.date_input("Fecha del análisis", value=datetime.today())
            nitrógeno = st.selectbox("Nivel de Nitrógeno", ["Bajo", "Medio", "Alto"])
            potasio = st.selectbox("Nivel de Potasio", ["Bajo", "Medio", "Alto"])
            ph = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, value=6.5, step=0.1)
            
            btn_guardar_suelo = st.form_submit_button("Guardar Análisis")
            
            if btn_guardar_suelo:
                try:
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    query = "INSERT INTO analisis_suelos (fecha_muestra, nivel_nitrogeno, nivel_potasio, ph_suelo) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (fecha, nitrógeno, potasio, ph))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("✅ ¡Análisis de suelo guardado con éxito!")
                except Exception as ex: Exception:
                st.error(f"Error al guardar análisis: {ex}")  # 👈 Al poner {exc} aquí, se quita el subrayado