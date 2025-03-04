import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import seaborn as sns
#from pathlib import Path
#import importlib.util
import requests
import sys
import os
import time
#*****************************************************************************
def load_beautifulsoup_script():
    """Fonction de scraping pour CoinAfrique"""
    try:
        # Définition des URLs et DataFrames
        urls_df = {
            'url_1': 'https://sn.coinafrique.com/categorie/chiens',
            'df_1': None,
            'url_2': 'https://sn.coinafrique.com/categorie/moutons',
            'df_2': None,
            'url_3': 'https://sn.coinafrique.com/categorie/autres-animaux',
            'df_3': None,
            'url_4': 'https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons',
            'df_4': None
        }

        # Barre de progression Streamlit
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Scraping pour chaque URL
        for i in range(1, 5):
            status_text.text(f'Scraping de la catégorie {i}/4...')
            data = []
            
            try:
                response = requests.get(urls_df[f'url_{i}'])
                response.raise_for_status()  # Vérifie si la requête a réussi
                bsp = bs(response.text, 'html.parser')
                containers = bsp.find_all('div', class_='col s6 m4 l3')

                for item in containers:
                    try:
                        info = {
                            "Image_lien": item.find('img', class_='ad__card-img').attrs['src'],
                            "Prix": item.find('p', class_='ad__card-price').text.strip(),
                            "Adresse": item.find('p', class_='ad__card-location').find('span').text
                        }

                        if i == 4:
                            # Traitement spécial pour poules, lapins et pigeons
                            details_page_url = item.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                            details_page_response = requests.get(f'https://sn.coinafrique.com{details_page_url}')
                            details_page_bsp = bs(details_page_response.text, 'html.parser')
                            
                            element_detail = details_page_bsp.find('div', class_='ad__info__box ad__info__box-descriptions')
                            if element_detail and element_detail.find_all('p'):
                                info['Détail'] = element_detail.find_all('p')[1].text.strip().replace('\r\n', ' ').replace('\r\r', ' ')
                            else:
                                info['Détail'] = ""
                            
                            time.sleep(1)  # Pause pour éviter de surcharger le serveur
                        else:
                            info['Nom'] = item.find('p', class_='ad__card-description').text.strip()

                        data.append(info)
                    except Exception as e:
                        st.warning(f"Erreur lors du scraping d'un item: {str(e)}")
                        continue

                urls_df[f'df_{i}'] = pd.DataFrame(data)
                
                # Sauvegarde des données
                filename = {
                    1: 'chiens.csv',
                    2: 'moutons.csv',
                    3: 'autres_animaux.csv',
                    4: 'poules_lapins_et_pigeons.csv'
                }[i]
                
                # Création du dossier si nécessaire
                import os
                os.makedirs('data_clean', exist_ok=True)
                
                # Sauvegarde du DataFrame
                urls_df[f'df_{i}'].to_csv(f'data_clean/{filename}', index=False)
                
                # Mise à jour de la barre de progression
                progress_bar.progress(i * 25)
                
            except requests.RequestException as e:
                st.error(f"Erreur lors de la requête pour l'URL {i}: {str(e)}")
                continue
            except Exception as e:
                st.error(f"Erreur inattendue pour la catégorie {i}: {str(e)}")
                continue

        progress_bar.progress(100)
        status_text.text('Scraping terminé !')
        
        return urls_df
        
    except Exception as e:
        st.error(f"Erreur générale lors du scraping: {str(e)}")
        return None

def main_scraping(n_pages=1):
    """Fonction principale appelée par Streamlit"""
    urls_df = load_beautifulsoup_script()
    if urls_df:
        st.success("Scraping terminé avec succès!")
        
        # Afficher un aperçu des données récupérées
        for i in range(1, 5):
            if urls_df[f'df_{i}'] is not None:
                st.subheader(f"Aperçu des données - Catégorie {i}")
                st.dataframe(urls_df[f'df_{i}'].head())
    
    return urls_df
#----------------------------------------------------------------------------------------------------------
def visualize_data(df, plot_type, x_col, y_col):
    """Fonction pour créer différents types de visualisations"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if plot_type == "Ligne":
        plt.plot(df[x_col], df[y_col])
    elif plot_type == "Barre":
        plt.bar(df[x_col], df[y_col])
    elif plot_type == "Scatter":
        plt.scatter(df[x_col], df[y_col])
    elif plot_type == "Heatmap":
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm')
    
    plt.title(f"Graphique {plot_type}")
    if x_col and y_col:
        plt.xlabel(x_col)
        plt.ylabel(y_col)
    return fig
#---------------------------------------------------------------------------------------------------
# Configuration de la page
st.set_page_config(
    page_title="Application de Web Scraping et Analyse",
    layout="wide"
)

# Sidebar avec les options
st.sidebar.title("Menu de Navigation")

# Nombre de pages pour le scraping
n_pages = st.sidebar.number_input(
    "Nombre de pages à scraper",
    min_value=1,
    value=1
)

# Menu déroulant des options
option = st.sidebar.selectbox(
    "Choisissez une option",
    ["Accueil",
     "Scraping des données",
     "Données scrapées",
     "Données non-scrapées",
     "Visualisation",
     "Formulaire d'évaluation"]
)

# Contenu principal
if option == "Accueil":
    st.title("🌐APPLICATION DE WEB-SCRAPING")
    st.write("""
    Cette application permet de:
    - Scraper des données avec BeautifulSoup
    - Visualiser les données scrapées
    - Télécharger les données (nettoyées et non-nettoyées)
    - Remplir un formulaire d'évaluation
    """)

elif option == "Scraping des données":
    st.title("🔍 Scraping des données")
    
    if st.button("Lancer le scraping"):
        scraping_module = load_beautifulsoup_script()
        if scraping_module:
            try:
                # Appel de la fonction de scraping de votre module
                # Adaptez cette partie selon votre fonction de scraping
                with st.spinner("Scraping en cours..."):
                    # scraping_module.votre_fonction_scraping(n_pages)
                    st.success(f"Scraping terminé pour {n_pages} pages!")
            except Exception as e:
                st.error(f"Erreur pendant le scraping: {str(e)}")

elif option == "Données scrapées":
    st.title("📊 Données scrapées (nettoyées)")
    
    # Chemin vers vos données nettoyées
    clean_data_path = "data_clean"
    clean_files = [f for f in os.listdir(clean_data_path) if f.endswith('.csv')]
    
    if clean_files:
        selected_file = st.selectbox(
            "Choisissez un fichier",
            clean_files
        )
        
        df = pd.read_csv(os.path.join(clean_data_path, selected_file))
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            "Télécharger les données",
            csv,
            f"clean_{selected_file}",
            "text/csv"
        )
    else:
        st.info("Aucun fichier de données nettoyées disponible")

elif option == "Données non-scrapées":
    st.title("📑 Données non-scrapées")
    
    # Chemin vers vos données non-nettoyées
    unclean_data_path = "data_unclean"
    unclean_files = [f for f in os.listdir(unclean_data_path) if f.endswith('.csv')]
    
    if unclean_files:
        selected_file = st.selectbox(
            "Choisissez un fichier",
            unclean_files
        )
        
        df = pd.read_csv(os.path.join(unclean_data_path, selected_file))
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            "Télécharger les données",
            csv,
            f"unclean_{selected_file}",
            "text/csv"
        )
    else:
        st.info("Aucun fichier de données non-nettoyées disponible")

elif option == "Visualisation":
    st.title("📈 Visualisation des données")
    
    # Sélection du fichier à visualiser
    data_files = [f for f in os.listdir("data_clean") if f.endswith('.csv')]
    
    if data_files:
        selected_file = st.selectbox(
            "Choisissez un fichier à visualiser",
            data_files
        )
        
        df = pd.read_csv(os.path.join("data_clean", selected_file))
        
        # Options de visualisation
        plot_type = st.selectbox(
            "Type de graphique",
            ["Ligne", "Barre", "Scatter", "Heatmap"]
        )
        
        if plot_type != "Heatmap":
            cols = df.columns.tolist()
            x_col = st.selectbox("Choisissez la colonne X", cols)
            y_col = st.selectbox("Choisissez la colonne Y", 
                               df.select_dtypes(include=['float64', 'int64']).columns)
            
            fig = visualize_data(df, plot_type, x_col, y_col)
        else:
            fig = visualize_data(df, plot_type)
        
        st.pyplot(fig)
    else:
        st.info("Aucun fichier de données disponible pour la visualisation")

elif option == "Formulaire d'évaluation":
    st.title("📝 Formulaire d'évaluation")
    
    # Remplacez par votre URL KoboToolbox
    kobotoolbox_url = "VOTRE_URL_KOBOTOOLBOX"
    
    st.components.v1.html(
       f'<iframe src=https://ee.kobotoolbox.org/i/YMkinkZI width="800" height="600"></iframe>',height=700)
       


# Footer
st.markdown("---")
st.markdown("© 2025 - Développé par Arthur-MANTSOUAKA")
