import numpy as np
import random
import pygame
import math
import sys

#
#   INICIALITZACIO DE VARIABLES
#
BLACK = (0,0,0)      # Defincio del color negre
GREY = (120,120,120) # Defincio del color gris
RED = (255,0,0)      # Defincio del color vermell
YELLOW = (255,255,0) # Defincio del color groc
GREEN = (0,128,0)    # Defincio del color verd
WHITE = (255,255,255)# Defincio del color blanc
BLUE = (0,0,255)     # Defincio del color blau 
GOLD = (212,175,55)  # Defincio del color daurat

ROW_COUNT = 6        # Numero de files del tauler
COLUMN_COUNT = 13    # Numero de columnes del tauler

PLAYER = 0           # Codi del jugador huma
AI = 1               # Codi del jugador AI

EMPTY = 0            # Codi de posicio lliure
BONUS = 9            # Codi de posicio bonus

PLAYER_PIECE = 1     # Codi de posicio jugador huma
PLAYER_PAINTED = 3   # Codi de posicio cremada per huma

AI_PIECE = 2         # Codi de posicio jugador AI
AI_PAINTED = 4       # Codi de posicio cremada per AI

WINNER_PIECE = 5     # Codi de posicio guanyadora
WALL = 6             # Codi de posicio cremada no jugable

DEPH_LEVEL = 6   # Profunditat de l'arbre base.
# Important parell o imparell si volem que calculi darrer nivell a max o a min. Parell max, imparell min.
# Ens interesa el valor de max(ia) en el nivell 0, gens el de min (huma)

#
# DEFINICIO DE MODULS
#
def crear_tauler(): # Crea la matriu de mida files per columnes, que utilitzarem per identificar els estats
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board


def situa_bonus_murs(board, piece1, piece2): # Dins de la matriu del joc, situarem un espai amb bonus
    # Situa bonus en la zona entre els dos jugadors.
    # El torn d'inici aleatori, permet equilibrar la probabilitat d'arribar-hi segons distancia 
    fila = (piece1[0] + piece2[0]) // 2
    columna = (piece1[1] + piece2[1]) // 2
    board[ROW_COUNT-fila-1][columna] = BONUS
    
    # Situa de forma aleatoria murs, que te en compte una proporcio del numero de posicions totals
    murs = (COLUMN_COUNT*ROW_COUNT)//10

    # Defineix la mida en numero de caselles que formen els murs
    mida = 2

    # Situa murs, verificant que no es solapen entre ells, no xafen altres fitxes o la casella bonus
    for c in range(murs):
        colisio = True # Evita que el mur creui altres estructures o bonus
        while colisio == True: # Vaig fent proves de per colocar murs, i si evito colisio, el consolido
            # Direccio del mur (1 horitzontal, 0 vertical)
            direccio = random.choice([1, 0])
            fila, columna = random.randint(0, ROW_COUNT-1), random.randint(0, COLUMN_COUNT-1)
            colisio = False # Inicializa la variable d aturada per colisio

            # Valors hipotetica colissio
            if (direccio == 0 and ROW_COUNT-fila + mida >= ROW_COUNT) or (direccio == 1 and columna + mida >= COLUMN_COUNT):
                colisio = True # Mostra colisio en la projeccio si supera les mides del tauler
            else:
                # Prova de situar el mur, per valorar si en algun punt hi ha un solapament amb altres elements del tauler
                for i in range(mida):
                    if direccio == 1:
                        if board[ROW_COUNT-fila-1][columna+i] != EMPTY:
                            colisio = True
                    else:
                        if board[ROW_COUNT-fila+i-1][columna] != EMPTY:
                            colisio = True

        for i in range(mida): # En cas de no colisio, consolida el mur en el tauler
            if direccio == 1:
                board[ROW_COUNT-fila-1][columna+i] = WALL
            else:
                board[ROW_COUNT-fila+i-1][columna] = WALL
    return board


def moure_fitxa(board, row, col, piece):  # Segons l estat i el moviment, assigna el seguent estat
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == piece: # Segons la fitxa moguda, s'assigna valor al tauler
                if piece == PLAYER_PIECE:
                    board[r][c] = PLAYER_PAINTED
                elif piece == PLAYER_PAINTED:
                    board[r][c] = PLAYER_PIECE
                elif piece == AI_PIECE:
                    board[r][c] = AI_PAINTED
                elif piece == AI_PAINTED:
                    board[r][c] = AI_PIECE
    board[row][col] = piece


def mostra_tauler(board): # Mostra el tauler per consola
    print(np.flip(board, 0))


def jugada_guanyadora(board, player): # Avalua algunes de les condiciona d'aturada de la partida
    winning = False

    if  (player == PLAYER_PIECE): # Segon jugador, si jugador contrari ofegat, guanya jugador actual
        if len(recupera_posicions_lliures_jugador(board, AI_PIECE)) == 0:
            winning = True
    elif len(recupera_posicions_lliures_jugador(board, PLAYER_PIECE)) == 0:
            winning = True    
    return winning


def es_node_terminal(board): # Avalua node fulla
    return jugada_guanyadora(board, PLAYER_PIECE) or jugada_guanyadora(board, AI_PIECE)


def es_posicio_lliure(board, row, col, player): # Avalua si es posicio jugable, tenint en compte qui juga
    valid = 0
    if ((board[row][col] == EMPTY) or ((board[row][col] == BONUS))) and (((row < ROW_COUNT-1) and (board[row+1][col] == player)) or ((row > 0) and (board[row-1][col] == player))): # Posicio lliure i jugador en la mateixa columna, fila anterior o posterior
        valid = 1
    elif ((board[row][col] == EMPTY) or ((board[row][col] == BONUS))) and (((col < COLUMN_COUNT-1) and (board[row][col+1] == player)) or ((col > 0) and (board[row][col-1] == player))): # Posicio lliure i jugador en la mateixa fila, columna anterior o posterior
        valid = 1
    return valid


def recupera_posicions_lliures_jugador(board, player): # Prepar una matriu amb les posicions lliures d un jugador
    posicions_lliures_jugador = []
    row = col = 0
    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            if es_posicio_lliure(board, row, col, player) == True:
                posicions_lliures_jugador.append([row, col])
    return posicions_lliures_jugador


def avalua_estat(board, piece): # Modul MOLT IMPORTANT en el qual cal programar la inteligencia del joc
    # Cal reprogramar aquest modul, per avaluar quan de bo es un tauler respecte als demes.
    # Us deixo un funcio d exemple, amb valors per defecte.
    value = score = 0
    return score # Retorna puntuacio de l'estat


def minimax(board, depth, alpha, beta, maximizingPlayer):
    # Cal reprogramar aquest modul, per avaluar cada jugada.
    # Us deixo un funcio d exemple, pero l'heu de modificar/millorar.
    # Utilitza crides recursives fins jugada_guanyadora, o no recupera_posicions_valides
    # Retorna l'avaluacio (MAX o MIN) segons jugador, o avaluacio segons heuristica
    if maximizingPlayer:
        posicions_valides = recupera_posicions_lliures_jugador(board, AI_PIECE)
    else:
        posicions_valides = recupera_posicions_lliures_jugador(board, PLAYER_PIECE)

    es_terminal = es_node_terminal(board) # Comprova si hi ha alguna jugada no guanyadora possible
    if depth == 0 or es_terminal: # La profunditat es decreixent, comenca a #DEPTH i resta un nivell fins a zero
        if es_terminal: 
            if jugada_guanyadora(board, AI_PIECE):
                return (None, None, 0) # Cal modificar els parametres assignats per defecte
            elif jugada_guanyadora(board, PLAYER_PIECE):
                return (None, None, 0) # Cal modificar els parametres assignats per defecte
        else: # Maxim nivell de produnditat, no terminal
            if maximizingPlayer:
                new_score = avalua_estat(board, AI_PIECE)
            else:
                new_score = -avalua_estat(board, PLAYER_PIECE) # Atencio amb el signe d aquest retorn del modul
            return (None, None, new_score)
    
    if maximizingPlayer:
        value = float('-inf')

        for pos in posicions_valides: # Recorre totes les posicions valides
            b_copy = board.copy()     # Prepara nou tauler
            moure_fitxa(b_copy, pos[0], pos[1], AI_PIECE)   # Mou a nova posicio valida, dins del nou tauler
            temp = minimax(b_copy, depth-1, alpha, beta, False)
            new_score = temp[2]
            if new_score > value:
                value = new_score
                position = pos

        return position[0], position[1], value
    else:
        value = float('inf')
        position = random.choice(posicions_valides) # Tria una posicio valida com inicialitzacio
        for pos in posicions_valides:
            b_copy = board.copy()

            moure_fitxa(b_copy, pos[0], pos[1], PLAYER_PIECE)
            temp = minimax(b_copy, depth-1, alpha, beta, True) # Recupera nomes valor minimax
            new_score = temp[2]
            if new_score < value:
                value = new_score
                position = pos
    
        return position[0], position[1], value


def dibuixa_tauler(board): # Dibuixa tauler via GUI
    screen.fill(BLACK)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, WHITE, (c*SQUARESIZE, r*SQUARESIZE, SQUARESIZE-2, SQUARESIZE),1) # Superposem la graella en blanc 

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS,2)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS,2)
            elif board[r][c] == PLAYER_PAINTED:
                pygame.draw.rect(screen, RED, (c*SQUARESIZE, height-(r*SQUARESIZE)-SQUARESIZE, SQUARESIZE-2, SQUARESIZE-2))
            elif board[r][c] == AI_PAINTED:
                pygame.draw.rect(screen, YELLOW, (c*SQUARESIZE, height-(r*SQUARESIZE)-SQUARESIZE, SQUARESIZE-2, SQUARESIZE-2))
            elif board[r][c] == WINNER_PIECE:
                pygame.draw.circle(screen, GREEN, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == WALL:
                pygame.draw.rect(screen, GREY, (c*SQUARESIZE, height-(r*SQUARESIZE)-SQUARESIZE, SQUARESIZE-2, SQUARESIZE-2))
            elif board[r][c] == BONUS: 
                pygame.draw.rect(screen, GOLD, (c*SQUARESIZE, height-(r*SQUARESIZE)-SQUARESIZE, SQUARESIZE-2, SQUARESIZE-2))
    pygame.display.update()


def qui_guanya(winner):
    if winner == PLAYER_PIECE:
        label = myfont.render("Guanya huma!", 1, BLUE)
    elif winner == AI_PIECE:
        label = myfont.render("Guanya IA!", 1, BLUE)
    screen.blit(label, (50, 10))
    pygame.display.update()
    return winner


"""
********************************
*  JOC LA CACERA DEL TRESOR    *
********************************
"""
board = crear_tauler() # Crea tauler de joc
game_over = False

pygame.init()
SQUARESIZE = 100 # Quadrats de 100 pixels quadrats
width = COLUMN_COUNT * SQUARESIZE
height = ROW_COUNT * SQUARESIZE
size = (width, height) # Calcula la mida del tauler
RADIUS = int(SQUARESIZE/2 - 5) # Radi fitxa
myfont = pygame.font.SysFont("monospace", 75)

# Cal reprogramar qui obte el torn inicial
turn = PLAYER # Inicialment, obliga a comencar a jugador huma

# Cal reprogramar la situacio inicial de les fitxes
# Les posicions assignades han de ser aleatories i exclussives (NO han de coincidir en la mateixa posicio)
start_player = [0,0]
moure_fitxa(board, start_player[0], start_player[1], PLAYER_PIECE) # Posiciona fitxa humana
start_ai = [5,12]
moure_fitxa(board, start_ai[0], start_ai[1], AI_PIECE) # Posiciona fitxa IA

board = situa_bonus_murs(board,start_player,start_ai) # Un cop situades fitxes, es poden situar bonus i cremades

screen = pygame.display.set_mode(size)
size = (width, height) # Calcula la mida del tauler

mostra_tauler(board)
dibuixa_tauler(board)
pygame.display.update()

while not game_over: # Mentre hi ha partida
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if turn == PLAYER:      # Espera la jugada humana
                posx = event.pos[0] # Recupera la posicio (columna) clicada
                posy = event.pos[1] # Recupera la posicio (fila) clicada

                row = int(math.floor((ROW_COUNT*SQUARESIZE-posy)/SQUARESIZE)) # Cal invertir el calcul de la posicio de l eix de les Y
                col = int(math.floor(posx/SQUARESIZE))
                
                if es_posicio_lliure(board, row, col, PLAYER_PIECE):
                    moure_fitxa(board, row, col, PLAYER_PIECE)

                    if jugada_guanyadora(board, PLAYER_PIECE):
                        moure_fitxa(board, row, col, WINNER_PIECE)
                        dibuixa_tauler(board)
                        qui_guanya(PLAYER_PIECE)
                        game_over = True
                    else:
                        dibuixa_tauler(board)
                    turn += 1
                    turn = turn % 2

    if turn == AI and not game_over: # Espera la jugada d'IA
        row, col, minimax_score = minimax(board, DEPH_LEVEL, 0, 0, True) # Ull amb aquests zeros d inicialitzacio del minimax
        pygame.time.wait(500)
        if row == None: # Si huma no disposa de jugada possible
            qui_guanya(AI_PIECE)
            game_over = True
        else:
            moure_fitxa(board, row, col, AI_PIECE) # Si huma te jugada possible
            if jugada_guanyadora(board, AI_PIECE):
                moure_fitxa(board, row, col, WINNER_PIECE)
                dibuixa_tauler(board)
                qui_guanya(AI_PIECE)
                game_over = True
            else:
                dibuixa_tauler(board)
            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)