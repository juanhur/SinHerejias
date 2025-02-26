import streamlit as st
import streamlit_antd_components as sac

# Datos de ejemplo con múltiples proyectos
data = [
    {'Nombre_proyecto': 'Proyecto Datos',
     'Proyecto': 'AN-2025-0002',
     'Epicas': [
         'Análisis de Datos de Clientes',
         'Generación de Campañas Personalizadas',
         'Integración de Sistemas',
         'Medición de Éxito de Campañas',
         'Capacitación y Gestión del Cambio'
     ]},
    {'Nombre_proyecto': 'Proyecto Seguridad',
     'Proyecto': 'SE-2025-0003',
     'Epicas': [
         'Evaluación de Riesgos',
         'Implementación de Controles de Seguridad',
         'Capacitación en Seguridad Informática'
     ]}
]

# Construcción del árbol de proyectos y épicas
tree_items = []
for item in data:
    epicas_children = [sac.TreeItem(epica, icon='file') for epica in item["Epicas"]]
    project_node = sac.TreeItem(item["Nombre_proyecto"], icon='folder', children=epicas_children)
    tree_items.append(project_node)

# Mostrar árbol en Streamlit
st.title("Estructura de Proyectos y Épicas")

sac.tree(items=tree_items, label='Proyectos y Épicas', icon='table', open_all=True, checkbox=True)
