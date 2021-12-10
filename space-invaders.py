# ROBERT Louan

import random
import math
from modules import *

# définition d'un nouvel évènement pour représenter une touche qui reste enfoncée
pygame.KEYPRESSED = pygame.USEREVENT

#### COULEURS
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS_CLAIR = (169, 169, 169)
ROUGE = (255, 0, 0)
VERT = 35, 204, 1, 255
BLEU = 32, 122, 217

SANTE_DEPART = 100 #hp

FENETRE_LARGEUR = 800  # px
FENETRE_HAUTEUR = 600  # px

CANON_LARGEUR = 64  # px
CANON_HAUTEUR = 64  # px
CANON_Y = 510
canon_deplacement = 5  # px

ALIEN_LARGEUR = 64  # px
ALIEN_HAUTEUR = 64  # px
VITESSE_ALIEN = 30  # px/s
INTERVALLE_DEPLACEMENT_ALIEN = 300  # ms
NBR_ALIENS_HORIZONTAL = 5
NBR_ALIENS_VERTICAL = 0
DISTANCE_ALIEN_HORIZONTAL = ALIEN_LARGEUR * 2
DISTANCE_ALIEN_VERTICAL = ALIEN_HAUTEUR

HAUTEUR_BALLE = 8  # px
LARGEUR_BALLE = 3  # px
VITESSE_BALLE = -80  # VITESSE VERTICALE
INTERVALLE_TIR_JOUEUR = 1000  # ms | interval entre chaque tir
INTERVALLE_TIR_ALIEN = 600  # ms
INTERVALLE_POWERUP = 8000

TOUCHE_LARGEUR = 64
TOUCHE_HAUTEUR = 64


#### Fonctions

def nouvelleEntite(type, position=None, rect=None, vitesse=None, couleur=BLANC):
    """Crée une nouvelle entité"""
    if vitesse is None:
        vitesse = [0, 0]
    if position is None:
        position = [0, 0]
    return {
        'visible': True,
        'position': position,
        'vitesse': vitesse,
        'acceleration': [0, 0],
        'type': type,
        'rangeeAlien': 0,
        'colonneAlien': 0,
        'derniereDirection': 'DROITE',
        'image': None,
        'dernierTir': -INTERVALLE_TIR_JOUEUR,  # permet de tirer dès la première seconde
        'poses': {},  # dictionnaire de nom:image
        'animationActuelle': None,
        'animé': True,
        'animations': {},
        'momentDeplacement': pygame.time.get_ticks(),
        'rect': rect,
        'couleur': couleur
    }


def nouveauTirJoueur(scene, entite, decalle):
    """Crée un nouveau tir joueur"""
    if maintenant - entite['dernierTir'] > INTERVALLE_TIR_JOUEUR:
        tir = nouvelleEntite('tir', [entite['position'][0] + decalle, entite['position'][1]],
                             rect=pygame.Rect(entite['position'], (LARGEUR_BALLE, HAUTEUR_BALLE)),
                             vitesse=[0, VITESSE_BALLE], couleur=BLANC)
        ajouteEntite(scene, tir)
        entite['dernierTir'] = maintenant
        joue_son('TIR')


def nouveauTirAlien(scene, position):
    """Crée un nouveau tir alien"""
    tir = nouvelleEntite('tir', [position[0] + ALIEN_LARGEUR // 2, position[1] + ALIEN_HAUTEUR // 2],
                         rect=pygame.Rect(position, (LARGEUR_BALLE, HAUTEUR_BALLE)), vitesse=[0, -VITESSE_BALLE],
                         couleur=VERT)
    ajouteEntite(scene, tir)
    joue_son('TIR ALIEN')


def detecte_touche_aliens(tirs_joueur, aliens):
    """Detection de collision tirs_joueur / aliens"""
    global chrono, score
    for tir in acteurs(tirs_joueur):
        for alien in acteurs(aliens):
            if rectangle(alien) != None:
                if rectangle(alien).colliderect(tir['rect']) == 1:
                    chrono += 1
                    if chrono > 20:
                        enleveEntite(aliens, alien)
                        enleveEntite(tirs_joueur, tir)
                        chrono = 0
                        score += 100


def detecte_touche_canon(tirs_aliens, canon):
    """Dection de collision tirs_aliens / canon"""
    global chrono, score, sante, shield
    for tir in acteurs(tirs_aliens):
        if rectangle(canon).colliderect(tir['rect']) == 1:
            chrono += 1
            if chrono > 20:
                enleveEntite(tirs_alien, tir)
                if shield > 0:
                    shield -= 7.5
                    if shield < 0:
                        sante += shield
                        shield = 0
                else:
                    sante -= 5
                score -= 50
                chrono = 0


def detecte_touche_powerups(powerups, canon):
    """Detection de collision canon / powerup"""
    global chrono, sante, shield, score, canon_deplacement
    for powerup in acteurs(powerups):
        if rectangle(canon).colliderect(rectangle(powerup)) == 1:
            chrono += 1
            if chrono > 20:
                enleveEntite(powerups, powerup)
                if powerup['power'] == 'SHIELD':
                    shield += 25
                    if shield > 100:
                        shield = 100
                elif powerup['power'] == 'VIE':
                    sante += 10
                    if sante > 100:
                        sante = 100
                elif powerup['power'] == 'BOOST_VITESSE':
                    canon_deplacement += 1
                score += 20
                chrono = 0
                joue_son('POWERUP')


def deplace(entite):
    dt = (maintenant - entite['momentDeplacement']) / 1000
    # mise à jour vitesse
    entite['vitesse'][0] += entite['acceleration'][0] * dt
    entite['vitesse'][1] += entite['acceleration'][1] * dt
    # mise à jour position
    entite['position'][0] += entite['vitesse'][0] * dt
    entite['position'][1] += entite['vitesse'][1] * dt
    if entite['type'] == 'tir':
        entite['rect'].x = entite['position'][0]
        entite['rect'].y = entite['position'][1]
    # mise à jour moment de déplacement
    entite['momentDeplacement'] = maintenant


def miseAJour(scene):
    ma_scene = acteurs(scene)
    for entite in ma_scene:
        deplace(entite)
        if entite['type'] == 'tir':
            pygame.draw.rect(fenetre, entite['couleur'], entite['rect'])


def enScene(scene):
    # supprime les entitées en dehors de l'écran
    for tir in acteurs(scene):
        if tir['rect'].right > FENETRE_LARGEUR or tir['rect'].left < 0:
            enleveEntite(scene, tir)
        elif tir['rect'].bottom > FENETRE_HAUTEUR or tir['rect'].bottom < 0:
            enleveEntite(scene, tir)


def deplacer_canon(deplacement):
    canon['position'][0] += deplacement
    if canon['position'][0] >= FENETRE_LARGEUR - CANON_LARGEUR:
        canon['position'][0] = FENETRE_LARGEUR - CANON_LARGEUR
    elif canon['position'][0] <= 0:
        canon['position'][0] = 0


def gestion_direction_aliens(aliens):
    """Cette fonction gère le déplacement des aliens GAUCHE --> BAS --> DROITE --> BAS --> ..."""
    global game_over, aliens_warning
    for alien in acteurs(aliens):
        if int(alien['position'][0]) > FENETRE_LARGEUR - ALIEN_LARGEUR - 32:
            change_direction_entites(aliens, 'BAS', VITESSE_ALIEN)
        if int(alien['position'][0]) < 30:
            change_direction_entites(aliens, 'BAS', VITESSE_ALIEN)

        if int(alien['position'][1]) > (alien['rangeeAlien'] + 1) * DISTANCE_ALIEN_VERTICAL:
            if alien['derniereDirection'] == 'GAUCHE':
                change_direction_entites(aliens, 'DROITE', VITESSE_ALIEN)
                alien['derniereDirection'] = 'DROITE'
            elif alien['derniereDirection'] == 'DROITE':
                change_direction_entites(aliens, 'GAUCHE', VITESSE_ALIEN)
                alien['derniereDirection'] = 'GAUCHE'
            alien['rangeeAlien'] += 1
            alien['position'][1] = alien['rangeeAlien'] * DISTANCE_ALIEN_VERTICAL

        if int(alien['position'][1]) > (FENETRE_HAUTEUR // 10) * 6 - ALIEN_HAUTEUR:
            aliens_warning = True
        else:
            aliens_warning = False
        if int(alien['position'][1]) > (FENETRE_HAUTEUR // 10) * 8 - ALIEN_HAUTEUR:
            game_over = True
            if random.randrange(400) == 0:
                joue_musique('STOP')
                joue_musique('GAME OVER')


def tir_aleatoire_aliens(aliens):
    global dernier_tir_aliens
    if dernier_tir_aliens < maintenant - random.randrange(INTERVALLE_TIR_ALIEN, 20000):
        if acteurs(aliens):
            alien_aleatoire = random.choice(acteurs(aliens))
            nouveauTirAlien(tirs_alien, alien_aleatoire['position'])
            dernier_tir_aliens = maintenant


## POWERUPS
def nouveauPowerup(position, vitesse):
    power = random.choice(powerups_images['liste'])
    return {
        'visible': True,
        'position': position,
        'vitesse': vitesse,
        'acceleration': [0, 0],
        'momentDeplacement': pygame.time.get_ticks(),
        'power': power,
        'image': powerups_images[power],
        'type': 'powerup',
        'animé': False,
    }


def power_up_aleatoire(aliens):
    global dernier_power_up
    if dernier_power_up < maintenant - random.randrange(INTERVALLE_POWERUP, 40000):
        if acteurs(aliens):
            alien_aleatoire = random.choice(acteurs(aliens))
            powerup = nouveauPowerup([alien_aleatoire['position'][0], alien_aleatoire['position'][1]],
                                     [0, -VITESSE_BALLE])
            ajouteEntite(powerups, powerup)
            dernier_power_up = maintenant


## AFFICHAGE
def affiche(entites, ecran):
    for objet in entites:
        if objet['animé']:
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


def affiche_marquoir(score):
    marquoir = space_font.render("SCORE : {}".format(score), True, BLANC)
    fenetre.blit(marquoir, (FENETRE_LARGEUR // 15, FENETRE_HAUTEUR - 25))
    nombre_aliens_vertical = space_font.render("VAGUE : {}".format(vague), True,
                                               BLANC)
    fenetre.blit(nombre_aliens_vertical, (FENETRE_LARGEUR // 15 * 5, FENETRE_HAUTEUR - 25))


def affiche_sante(sante, shield):
    left = (FENETRE_LARGEUR // 15) * 12
    top = FENETRE_HAUTEUR - 20
    width, height = (FENETRE_LARGEUR // 15) * 2, 15

    barre = pygame.Rect(left, top - height, width, 2 * height)
    pygame.draw.rect(fenetre, GRIS_CLAIR, barre)
    barre_sante = pygame.Rect(left, top, width * (sante / SANTE_DEPART), height)
    pygame.draw.rect(fenetre, ROUGE, barre_sante)
    barre_shield = pygame.Rect(left, top - height, width * (shield / 100), height)
    pygame.draw.rect(fenetre, BLEU, barre_shield)


## Background
def affiche_background():
    """Affiche le background animé : defillement d'images depuis backgrounds[xx]"""
    if backgrounds['dernier_affichage'] < maintenant - 500:
        backgrounds['dernier_background'] += 1
        if backgrounds['dernier_background'] == 5:
            backgrounds['dernier_background'] = 1
        backgrounds['dernier_affichage'] = maintenant
    fenetre.blit(backgrounds['{}'.format(backgrounds['dernier_background'])], (0, 0))


def init_vague():
    global NBR_ALIENS_VERTICAL
    """Initialise les aliens selon la vague"""
    if NBR_ALIENS_VERTICAL < 7:
        NBR_ALIENS_VERTICAL = int(math.sqrt(2 * vague))
    for x in range(int(NBR_ALIENS_VERTICAL)):
        for i in range(NBR_ALIENS_HORIZONTAL):
            alien = nouvelleEntite('alien', [32 + i * DISTANCE_ALIEN_HORIZONTAL, x * DISTANCE_ALIEN_VERTICAL])
            alien['vitesse'][0] = VITESSE_ALIEN
            alien['rangeeAlien'] = x
            alien['colonneAlien'] = i

            ajoutePose(alien, 'ALIEN_DOWN', alien_down_image)
            ajoutePose(alien, 'ALIEN_UP', alien_up_image)
            prendsPose(alien, 'ALIEN_DOWN')
            ajouteAnimation(alien, 'deplacement', animation)
            commenceAnimation(alien, 'deplacement', 0)
            ajouteEntite(aliens, alien)


def jeu():
    global tir_auto, NBR_ALIENS_VERTICAL, game_over, sante, shield, barre_limite_couleur, delai_barre_limite, aliens_warning, VITESSE_ALIEN, vague
    # MUSIQUE
    if not acteurs(aliens):
        vague += 1
        sante += 10
        if sante > 100:
            sante = 100
        init_vague()
    fenetre.fill(NOIR)
    affiche_background()
    if aliens_warning:
        if maintenant > delai_barre_limite + 500:
            delai_barre_limite = maintenant
            if barre_limite_couleur == ROUGE:
                barre_limite_couleur = BLANC
            else:
                barre_limite_couleur = ROUGE
    else:
        barre_limite_couleur = BLANC
    pygame.draw.rect(fenetre, barre_limite_couleur, barre_limite)
    pygame.draw.rect(fenetre, BLANC, border_left)
    pygame.draw.rect(fenetre, BLANC, border_right)

    affiche_marquoir(score)
    affiche_sante(sante, shield)
    anime(animation)
    dessine(canon, fenetre)
    if sante <= 0:
        game_over = True
        if random.randrange(20) == 0:
            joue_musique('STOP')
            joue_musique('GAME OVER')
    if tir_auto:
        nouveauTirJoueur(tirs_joueur, canon, CANON_LARGEUR // 2)
    if acteurs(aliens):
        miseAJour(tirs_joueur)
        miseAJour(tirs_alien)
        miseAJour(powerups)
        gestion_direction_aliens(aliens)
        miseAJour(aliens)
        tir_aleatoire_aliens(aliens)
        power_up_aleatoire(aliens)
        detecte_touche_aliens(tirs_joueur, aliens)
        detecte_touche_canon(tirs_alien, canon)
        detecte_touche_powerups(powerups, canon)
        enScene(tirs_joueur)
        enScene(tirs_alien)
        affiche(acteurs(aliens), fenetre)
        affiche(acteurs(powerups), fenetre)

    temps.tick(60)


def joue_musique(type):
    """Joue une musique"""
    global musique, musique_switch
    if type == 'JEU':
        if not musique.get_busy() and musique_switch:
            print("pass")
            aleatoire = random.randrange(32)
            chemin = "assets/musics/game/bgm_{}.ogg".format(aleatoire)
            a = pygame.mixer.Sound(chemin)
            musique.play(a, loops=-1)
    elif type == 'GAME OVER':
        if musique.get_busy():
            musique.stop()
        a = pygame.mixer.Sound("assets/musics/avengers.wav")
        musique.play(a)
    elif type == 'STOP':
        musique.fadeout(3000)
    else:
        raise Exception('else atteint dans def joue_musique(), {} reçu'.format(type))


def joue_son(type):
    """Joue un son"""
    global son, son2
    if type == 'TIR':
        son.stop()
        son.play(effects['tir'])
    elif type == 'TIR ALIEN':
        son2.stop()
        son2.play(effects['tir_alien'])
    elif type == 'POWERUP':
        son.stop()
        son.play(effects['powerup'])
    else:
        raise Exception('else atteint dans def joue_musique(), {} reçu'.format(type))


def pause():
    """Menu de pause"""
    titre_pause = space_font_grand.render("PAUSE", True, BLANC)
    sous_titre_pause = space_font.render("Appuyez sur n'importe quelle touche pour continuer.", True, GRIS_CLAIR)
    position_titre_pause = (FENETRE_LARGEUR // 2 - space_font_grand.size("PAUSE")[0] // 2,
                            FENETRE_HAUTEUR // 2 - space_font_grand.size("PAUSE")[1])
    position_sous_titre_pause = (
        FENETRE_LARGEUR // 2 - space_font.size("Appuyez sur n'importe quelle touche pour continuer.")[0] // 2,
        position_titre_pause[1] + 100)
    fenetre.blit(titre_pause, position_titre_pause)
    fenetre.blit(sous_titre_pause, position_sous_titre_pause)
    for entite in acteurs(aliens):
        entite['momentDeplacement'] = maintenant
    for entite in acteurs(tirs_joueur):
        entite['momentDeplacement'] = maintenant
    for entite in acteurs(tirs_alien):
        entite['momentDeplacement'] = maintenant
    temps.tick(5)


def game_over_screen():
    """Game over screen"""
    titre_game_over = space_font_grand.render("GAME OVER", True, BLANC)
    position_titre_game_over = (FENETRE_LARGEUR // 2 - space_font_grand.size("GAME OVER")[0] // 2,
                                FENETRE_HAUTEUR // 2 - space_font_grand.size("GAME OVER")[1])
    fenetre.blit(titre_game_over, position_titre_game_over)
    temps.tick(5)


def decor_menu(position_titre_principal):
    decor = nouvelleScene()
    # ALIEN GAUCHE
    position_alien1 = [position_titre_principal[0] - ALIEN_LARGEUR - 40, position_titre_principal[1] - 5]
    alien1 = nouvelleEntite('alien', position=position_alien1)
    ajoutePose(alien1, 'ALIEN_DOWN', alien_down_image)
    ajoutePose(alien1, 'ALIEN_UP', alien_up_image)
    ajouteAnimation(alien1, 'deplacement', animation)
    commenceAnimation(alien1, 'deplacement', 0)
    ajouteEntite(decor, alien1)
    # ALIEN DROIT
    position_alien2 = [position_titre_principal[0] + space_font_grand.size("SPACE INVADERS")[0] + 40,
                       position_titre_principal[1] - 5]
    alien2 = nouvelleEntite('alien', position=position_alien2)
    ajoutePose(alien2, 'ALIEN_DOWN', alien_down_image)
    ajoutePose(alien2, 'ALIEN_UP', alien_up_image)
    ajouteAnimation(alien2, 'deplacement', animation)
    commenceAnimation(alien2, 'deplacement', 0)
    ajouteEntite(decor, alien2)

    anime(animation)
    miseAJour(decor)
    affiche(acteurs(decor), fenetre)


def montre_commandes_menu():
    fenetre.fill(NOIR)
    affiche_background()
    background = pygame.Rect(FENETRE_LARGEUR // 10, FENETRE_HAUTEUR // 10, (FENETRE_LARGEUR // 10) * 8,
                             (FENETRE_HAUTEUR // 10) * 8)
    pygame.draw.rect(fenetre, GRIS_CLAIR, background)
    titre = space_font_grand.render("Commandes :", True, NOIR)
    fenetre.blit(titre,
                 (FENETRE_LARGEUR // 2 - space_font_grand.size("Commandes :")[0] // 2, (FENETRE_HAUTEUR // 10) * 2))
    # ESPACE
    fenetre.blit(touches['espace'], ((FENETRE_LARGEUR // 10) * 1.5, (FENETRE_HAUTEUR // 10) * 4))
    tir = space_font.render("tir", True, NOIR)
    fenetre.blit(tir, ((FENETRE_LARGEUR // 10) * 4, (FENETRE_HAUTEUR // 10) * 4 + 25))
    # FLECHES
    fenetre.blit(touches['fleche_gauche'], ((FENETRE_LARGEUR // 10) * 1.5, (FENETRE_HAUTEUR // 10) * 5.5))
    fenetre.blit(touches['fleche_droite'], ((FENETRE_LARGEUR // 10) * 2.2, (FENETRE_HAUTEUR // 10) * 5.5))
    deplacement = space_font.render("deplacement", True, NOIR)
    fenetre.blit(deplacement, ((FENETRE_LARGEUR // 10) * 4, (FENETRE_HAUTEUR // 10) * 5.5 + 25))
    # A
    fenetre.blit(touches['a'], ((FENETRE_LARGEUR // 10) * 1.5, (FENETRE_HAUTEUR // 10) * 7))
    tir_auto = space_font.render("tir automatique", True, NOIR)
    fenetre.blit(tir_auto, ((FENETRE_LARGEUR // 10) * 4, (FENETRE_HAUTEUR // 10) * 7 + 25))
    temps.tick(5)


def menu():
    fenetre.fill(NOIR)
    affiche_background()
    ##TITRES
    titre_principal = space_font_grand.render("SPACE INVADERS", True, BLANC)
    titre_start = space_font.render("Appuyez sur n'importe quelle touche pour commencer.", True, GRIS_CLAIR)
    titre_montre_commandes = space_font.render("Appuyez sur TAB pour voir les commandes.", True, GRIS_CLAIR)
    position_titre_principal = (FENETRE_LARGEUR // 2 - space_font_grand.size("SPACE INVADERS")[0] // 2, 150)
    position_titre_start = (
        FENETRE_LARGEUR // 2 - space_font.size("Appuyez sur n'importe quelle touche pour continuer.")[0] // 2, 250)
    position_titre_montre_commandes = (
        FENETRE_LARGEUR // 2 - space_font.size("Appuyez sur TAB pour voir les commandes.")[0] // 2, 300)
    fenetre.blit(titre_principal, position_titre_principal)
    fenetre.blit(titre_start, position_titre_start)
    fenetre.blit(titre_montre_commandes, position_titre_montre_commandes)

    # ANIMATION ALIEN
    decor_menu(position_titre_principal)
    temps.tick(5)


# TRAITEMENT ENTREES
def traite_entrees():
    global fini, en_jeu, en_pause, tir_auto, game_over, NBR_ALIENS_VERTICAL, montre_commandes, sante, shield, musique_switch, vague
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            fini = True
        elif evenement.type == pygame.KEYDOWN:
            if en_pause:
                if evenement.key:
                    en_pause = not en_pause
            elif en_jeu and not en_pause:
                if evenement.key == pygame.K_a:
                    tir_auto = not tir_auto
                elif evenement.key == pygame.K_ESCAPE:
                    en_pause = True
                elif evenement.key == pygame.K_SPACE:
                    nouveauTirJoueur(tirs_joueur, canon, CANON_LARGEUR // 2)
                elif evenement.key == pygame.K_m:
                    musique_switch = not musique_switch
                    joue_musique('STOP')
            else:
                if evenement.key == pygame.K_TAB:
                    montre_commandes = not montre_commandes
                else:
                    en_jeu = True
                    joue_musique('JEU')
            if game_over:
                game_over = False
                en_jeu = False
                NBR_ALIENS_VERTICAL = 0
                for alien in acteurs(aliens):
                    enleveEntite(aliens, alien)
                for tir in acteurs(tirs_alien):
                    enleveEntite(tirs_alien, tir)
                for tir in acteurs(tirs_joueur):
                    enleveEntite(tirs_joueur, tir)
                joue_musique('STOP')
                sante = 100
                shield = 0
                vague = 0
        elif evenement.type == pygame.KEYPRESSED:
            if en_jeu:
                if evenement.key == pygame.K_LEFT:
                    deplacer_canon(-canon_deplacement)
                elif evenement.key == pygame.K_RIGHT:
                    deplacer_canon(canon_deplacement)
                elif evenement.key == pygame.K_SPACE:
                    nouveauTirJoueur(tirs_joueur, canon, CANON_LARGEUR // 2)


pygame.init()
random.seed()
pygame.mixer.init()
musique = pygame.mixer.Channel(1)

# INITIALISATION CLAVIER
gc = nouvelleGestionClavier()
repeteTouche(gc, pygame.K_SPACE, 100, 25)
repeteTouche(gc, pygame.K_RIGHT, 100, 25)
repeteTouche(gc, pygame.K_LEFT, 100, 25)

# INITIALISATION DES VARIABLES GLOBALES
chrono = 0
score = 0
sante = SANTE_DEPART
shield = 0
dernier_tir_aliens = 0
game_over = False
en_jeu = False
en_pause = False
fin_vague = True
tir_auto = False
musique_switch = True
montre_commandes = False
barre_limite_couleur = BLANC
delai_barre_limite = 0
aliens_warning = False
dernier_power_up = 0
vague = 0

# CREATION FENETRE
fenetre_taille = (FENETRE_LARGEUR, FENETRE_HAUTEUR)
fenetre = pygame.display.set_mode(fenetre_taille)
pygame.display.set_caption('SPACE INVADERS')

# SONS
son = pygame.mixer.Channel(2)
son2 = pygame.mixer.Channel(3)
effects = {
    'tir_alien': pygame.mixer.Sound('assets/sounds/tir_alien.wav'),
    'tir': pygame.mixer.Sound('assets/sounds/tir.wav'),
    'powerup': pygame.mixer.Sound('assets/sounds/powerup.wav'),
}

# BACKGROUND
backgrounds = {
    'dernier_background': 1,
    'dernier_affichage': pygame.time.get_ticks(),
}
for nom_image, nom_fichier, LARGEUR, HAUTEUR in (
        ('1', 'frame-1.gif', FENETRE_LARGEUR, FENETRE_HAUTEUR),
        ('2', 'frame-2.gif', FENETRE_LARGEUR, FENETRE_HAUTEUR),
        ('3', 'frame-3.gif', FENETRE_LARGEUR, FENETRE_HAUTEUR),
        ('4', 'frame-4.gif', FENETRE_LARGEUR, FENETRE_HAUTEUR),
):
    chemin = 'assets/background/' + nom_fichier
    image = pygame.image.load(chemin).convert_alpha(fenetre)
    image = pygame.transform.scale(image, (LARGEUR, HAUTEUR))
    backgrounds[nom_image] = image

# COMMON
pygame.font.init()
space_font = pygame.font.Font('assets/fonts/space_invaders.ttf', 18)
space_font_grand = pygame.font.Font('assets/fonts/space_invaders.ttf', 48)
touche_fleche = pygame.image.load('assets/touche_fleche_droit.png').convert_alpha(fenetre)
# INITIALISATION DES IMAGES TOUCHES , utilisation : touches['a']
touches = {}
for nom_image, nom_fichier, LARGEUR, HAUTEUR in (
        ('fleche_droite', 'touche_fleche_droit.png', TOUCHE_LARGEUR, TOUCHE_HAUTEUR),
        ('fleche_gauche', 'touche_fleche_gauche.png', TOUCHE_LARGEUR, TOUCHE_HAUTEUR),
        ('a', 'touche_a.png', TOUCHE_LARGEUR, TOUCHE_HAUTEUR),
        ('espace', 'touche_espace.png', 128, TOUCHE_HAUTEUR),
):
    chemin = 'assets/' + nom_fichier
    image = pygame.image.load(chemin).convert_alpha(fenetre)
    image = pygame.transform.scale(image, (LARGEUR, HAUTEUR))
    touches[nom_image] = image
# INITIALISATION DES IMAGES, utilisation : touches['powerup']
powerups_images = {
    'liste': [],
}
for nom_image, nom_fichier, LARGEUR, HAUTEUR in (
        ('VIE', 'powerup_vie.png', 32, 32),
        ('SHIELD', 'powerup_shield.png', 32, 32),
        ('BOOST_VITESSE', 'powerup_boost.png', 32, 32)
):
    chemin = 'assets/powerups/' + nom_fichier
    image = pygame.image.load(chemin).convert_alpha(fenetre)
    image = pygame.transform.scale(image, (LARGEUR, HAUTEUR))
    powerups_images[nom_image] = image
    powerups_images['liste'].append(nom_image)
# CANON
canon_image = pygame.image.load('assets/laser_canon.webp').convert_alpha(fenetre)
canon_image = pygame.transform.scale(canon_image, (CANON_LARGEUR, CANON_HAUTEUR))
canon = nouvelleEntite('canon', [(FENETRE_LARGEUR - CANON_LARGEUR) // 2, CANON_Y])
canon['image'] = canon_image

# SCENES DE TIRS
tirs_joueur = nouvelleScene()
tirs_alien = nouvelleScene()
powerups = nouvelleScene()

# ZONE DE JEU
border_left = pygame.Rect(0, 0, 32, FENETRE_HAUTEUR)
border_right = pygame.Rect(FENETRE_LARGEUR - 32, 0, 32, FENETRE_HAUTEUR)
barre_limite = pygame.Rect(0, (FENETRE_HAUTEUR // 10) * 8, FENETRE_LARGEUR, 5)

# INITIALIASATION ALIENS
aliens = nouvelleScene()
alien_up_image = pygame.image.load('assets/alien-up.png').convert_alpha(fenetre)
alien_up_image = pygame.transform.scale(alien_up_image, (ALIEN_LARGEUR, ALIEN_HAUTEUR))
alien_down_image = pygame.image.load('assets/alien-down.png').convert_alpha(fenetre)
alien_down_image = pygame.transform.scale(alien_down_image, (ALIEN_LARGEUR, ALIEN_HAUTEUR))

# ANIMATION POUR LES ALIENS
animation = nouvelleAnimation()
ajouteMouvement(animation, mouvement('ALIEN_UP', INTERVALLE_DEPLACEMENT_ALIEN))
ajouteMouvement(animation, mouvement('ALIEN_DOWN', INTERVALLE_DEPLACEMENT_ALIEN))

fini = False
temps = pygame.time.Clock()

dernier = 1
compteur = -1000

while not fini:
    maintenant = pygame.time.get_ticks()
    scan(gc)
    traite_entrees()  # --- Traite entrees joueurs
    # GESTION DISPLAY ICON
    if compteur < maintenant - 1000:
        if dernier == 1:
            pygame.display.set_icon(alien_down_image)
            dernier = 0
        else:
            pygame.display.set_icon(alien_up_image)
            dernier = 1
        compteur = maintenant

    if en_jeu and en_pause:
        pause()
    elif en_jeu and game_over:
        game_over_screen()
    elif en_jeu and not en_pause:
        jeu()
    if not en_jeu and montre_commandes:
        montre_commandes_menu()
    elif not en_jeu:
        menu()

    pygame.display.flip()

pygame.display.quit()
pygame.quit()
exit()
