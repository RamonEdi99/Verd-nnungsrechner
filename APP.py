import os
import json
import streamlit as st
import pandas as pd
from PIL import Image
from jasonbin import load_key, save_key
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

jsonbin_secrets = st.secrets["jsonbin"]
api_key = jsonbin_secrets["api_key"]
bin_id = jsonbin_secrets["bin_id"]

# Definieren App Name und Icon
st.set_page_config(page_title="Verdünnungsrechner", page_icon=":Woman Scientist emoji:")

# -------- user login --------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

fullname, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == True:   # login successful
    authenticator.logout('Logout', 'main')   # show logout button
elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()
    
data = load_key(api_key, bin_id, username) 
    
    

# Funktion zum Laden der Adressliste aus einer JSON-Datei
def load_data(filename):
   if os.path.isfile(filename):
       with open(filename, "r", encoding="utf-8") as file:
           data = json.load(file)
   else:
       data = []
   return data


# Funktion zum Speichern der Adressliste in einer JSON-Datei
def save_data(data, filename):
   with open(filename, "w", encoding="utf-8") as file:
       json.dump(data, file, indent=2, ensure_ascii=False)



def pages():
   st.subheader("Neue Berechnung")
   global name
   name = st.text_input("Versuch: ")


   # Eingabefeld für Stoffname
   stoffname = st.text_input("Stoffname:")

   # Eingabefeld für Endvolumen in Millilitern (ml)
   endvolumen_ml = st.number_input("Endvolumen (ml)", min_value=0.0, step=0.1)

   # Dropdown-Menü für Auswahl der Verdünnungsstufen
   global Verdunnungsfaktor_1zuX
   Verdunnungsfaktor_1zuX = st.selectbox("Verdünnung", options=range(1, 101), format_func=lambda x: f"Verdünnung 1:{x}")

   # Berechnung der benötigten Menge des Stoffs und Verdünnungsmittel in Mikrolitern (µl)
   benoetigte_menge_stoff_ul = endvolumen_ml * 1000 / Verdunnungsfaktor_1zuX
   verdunnungsmittel_menge_ul = benoetigte_menge_stoff_ul * (Verdunnungsfaktor_1zuX - 1)

   # Anzeige der berechneten Werte in Mikrolitern (µl)
   st.write(f"Verdünnungsfaktor: 1:{Verdunnungsfaktor_1zuX}")
   st.write(f"Benötigte Menge des Verdünnungsmittels: {verdunnungsmittel_menge_ul:.2f} µl")
   st.write(f"Benötigte Menge von {stoffname}: {benoetigte_menge_stoff_ul:.2f} µl")

   # Button für Wikipedia-Link des Stoffnamens
   if stoffname:
       wikipedia_link = f"https://de.wikipedia.org/wiki/{stoffname}"
       if st.button("Wikipedia-Seite anzeigen"):
           st.write(f"[Wikipedia-Seite von {stoffname}]({wikipedia_link})")

   # Eingabefeld für Bemerkungen
   st.subheader("Bemerkungen")
   bemerkungen = st.text_area("zu deiner Verdünnungsreihe:", height=100)

   return [stoffname, endvolumen_ml, verdunnungsmittel_menge_ul, benoetigte_menge_stoff_ul, bemerkungen]

   # # Submit-Button, um die eingegebenen Daten zu speichern und die Berechnungen durchzuführen
   if st.button("Berechnung speichern"):
        return [stoffname, endvolumen_ml, verdunnungsmittel_menge_ul, benoetigte_menge_stoff_ul, bemerkungen]

# Streamlit-App
def app():
   st.title("Verdünnungsrechner für Deine Verdünnungsreihe")

   # Sidebar
   options = ["Neue Berechnung", "Archiv", "Gefahrensymbole"]

   page = st.sidebar.radio("Seite auswählen", 
                           options
                           )

   data = load_data("data.json")

 
   if page == options[0]:

       seite = pages()

       data[name] = {}
       data[name]["Stoffname"] = seite[0]
       data[name]["Endvolumen in ml"] = seite[1]
       data[name]["Verdünnungsmittel in ul"] = seite[2]
       data[name]["Menge von Stoff in ul"] = seite[3]
       data[name]["Verdünnungsfaktor"] = Verdunnungsfaktor_1zuX
       data[name]["Bemerkungen"] = seite[4]
       
       
       if st.button("Speichern"):
           save_data(data, "data.json")
            
            
   
   if page == options[1]:
       data = load_data("data.json")
       st.subheader("Archiv")

       # Convert the JSON to a list of dictionaries
       fin = []
       for key, value in data.items():
           value["row_name"] = key
           fin.append(value)

       # Create DataFrame from the list of dictionaries
       df = pd.DataFrame(fin)

       # Set the row_name column as the index
       df.set_index("row_name", inplace=True)

       st.table(df)
      
   if page == options[2]:

        # Define the dictionary of substances and their corresponding hazard symbols
        substances = {
            "Wasserstoffperoxid": ["GHS03", "GHS05", "GHS07"],
            "Benzol": ["GHS02", "GHS07", "GHS08"],
            "Chlor": ["GHS03", "GHS05", "GHS08"],
            "Salzsäure": ["GHS05", "GHS07", "GHS09"],
            "Pikrinsäure": ["GHS01", "GHS06"],
            "Glycerintrinitrat": ["GHS01", "GHS06", "GHS09"],
            "Ethin": ["GHS02"],
            "Diethylether": ["GHS02", "GHS08"],
            "Benzin": ["GHS02", "GHS06", "GHS09"],
            "Ethanol": ["GHS02", "GHS07"],
            "Aceton": ["GHS02", "GHS07"],
            "Kaliumnitrat": ["GHS03"],
            "Cyanwasserstoff": ["GHS02", "GHS06", "GHS09"],
            "Bariumchlorid": ["GHS06"],
            "Bleioxid": ["GHS06", "GHS09"],
            "Methanol": ["GHS06", "GHS02"],
            "Calciumchlorid": ["GHS07"],
            "Natriumcarbonat": ["GHS07"],
            "Kupfersulfat": ["GHS08", "GHS09"],
            "Kaliumiodid": ["GHS08"],
            "Natriumthiosulfat": ["GHS02", "GHS08", "GHS07", "GHS09"],
            "Essigsäure": ["GHS02", "GHS05"],
            "Iodmonochlorid": ["GHS05", "GHS07"],
            "Iodtrichlorid": ["GHS05", "GHS07"],
            "Phenolphthalein": ["GHS08", "GHS07"],
            "Natronlauge": ["GHS05"],
            "Schwefelsäure": ["GHS05"],
            "Natriumcarbonat": ["GHS07"],
            "Natriumhydroxid": ["GHS05"],
            "Ascorbinsäure": [""],
            "1-Pentanol": ["GHS02", "GHS05", "GHS07"],
            "Essigsäureethylester": ["GHS02", "GHS07"],
            "3-Pentanon": ["GHS02", "GHS07"],
            "n-Hexan": ["GHS02", "GHS08", "GHS07", "GHS09"],
            "2-Propanol": ["GHS02", "GHS07"],
            "Aluminiumoxid": [""],
            "Methanol": ["GHS02", "GHS06", "GHS08"],
            "Bariumchlorid": ["GHS06"],
            "Ethylendiamintetraessigsäure": ["GHS07"],
            "Natriumacetattrihydrat": [""],
            "Kaliumthiocyanat": ["GHS05", "GHS07"],
            "Ammoniaklösung": ["GHS05", "GHS07", "GHS09"],
            "Kaliumhexacyanoferrat(III)": ["GHS07", "GHS09"],
        }
        
        # Define the function to display the hazard symbols for a given substance
        def display_hazard_symbols(substance):
            # Get the list of hazard symbols for the given substance
            symbols = substances.get(substance)
            if symbols is None:
                st.write(f"Keine Gefahrensymbole gefunden für {substance}.")
                return
            # Load the hazard symbol images
            images = [Image.open(f"images/{symbol}.png") for symbol in symbols]
            # Display the images in a horizontal layout
            st.image(images, width=100)
        
        # Define the Streamlit app
        def main():
            st.subheader("Gefahrensymbole")
            # Add an input field for the substance name
            substance = st.text_input("Stoffname:")
            # Add a button to display the hazard symbols for the entered substance
            if st.button("Gefahrensymbole anzeigen"):
                display_hazard_symbols(substance)

        main()

# App starten
app()
