import json
import os
import matplotlib.pyplot as plt
import csv
from error_data import *
from participant import Participant


def resultats_chiffre(fichiers, dossier_entree, dossier_sortie, csv_bool):

    participants = []
    participants_obj = []
    participants_nom = []

    for index in range(len(fichiers)):
        nom_du_fichier = dossier_entree + fichiers[index]
        print(f"Process en cours [{index}/{len(fichiers)}]: {nom_du_fichier}")

        conditions = nom_du_fichier.split('_')
        corpus = conditions[0].split('/')[-1]
        participant = conditions[1]
        format = conditions[2]
        condition = conditions[3]
        if format == '2d' : condition = '2d'

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

        data = []
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
            nb_images_validees.append(nb_image_valide_a_d)
            temps.append(d['timeStamp']-LAPS_TEMPS[participant+corpus])
            # if nb_image_valide_a_d > 0 and nb_image_valide_a_d != len(data[-1]['idValidated']):
            #     nb_images_validees.append(nb_image_valide_a_d)
            #     temps.append(d['timeStamp'])

        # Fin de la boucle
        # ---------------------------------------------------------------------------------------------
        # Ecriture des resultats :

        plot_title = f"{corpus} - {participant} - {condition} Nombre d'images validées en fonction du temps"
        plt.title(plot_title)
        plt.plot(temps, nb_images_validees, color="green")
        plt.ylim(0, 100)
        plt.savefig(dossier_sortie + plot_title + '.png')
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

        if csv_bool:
            with open("resultat.csv", "a") as f:
                w = csv.DictWriter(f, resultats.keys())
                if index == 0: w.writeheader()
                w.writerow(resultats)

        nom_resultat = f"{condition} {corpus}"
        if not participant in participants_nom:
            participants_nom.append(participant)
            participant_actuel = Participant(participant)
            participant_actuel.ajout_resultat(nom_resultat, nb_images_validees, temps)
            participants_obj.append(participant_actuel)
        else:
            participants_obj[participants_nom.index(participant)].ajout_resultat(
                nom_resultat, nb_images_validees, temps
            )

    print('génération des images nb participants en fonction du temps 3 conditions en 1...')
    for p in participants_obj:
        plot_title = f"{p.nom} - trois conditions \n" \
                     f"nb images validées en fonction du temps"
        colors = ['red', 'blue', 'green']
        courbes = []
        fig, axis = plt.subplots(ncols=1, figsize=(15, 10))
        for n, r in p.resultats.items():
            c = ''
            if '2d' in n: c = 'red'
            elif 'cylindre' in n: c = 'blue'
            else: c = 'green'

            axis.set_title(plot_title)
            axis.set(ylim=(0, 90))
            ligne, = axis.plot(p.abscisse, r, label=f"{n}", color=c)
            courbes.append(ligne)

        axis.legend(handles=courbes)
        plt.savefig(dossier_sortie+ 'trois_condition/' + plot_title + '.png')
        plt.clf()
    print('... fini')


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

    camera_x = []
    camera_y = []
    camera_z = []

    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

    field = 'headPosition'
    if format == '2d':
        field = 'mousePosition'
        condition='2d'

    for d in data:
        positions_x.append(d[field]['x'])
        positions_y.append(d[field]['y'])
        positions_z.append(d[field]['z'])
        temps.append(d['timeStamp']-LAPS_TEMPS[participant+corpus])
        if format == '2d':
            camera_x.append(d['camPosition']['x'])
            camera_y.append(d['camPosition']['y'])
            camera_z.append(d['camPosition']['z'])

    plot_title_template = f"{condition} - {corpus} - {participant}"
    # Condition 2D
    if format == '2d':
        plot_title = plot_title_template + "\nPosition de la souris"
        fig, axis = plt.subplots(ncols=2, figsize=(15, 7))
        axis[0].set(xlim=(0,2000) ,ylim=(0, 1200))
        axis[0].set_title(plot_title)
        axis[0].plot(positions_x, positions_y, color="green")

        plot_title = plot_title_template + "\nPosition de la caméra\nDébut en haut à gauche"
        axis[1].set_title(plot_title)
        axis[1].plot(camera_x, camera_z, color="blue")
        plt.savefig('./data/plot_pos/' + format + '/' + plot_title_template + '.png')
        plt.clf()
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
        axis[1].set(xlim=(0, 350), ylim=(0, 3.2))
        axis[1].plot(temps, positions_y, color='blue')
        axis[1].set_title(plot_title)

        plt.savefig('./data/plot_pos/' + format + '/' + plot_title_template + '.png')
    plt.clf()


def graphe_image_fov_et_rotation(nom_du_fichier):
    conditions = nom_du_fichier.split('_')
    corpus = conditions[0].split('/')[-1]
    participant = conditions[1]
    format = conditions[2]
    condition = conditions[3]

    images_fov = []
    rotation = []
    frequence_rot = [0]*360
    temps = []

    data = []
    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

    if format == '2d':
        return

    for d in data:
        images_fov.append(d['imagesInFov'])
        rotation.append((
            d['headOrientationEulerAngles']['x'],
            d['headOrientationEulerAngles']['y'],
            d['headOrientationEulerAngles']['z']))
        temps.append(d['timeStamp']-LAPS_TEMPS[participant+corpus])
        frequence_rot[int(d['headOrientationEulerAngles']['y'])] += 1

    plot_title_template = f"images fov {condition} - {corpus} - {participant}"
    plot_title = plot_title_template + "\nNombre d'image dans le champ de vision en fonction du temps"
    fig, axis = plt.subplots(ncols=1, figsize=(10, 10))
    axis.set(xlim=(0, 310), ylim=(0, 1500))
    axis.plot(temps, images_fov, color="red")
    axis.set_title(plot_title)
    plt.savefig('./data/plot_fov/' + plot_title_template + '.png')
    plt.clf()

    plot_title_template = f"rotations {condition} - {corpus} - {participant}"
    plot_title = plot_title_template + "\nRotation en fonction du temps\n" \
                                       "Les pointillées signifient un changement rapide"
    fig, axis = plt.subplots(ncols=1, figsize=(10, 10))
    axis.set(ylim=(-50, 400))
    axis.plot(temps, [x[1] for x in rotation], 'o', markersize=1, color="red")
    axis.set_title(plot_title)
    plt.savefig('./data/plot_rot/' + plot_title + '.png')
    plt.clf()

    plot_title_template = f"rotations {condition} - {corpus} - {participant}"
    plot_title = plot_title_template + "\nFréquence de rotation\n" \
                                       "Abscisse : angle de rotation\n" \
                                       "Ordonnée : nombre de données ayant cette rotation"
    fig, axis = plt.subplots(ncols=1, figsize=(10, 10))
    axis.set(xlim=(-10, 400))
    axis.plot([x for x in range(0, 360)], frequence_rot, color="red")
    axis.set_title(plot_title)
    plt.savefig('./data/plot_rot/frequences/' + plot_title + '.png')
    plt.clf()


def graphe_acceleration(nom_du_fichier):
    conditions = nom_du_fichier.split('_')
    corpus = conditions[0].split('/')[-1]
    participant = conditions[1]
    format = conditions[2]
    condition = conditions[3]
    if format == '2d': condition='2d'

    main_acc = []
    souris_acc = []
    temps = []

    data = []
    with open(nom_du_fichier, 'r+', encoding='utf8') as file:
        # Convert file to JSON
        data = json.loads(file.read())['frames']

    for d in data:
        if format == '2d':
            main_acc.append(d['camAccelaration'])
            souris_acc.append(d['mouseAccelaration'])
        else:
            main_acc.append(d['headAcceleration'])
        temps.append(d['timeStamp']-LAPS_TEMPS[participant+corpus])

    plot_title = f"Accélération de la tête (3D) ou caméra (2D) \n {condition} - {corpus} - {participant}"
    fig, axis = plt.subplots(ncols=1, figsize=(10, 10))
    axis.plot(temps, main_acc, color="red")
    axis.set_title(plot_title)
    plt.savefig('./data/plot_acc/' + format + '/' + plot_title + '.png')
    plt.clf()

    if format == '2d':
        plot_title = f"Accélération de la souris \n {condition} - {corpus} - {participant}"
        fig, axis = plt.subplots(ncols=1, figsize=(10, 10))
        axis.plot(temps, souris_acc, color="blue")
        axis.set_title(plot_title)
        plt.savefig('./data/plot_acc/' + format + '/' + plot_title + '.png')
        plt.clf()


def nettoyage_cas_par_cas(fichiers):
    for index in range(len(fichiers)):
        nom_du_fichier = fichiers[index]
        print('nettoyage de ' + nom_du_fichier)
        conditions = nom_du_fichier.split('_')
        corpus = conditions[0].split('/')[-1]
        participant = conditions[1]
        format_c = conditions[2]
        condition = conditions[3]
        if format_c == '2d': condition = '2d'

        data = []
        with open('./data/json/' + nom_du_fichier, 'r+', encoding='utf8') as file:
            data = json.loads(file.read())['frames']

        index_premiere_donnee = -1
        index_derniere_donnee = 0
        a_coupe = False

        for index_data in range(len(data)):
            d = data[index_data]
            if index_premiere_donnee == -1 and d['timeStamp'] > LAPS_TEMPS[participant+corpus]:
                index_premiere_donnee = index_data
            if d['timeStamp'] - LAPS_TEMPS[participant+corpus] > 300:
                index_derniere_donnee = index_data
                a_coupe = True
                break

        print(f"   {len(data)}")
        if a_coupe: data = data[index_premiere_donnee:index_derniere_donnee]
        print(f"   {len(data)}")
        json_object = json.dumps({'frames':data}, indent=4)
        with open(f"./data/propre/{nom_du_fichier}", "w") as outfile:
            outfile.write(json_object)


def nettoyage(fichiers):
    for index in range(len(fichiers)):
        nom_du_fichier = fichiers[index]

        est_en_2d = '2d' in nom_du_fichier

        data = []
        with open('./data/json/' + nom_du_fichier, 'r+', encoding='utf8') as file:
            data = json.loads(file.read())['frames']

        derniere_position = [0,0,0]
        dernier_nb_images_validees = 0
        cherche = False
        temps_debut_recherche = 0
        index_derniere_donnee = 0
        nom_position = 'headPosition'
        if est_en_2d: nom_position = 'mousePosition'
        a_coupe = False

        for index_data in range(len(data)):
            d = data[index_data]
            if d['timeStamp'] < 300:
                continue

            if not cherche:
                cherche = True
                derniere_position = [v for v in d[nom_position].values()]
                dernier_nb_images_validees = len(d['idValidated'])
                temps_debut_recherche = d['timeStamp']
            else:
                if d['timeStamp'] - temps_debut_recherche > 50:
                    if derniere_position == [v for v in d[nom_position].values()] and \
                            dernier_nb_images_validees == len(d['idValidated']):
                        index_derniere_donnee = index_data
                        print(f"   a coupé {len(data)-index_derniere_donnee}")
                        a_coupe = True
                        break
                    else:
                        derniere_position = [v for v in d[nom_position].values()]
                        dernier_nb_images_validees = len(d['idValidated'])

        if a_coupe: data = data[:index_derniere_donnee]
        json_object = json.dumps({'frames':data}, indent=4)
        with open(f"./data/propre/{nom_du_fichier}", "w") as outfile:
            outfile.write(json_object)


def main():

    # On récupère tous les fichiers json (tri pour enlevé les dossiers)
    images_fov_final = {
        'sphere': [],
        'cylindre': []
    }
    compteur_de_fichier = {
        'sphere': 0,
        'cylindre': 0
    }

    net = int(input("nettoyage ? 0/1\n"))
    res = int(input("résultat chiffre ? 0/1\n"))
    autre = int(input("autres ? 0/1\n"))
    if autre:
        acc = int(input("accélération ? 0/1\n"))
        pos = int(input("position participant/souris/camera ? 0/1\n"))
        fov = int(input("fov/rotation ? 0/1\n"))
    else:
        acc, pos, fov = 0, 0, 0

    # Pour nettoyer les donnees
    if net == 1:
        nettoyage_cas_par_cas([f for f in os.listdir('./data/json') if not os.path.isdir(os.getcwd() + '/' + f)])

    fichiers = [f for f in os.listdir('./data/propre') if not os.path.isdir(os.getcwd() + '/' + f)]

    # Ecrire les résultats dans un csv et graphe du nombre d'images
    if res == 1:
        # resultats_chiffre([f for f in os.listdir('./data/json') if not os.path.isdir(os.getcwd() + '/' + f)], './data/json/', './data/ori/', False)
        resultats_chiffre([f for f in os.listdir('./data/propre') if not os.path.isdir(os.getcwd() + '/' + f)],
                      './data/propre/', './data/plot_images/', True)

    if autre == 0:
        return
    for index in range(len(fichiers)):
        nom_du_fichier = './data/propre/' + fichiers[index]
        print(f"Process en cours: {nom_du_fichier}")

        if os.path.isdir(os.getcwd() + '/' + nom_du_fichier):
            continue

        if acc:
            graphe_acceleration(nom_du_fichier)

        # Graphe des positions
        if pos:
            graphe_positions(nom_du_fichier)

        # Graphes du nombre d'images en fonction du temps
        if fov:
            graphe_image_fov_et_rotation(nom_du_fichier)


main()
