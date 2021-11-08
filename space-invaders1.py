import pygame

#### COULEURS
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

FENETRE_LARGEUR = 896
FENETRE_HAUTEUR = 600

CANON_LARGEUR = 64
CANON_HAUTEUR = 64
CANON_Y = FENETRE_HAUTEUR * 0.85
CANON_DEPLACEMENT = 5

ALIEN_LARGEUR = 64
ALIEN_HAUTEUR = 64
INTERVAL_DEPLACEMENT_ALIEN = 300 #ms

HAUTEUR_BALLE = 8
LARGEUR_BALLE = 3
VITESSE_BALLE = -80  # VITESSE VERTICALE
INTERVAL_TIR = 1000 #ms | interval entre chaque tir


#### Fonctions
## Entités
def nouvelleEntite(image, position=None):
    if position is None:
        position = [0, 0]
    return {
        'visible': True,
        'position': position,
        'image': image,
        'dernierTir': -INTERVAL_TIR, # permet de tirer dès la première seconde
        'poses': {},  # dictionnaire de nom:image
        'animationActuelle': None,
        'animations': {},
    }

def ajoutePose(entite, nom, image):
    entite['poses'][nom] = image


def prendsPose(entite, nom_pose):
    entite['image'] = entite['poses'][nom_pose]
    visible(entite)
    a = 2
    a +=2


def nouvelleBalle(position, vitesse_verticale):
    return {
        'visible': False,
        'position': position,
        'vitesse': [0, vitesse_verticale],
        'acceleration': [0, 0],
        'momentDeplacement': maintenant,
        'rect': pygame.Rect(position, (LARGEUR_BALLE, HAUTEUR_BALLE)),
    }

def visible(entite):
    entite['visible'] = True


def invisible(entite):
    entite['visible'] = False


def estVisible(entite):
    return entite['visible']


def dessine(entite, ecran):
    ecran.blit(entite['image'], entite['position'])


def nouveauTir(scene, entite, decalle):
    if maintenant - entite['dernierTir'] > INTERVAL_TIR:
        tir = nouvelleBalle([entite['position'][0] + decalle, entite['position'][1]], VITESSE_BALLE)
        entite['dernierTir'] = maintenant
        ajouteEntite(scene, tir)


def deplace(entite):
    dt = (maintenant - entite['momentDeplacement']) / 1000
    # mise à jour vitesse
    entite['vitesse'][0] += entite['acceleration'][0] * dt
    entite['vitesse'][1] += entite['acceleration'][1] * dt
    # mise à jour position
    entite['position'][0] += entite['vitesse'][0] * dt
    entite['position'][1] += entite['vitesse'][1] * dt
    entite['rect'].x = entite['position'][0]
    entite['rect'].y = entite['position'][1]
    # mise à jour moment de déplacement
    entite['momentDeplacement'] = maintenant


## Scènes
def nouvelleScene():
    return {
        'acteurs': []
    }


def ajouteEntite(scene, entite):
    scene['acteurs'].append(entite)


def enleveEntite(scene, entite):
    acteurs = scene['acteurs']
    if entite in acteurs:
        acteurs.remove(entite)


def acteurs(scene):
    return list(scene['acteurs'])


def miseAJour(scene, maintenant):
    ma_scene = acteurs(scene)
    for entite in ma_scene:
        deplace(entite)
        pygame.draw.rect(fenetre, BLANC, entite['rect'])

def enScene(scene):
    for tir in acteurs(scene):
        if tir['rect'].right > FENETRE_LARGEUR or tir['rect'].left < 0:
            enleveEntite(scene, tir)
            print('pass')
        elif tir['rect'].bottom > FENETRE_HAUTEUR or tir['rect'].bottom < 0:
            enleveEntite(scene, tir)

def deplacer_canon(deplacement):
    canon['position'][0] += deplacement
    if canon['position'][0] >= FENETRE_LARGEUR - CANON_LARGEUR:
        canon['position'][0] = FENETRE_LARGEUR - CANON_LARGEUR
    elif canon['position'][0] <= 0:
        canon['position'][0] = 0

## Animations
def nouvelleAnimation():
    return {
        'boucle':False,
        'repetition': 0,
        'momentMouvementSuivant':None,
        'indexMouvement':None,
        'choregraphie':[] # liste de mouvements
    }


def repete(animation, fois):
    animation['repetition'] = fois
    animation['boucle'] = False


def enBoucle(animation):
    animation['boucle'] = True


def mouvement(nom, duree):
    return (nom, duree) # durée en msec


def nomMouvement(mvt):
    return mvt[0]


def dureeMouvement(mvt):
    return mvt[1]


def ajouteMouvement(animation, mvt):
    animation['choregraphie'].append(mvt)


def mouvementActuel(animation):
    if animation['indexMouvement'] == None:
        return None
    else:
        return nomMouvement(animation['choregraphie'][animation['indexMouvement']])


def commenceMouvement(animation, index):
    animation['indexMouvement'] = index
    animation['momentMouvementSuivant'] = pygame.time.get_ticks() + dureeMouvement(animation['choregraphie'][index])


def commence(animation):
    commenceMouvement(animation, 0)


def arrete(animation):
    animation['indexMouvement'] = None

def commenceAnimation(entite, nomAnimation, fois = 1):
    entite['animationActuelle'] = entite['animations'][nomAnimation]
    if fois == 0:
        enBoucle(entite['animationActuelle'])
    else:
        repete(entite['animationActuelle'], fois - 1)
    visible(entite)


def arreteAnimation(entite):
    arrete(entite['animationActuelle'])
    entite['animationActuelle'] = None


def ajouteAnimation(entite, nom, animation):
    entite['animations'][nom] = animation


def estEnAnimation(entite):
    return entite['animationActuelle'] != None



def anime(animation):
    if animation['indexMouvement'] == None:
        commence(animation)
    elif animation['momentMouvementSuivant'] <= pygame.time.get_ticks():
      if animation['indexMouvement'] == len(animation['choregraphie']) - 1:
        if animation['boucle']:
            commence(animation)
        else:
            if animation['repetition'] > 0:
                animation['repetition'] -= 1
                commence(animation)
            else:
                arrete(animation)
      else:
        commenceMouvement(animation, animation['indexMouvement'] + 1)


def affiche(entites, ecran):
    for objet in entites:
        if estVisible(objet):
            if estEnAnimation(objet):
                animationActuelle = objet['animationActuelle']
                poseActuelle = mouvementActuel(animationActuelle)
                anime(animationActuelle)
                nouvellePose = mouvementActuel(animationActuelle)
                if nouvellePose == None:
                    objet['animationActuelle'] = None
                    prendsPose(objet, poseActuelle)
                else:
                    prendsPose(objet, nouvellePose)

            dessine(objet, ecran)


## Entrees
def traite_entrees():
    global fini
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            fini = True
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_LEFT:
                deplacer_canon(-CANON_DEPLACEMENT)
            elif evenement.key == pygame.K_RIGHT:
                deplacer_canon(CANON_DEPLACEMENT)
            elif evenement.key == pygame.K_SPACE:
                nouveauTir(tirs, canon, CANON_LARGEUR / 2)


pygame.init()
pygame.key.set_repeat(10, 10)

fenetre_taille = (FENETRE_LARGEUR, FENETRE_HAUTEUR)
fenetre = pygame.display.set_mode(fenetre_taille)
pygame.display.set_caption('SPACE INVADERS')

canon_image = pygame.image.load('images/laser_canon.webp').convert_alpha(fenetre)
canon_image = pygame.transform.scale(canon_image, (CANON_LARGEUR, CANON_HAUTEUR))
canon = nouvelleEntite(canon_image, [(FENETRE_LARGEUR - CANON_LARGEUR) // 2, CANON_Y])
tirs = nouvelleScene()

alien = nouvelleEntite(None, [80, 80])
for nom_image, nom_fichier in (('ALIEN_UP','alien-up.png'),
                               ('ALIEN_DOWN','alien-down.png')):
    chemin = 'images/' + nom_fichier
    image = pygame.image.load(chemin).convert_alpha(fenetre)
    image = pygame.transform.scale(image, (ALIEN_LARGEUR, ALIEN_HAUTEUR))
    ajoutePose(alien, nom_image, image)
animation = nouvelleAnimation()
ajouteMouvement(animation, mouvement('ALIEN_UP', INTERVAL_DEPLACEMENT_ALIEN))
ajouteMouvement(animation, mouvement('ALIEN_DOWN', INTERVAL_DEPLACEMENT_ALIEN))
ajouteAnimation(alien, 'deplacement', animation)



aliens = nouvelleScene()
ajouteEntite(aliens, alien)
commenceAnimation(alien, 'deplacement', 0)


fini = False
temps = pygame.time.Clock()

while not fini:
    maintenant = pygame.time.get_ticks()

    traite_entrees()  # --- Traite entrees joueurs

    fenetre.fill(NOIR)
    anime(animation)
    dessine(canon, fenetre)

    miseAJour(tirs, maintenant)
    enScene(tirs)

    affiche([alien], fenetre)
    print(alien)

    pygame.display.flip()

    temps.tick(60)

pygame.display.quit()
pygame.quit()
exit()
