class Participant:
    def __init__(self, nom):
        self.resultats = {
        }
        self.max = 0
        self.nom = nom
        self.abscisse = []

    def ajout_resultat(self, nature, donnees, abscisse):
        self.resultats[nature] = donnees
        if len(self.abscisse) < len(abscisse):
            self.abscisse = abscisse

        for key in self.resultats.keys():
            if len(self.resultats[key]) < len(self.abscisse):
                l = len(self.resultats[key])
                last = self.resultats[key][-1]
                self.resultats[key] = self.resultats[key] + [last for _ in range(len(self.abscisse)-l)]

        self.nettoyage(nature)

    def nettoyage(self, nature):

        for r in self.resultats:
            for valeur in r:
                return


