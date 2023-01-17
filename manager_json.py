import json
import os
import matplotlib.pyplot as plt
import csv
from error_data import *


def resultats_chiffre(nom_du_fichier, index):
    conditions = nom_du_fichier.split('_')
    corpus = conditions[0].split('/')[-1]
    participant = conditions[1]
    format = conditions[2]
    condition = conditions[3]

    tmp_zoom_etat = 0
    tmp_zoom_temps = 0.0

    tmp_validation_temps = 0
    tmp_validation_taille = 0
    tmp_temps_total_entre_zoom = 0
    tmp_temps_total_entre_validation = 0
    tmp_nb_total_validation = 0

    tmp_head_acceleration = 0

    resultats = {
        'participant': participant,
        'format': format,
        'condition': condition,
        'corpus': corpus,
        'nb_images_validees': 0,
        'nb_images_correctes': 0,
        'nb_images_hors_cat': 0,
        # Zoom
        'temps_moyen_entre_zoom': 0,
        'nb_total_zoom': 0,
        # Validation
        'temps_moyen_entre_validation': 0,
        'acceleration_moyenne_tete': 0,
        'acceleration_moyenne_manette': 0
    }

    nb_images_validees = []

    temps = []

    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

        # Chercher les images correctes
        resultats['nb_images_validees'] = len(data[-1]['idValidated'])
        for i in range(len(data[-1]['idValidated'])):
            cat = data[-1]['categoryValidated'][i]
            if cat == 'cible':
                resultats['nb_images_correctes'] += 1
            elif cat == 'reste':
                resultats['nb_images_hors_cat'] += 1

        for d in data:

            # Correction des erreurs liées au logiciel : ajout des images remises à zéro
            if participant == 'Amandine' and corpus == 'C2A' \
                    and float(d['timeStamp']) > 204.66:
                for i in range(len(AMANDINE_ERROR['idValidated'])):
                    if not AMANDINE_ERROR['idValidated'][i] in d['idValidated']:
                        d['idValidated'].append(AMANDINE_ERROR['idValidated'][i])
                        d['categoryValidated'].append(AMANDINE_ERROR['categoryValidated'][i])

            if participant == 'Marie' and corpus == 'C2B' \
                    and float(d['timeStamp']) > 333.54:
                for i in range(len(MARIE_ERROR['idValidated'])):
                    if not MARIE_ERROR['idValidated'][i] in d['idValidated']:
                        d['idValidated'].append(MARIE_ERROR['idValidated'][i])
                        d['categoryValidated'].append(MARIE_ERROR['categoryValidated'][i])

            if participant == 'Nathanael' and corpus == 'C3B' \
                    and float(d['timeStamp']) > 215.747:
                for i in range(len(NATHANAEL_ERROR['idValidated'])):
                    if not NATHANAEL_ERROR['idValidated'][i] in d['idValidated']:
                        d['idValidated'].append(NATHANAEL_ERROR['idValidated'][i])
                        d['categoryValidated'].append(NATHANAEL_ERROR['categoryValidated'][i])

            # nb_image_valide_a_d indique le nombre d'image validées à la donnée d
            nb_image_valide_a_d = len(d['idValidated'])

            # ZOOM : Calcul temps moyen
            if tmp_zoom_etat == 0 and d['controllerAction'] == 'Zoom':
                tmp_zoom_etat = 1
                resultats['nb_total_zoom'] += 1
                tmp_temps_total_entre_zoom += float(d['timeStamp']) - tmp_zoom_temps
            elif tmp_zoom_etat == 1 and d['controllerAction'] != 'Zoom':
                tmp_zoom_temps = float(d['timeStamp'])
                tmp_zoom_etat = 0

            # VALIDATION : Calcul temps moyen
            if tmp_validation_taille != nb_image_valide_a_d:
                tmp_validation_taille = nb_image_valide_a_d
                tmp_temps_total_entre_validation += float(d['timeStamp']) - tmp_validation_temps
                tmp_validation_temps = float(d['timeStamp'])
                tmp_nb_total_validation += 1

            # Acceleration
            if 'headAcceleration' in d.keys():
                resultats['acceleration_moyenne_tete'] += d['headAcceleration']
            if 'controllerRAcceleration' in d.keys():
                resultats['acceleration_moyenne_manette'] += d['controllerRAcceleration']

            # Plot
            if nb_image_valide_a_d > 0 and nb_image_valide_a_d != len(data[-1]['idValidated']):
                nb_images_validees.append(nb_image_valide_a_d)
                temps.append(d['timeStamp'])

        # Fin de la boucle
        # ---------------------------------------------------------------------------------------------
        # Ecriture des resultats :

        plot_title = f"{corpus} - {participant} - {condition} Nombre d'images en fonction du temps"
        plt.title(plot_title)
        plt.plot(temps, nb_images_validees, color="green")
        plt.savefig('./data/plot_images/' + plot_title + '.png')
        plt.clf()

        # Caclul des moyennes
        if resultats['nb_total_zoom'] > 0:
            resultats['temps_moyen_entre_zoom'] = "{:.2f}".format(
                tmp_temps_total_entre_zoom / resultats['nb_total_zoom'])
        else:
            resultats['temps_moyen_entre_zoom'] = 0
        resultats['temps_moyen_entre_validation'] = "{:.2f}".format(
            tmp_temps_total_entre_validation / tmp_nb_total_validation
        )
        resultats['acceleration_moyenne_tete'] = resultats['acceleration_moyenne_tete'] / len(data)
        resultats['acceleration_moyenne_manette'] = resultats['acceleration_moyenne_manette'] / len(data)

        with open("resultat.csv", "a") as f:
            w = csv.DictWriter(f, resultats.keys())
            if index == 0: w.writeheader()
            w.writerow(resultats)


def graphe_positions(nom_du_fichier):
    conditions = nom_du_fichier.split('_')
    corpus = conditions[0].split('/')[-1]
    participant = conditions[1]
    format = conditions[2]
    condition = conditions[3]

    positions_x = []
    positions_y = []
    positions_z = []
    temps = []

    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

        field = 'headPosition'
        if format == '2d':
            field = 'mousePosition'

        for d in data:
            positions_x.append(d[field]['x'])
            positions_y.append(d[field]['y'])
            positions_z.append(d[field]['z'])
            temps.append(d['timeStamp'])

        plot_title_template = f"{condition} - {corpus} - {participant}"
        # Condition 2D
        if format == '2d':
            plot_title = plot_title_template + "\nPosition de la souris"
            plt.title(plot_title)
            plt.xlim(0, 2000)
            plt.ylim(0, 1200)
            plt.plot(positions_x, positions_y, color="green")
            plt.savefig('./data/plot_pos/' + format + '/' + plot_title_template + '.png')
        # Condition 3D
        else:
            plot_title =  plot_title_template + "\nPosition vue du haut \n(couloir en haut " \
                         f"et fenêtre en bas)"
            fig, axis = plt.subplots(ncols=2, figsize=(20, 10))
            axis[0].set(xlim=(-3, 3), ylim=(-4, 4))
            axis[0].plot(positions_x, positions_z, color="green")
            axis[0].set_title(plot_title)

            plot_title =  plot_title_template + "\nElevation de la tête en fonction " \
                         f"du temps"
            axis[1].set(xlim=(0, 500), ylim=(0, 3.2))
            axis[1].plot(temps, positions_y, color='blue')
            axis[1].set_title(plot_title)

            plt.savefig('./data/plot_pos/' + format + '/' + plot_title_template + '.png')
        plt.clf()


def graphe_image_fov(nom_du_fichier):
    conditions = nom_du_fichier.split('_')
    corpus = conditions[0].split('/')[-1]
    participant = conditions[1]
    format = conditions[2]
    condition = conditions[3]

    images_fov = []
    temps = []

    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

        if format == '2d':
            return

        for d in data:
            images_fov.append(d['imagesInFov'])
            temps.append(d['timeStamp'])

        plot_title_template = f"images fov {condition} - {corpus} - {participant}"
        plot_title = plot_title_template + "\nNombre d'image dans le champ de vision en fonction du temps"
        fig, axis = plt.subplots(ncols=1, figsize=(20, 10))
        axis.plot(temps, images_fov, color="red")
        axis.set_title(plot_title)
        plt.savefig('./data/plot_fov/' + plot_title_template + '.png')
        plt.clf()


def main():

    fichiers = os.listdir('./data/')

    images_fov_final = {
        'sphere': [],
        'cylindre': []
    }
    compteur_de_fichier = {
        'sphere': 0,
        'cylindre': 0
    }

    for index in range(len(fichiers)):
        nom_du_fichier = './data/' + fichiers[index]
        print(f"Process en cours: {nom_du_fichier}")

        if os.path.isdir(os.getcwd() + '/' + nom_du_fichier):
            continue

        # Ecrire les résultats dans un csv et graphe du nombre d'images
        resultats_chiffre(nom_du_fichier, index)

        # Graphe des positions
        graphe_positions(nom_du_fichier)

        # Graphes du nombre d'images en fonction du temps
        graphe_image_fov(nom_du_fichier)

        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # Moyenne du nombre d'image FOV
        with open(nom_du_fichier, 'r+', encoding='utf8') as file:
            # Convert file to JSON
            data = json.loads(file.read())['frames']
            if nom_du_fichier.split('_')[2] == '2d':
                continue

            condition = nom_du_fichier.split('_')[3]

            compteur_de_fichier[condition] += 1

            for i in range(len(data)):
                d = data[i]

                if d['timeStamp'] > 500:
                    continue

                if len(images_fov_final[condition]) <= i:
                    images_fov_final[condition].append(d['imagesInFov'])
                else:
                    images_fov_final[condition][i] += d['imagesInFov']

    for i in range(len(images_fov_final['sphere'])):
        images_fov_final['sphere'][i] = images_fov_final['sphere'][i] / compteur_de_fichier['sphere']
    for i in range(len(images_fov_final['cylindre'])):
        images_fov_final['cylindre'][i] = images_fov_final['cylindre'][i] / compteur_de_fichier['cylindre']

    fig, axis = plt.subplots(ncols=2, figsize=(20, 10))
    axis[0].plot([i for i in range(len(images_fov_final['sphere']))],images_fov_final['sphere'], color="red")
    axis[0].set_title('sphere')
    axis[1].plot([i for i in range(len(images_fov_final['cylindre']))], images_fov_final['cylindre'], color='red')
    axis[1].set_title('cylindre')
    plt.savefig('./data/plot_fov/' + 'MOYENNE.png')
    plt.clf()

    # Fin moyenne FOV
    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------

main()
