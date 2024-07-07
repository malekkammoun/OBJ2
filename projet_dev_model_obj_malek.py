import numpy as np
from flask import Flask, request, render_template
import pickle
from sklearn.preprocessing import StandardScaler
import re
from flask import Flask, request, render_template, redirect, url_for

# Définition de la fonction pour extraire la marque du téléphone à partir de la chaîne de caractères
def extract_brand(text):
    match = re.search(r'^([^ ]+)', text)
    if match:
        return match.group(1)
    else:
        return None

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

# Charger les encodeurs sauvegardés
le_v1 = pickle.load(open('le_v1.pkl', 'rb'))
le_v4 = pickle.load(open('le_v4.pkl', 'rb'))
le_v7 = pickle.load(open('le_v7.pkl', 'rb'))
le_v8 = pickle.load(open('le_v8.pkl', 'rb'))
le_phone_brand = pickle.load(open('le_phone_brand.pkl', 'rb'))  # Charger l'encodeur pour phone_brand

# Sélection des variables pertinentes
selected_features = ['V6', 'V10', 'V11', 'V12', 'total_revenu_op', 'total_nb_options', 'total_recharge',
                     'total_nomtant_remb', 'total_nb_recharge', 'V7_encoded', 'V5']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    # Récupérer les valeurs du formulaire
    form_values = request.form.to_dict()

    # Convertir les valeurs nécessaires en float
    for key in form_values:
        try:
            form_values[key] = float(form_values[key])
        except ValueError:
            pass

    # Encoder les valeurs nécessaires
    encoded_values = {}
    if 'V1' in form_values:
        encoded_values['V1_encoded'] = le_v1.transform([form_values['V1']])[0]
    if 'V4' in form_values:
        encoded_values['V4_encoded'] = le_v4.transform([form_values['V4']])[0]
    if 'V7' in form_values:
        encoded_values['V7_encoded'] = le_v7.transform([form_values['V7']])[0]
    if 'V8' in form_values:
        encoded_values['V8_encoded'] = le_v8.transform([form_values['V8']])[0]

    # Extraire la marque du téléphone à partir de V9
    phone_brand = extract_brand(str(form_values.get('V9', '')))
    
    # Encoder la marque du téléphone
    if phone_brand is not None and phone_brand in le_phone_brand.classes_:
        encoded_values['phone_brand_encoded'] = le_phone_brand.transform([phone_brand])[0]
    else:
        # Gérer le cas où la marque du téléphone n'est pas reconnue
        encoded_values['phone_brand_encoded'] = le_phone_brand.transform(['Autre'])[0]

    # Calculer les nouvelles colonnes basées sur les form_values
    form_values['total_in_out'] = form_values.get('V12', 0) + form_values.get('V11', 0)

    recharge_columns_1 = ['V13', 'V14', 'V15', 'V16', 'V17']
    form_values['total_nb_recharge'] = sum([form_values.get(col, 0) for col in recharge_columns_1])

    recharge_columns_2 = ['V18', 'V19', 'V20', 'V21', 'V22']
    form_values['total_recharge'] = sum([form_values.get(col, 0) for col in recharge_columns_2])

    revenu_columns = ['V23', 'V24']
    form_values['total_revenu_op'] = sum([form_values.get(col, 0) for col in revenu_columns])

    remb_columns = ['V25', 'V26']
    form_values['total_nomtant_remb'] = sum([form_values.get(col, 0) for col in remb_columns])

    options_columns = ['V27', 'V28']
    form_values['total_nb_options'] = sum([form_values.get(col, 0) for col in options_columns])

    # Préparer les caractéristiques finales pour la standardisation et la prédiction
    final_features = np.array([form_values.get(feature, 0) for feature in selected_features]).reshape(1, -1)

    # Standardisation des caractéristiques
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(final_features)

    # Prédiction avec le modèle KMeans
    prediction = model.predict(scaled_features)

    output = round(prediction[0], 2)

     # Redirection vers la page d'accueil pour rafraîchir la page
    return render_template('index.html', prediction_text='La réponse est {}'.format(output))

if __name__ == "__main__":
    app.run(debug=True)
