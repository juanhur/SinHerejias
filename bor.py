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




##print(str(proyectos_ord))
        df=calcular_Matriz_rango_valores(matriz_suma)
        proyectos_seleccionados=consultar_nombres_proyectos(list(proyectos_ord))
        Proyectocod_nom = [f"{k}/{v}" for k, v in proyectos_seleccionados.items()]
        #st.write('Seleccione los proyectos en orden de importancia de Izquierda a Derecha:') 
        #sorted_items = sort_items(Proyectocod_nom)
        # Aplicar filtro
        df["proyecto"]=proyectos_ord.values
        epicas_proyecto_sel=consultar_epicas_por_codigo_proyecto(proyectos_seleccionados)
        df_filtrado = df[df["proyecto"].isin(proyectos_seleccionados)]
        df_filtrado = df_filtrado.sort_values(by=["proyecto"])
        # Ordenar las columnas según la lista_orden
        df_filtrado = df_filtrado.reindex(columns=lista_orden)
        lista_filtrada = [elemento for elemento in lista_orden if elemento in epicas_proyecto_sel]
        # Ordenar las filas según el índice de lista_orden (suponiendo que lista_orden también contiene los índices de las filas)
        df_filtrado = df_filtrado.reindex(index= lista_filtrada)
        #st.dataframe( df_filtrado)
        for index, row  in edited_df.iterrows():
                         dic={}
                         index=epicas_proyecto_codigo[row['proyecto']][index]
                         index=index.rsplit("-EP", 1)[1]   # Divide desde el final en "-EP"
                         filtro = {"epicas.id_epica": int(index), "proyecto":row['proyecto']}  # Agregar proyecto como filtro
                         print(filtro)
                         for col_name, valor in row.items():
                            if pd.notna(valor):  
                                #print(col_name)
                                if col_name!="proyecto":
                                    proyecto, id_epica = col_name.rsplit("-EP", 1)  # Divide desde el final en "-EP"
                                    dic["proyecto"]=proyecto
                                    dic["id_epica"]=int(id_epica)
                                    dic["valor"]=int(valor)
                                    actualizar_un_elemento_matriz_n(index,dic,filtro)
                            #else:
                                #print("valor nulo")

                             