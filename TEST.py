import random
import os

# =====================================================================
#   SOPA DE LETRAS - PROYECTO FINAL
#   Curso: SOFT-01 Principios de Programacion
#   Universidad CENFOTEC
# =====================================================================

# ── Constantes globales ───────────────────────────────────────────────
CARPETA          = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_PALABRAS = os.path.join(CARPETA, "palabras.txt")
ARCHIVO_PUNTAJES = os.path.join(CARPETA, "puntajes.txt")
LETRAS_ABECEDARIO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Colores para la consola (codigos ANSI)
AZUL       = "\033[34m"   # tabla y bordes
VERDE      = "\033[92m"   # palabras encontradas con [ ]
AMARILLO   = "\033[93m"   # numeros de fila y columna
RESET      = "\033[0m"    # volver al color normal
MAX_PISTAS  = 3
MAX_RANKING = 10

# Puntos segun complejidad
PUNTOS_A = 2
PUNTOS_B = 3
PUNTOS_C = 5

# Penalizacion segun cantidad de pistas usadas
PENAL_1_PISTA  = 2
PENAL_2_PISTAS = 4
PENAL_3_PISTAS = 5

# Direcciones posibles dentro de la matriz (fila, columna)
# Horizontal derecha, horizontal izquierda, vertical abajo,
# vertical arriba, diagonales (puntos extra)
DIRECCIONES_F = [0,  0,  1, -1,  1,  1, -1, -1]
DIRECCIONES_C = [1, -1,  0,  0,  1, -1,  1, -1]


# =====================================================================
#   FUNCIONES DE ARCHIVO
# =====================================================================

def cargar_palabras():
    # Lee las palabras guardadas en el archivo y las retorna en una lista
    # Cada elemento de la lista es otra lista: [palabra, complejidad]
    # Retorna lista vacia si el archivo no existe todavia
    lista_palabras = []
    try:
        archivo = open(ARCHIVO_PALABRAS, "r", encoding="utf-8")
        for linea in archivo:
            linea = linea.strip()
            if linea != "":
                partes = linea.split(",")
                if len(partes) == 2:
                    palabra     = partes[0].strip().upper()
                    complejidad = partes[1].strip().upper()
                    # Solo agregar si tiene al menos 3 letras y complejidad valida
                    if len(palabra) >= 3 and (complejidad == "A" or complejidad == "B" or complejidad == "C"):
                        lista_palabras.append([palabra, complejidad])
        archivo.close()
    except FileNotFoundError:
        pass  # Si el archivo no existe, retornamos lista vacia
    except Exception:
        print("Error al leer el archivo de palabras.")
    return lista_palabras


def guardar_palabras(lista_palabras):
    # Recibe la lista de palabras que armo configurar_juego()
    # y la escribe en el archivo palabras.txt linea por linea
    try:
        archivo = open(ARCHIVO_PALABRAS, "w", encoding="utf-8")
        indice = 0
        while indice < len(lista_palabras):
            archivo.write(lista_palabras[indice][0] + "," + lista_palabras[indice][1] + "\n")
            indice = indice + 1
        archivo.close()
    except Exception:
        print("Error al guardar las palabras.")


def cargar_puntajes():
    # Lee el archivo de puntajes y retorna una lista de listas [nombre, puntaje]
    # Es llamada por main() al iniciar y antes de cada partida
    lista_puntajes = []
    try:
        archivo = open(ARCHIVO_PUNTAJES, "r", encoding="utf-8")
        for linea in archivo:
            linea = linea.strip()
            if linea != "":
                partes = linea.split(",")
                if len(partes) == 2:
                    nombre       = partes[0].strip()
                    puntaje_texto = partes[1].strip()
                    # Validar que el puntaje sea numero sin usar try/except
                    es_numero = True
                    if puntaje_texto == "":
                        es_numero = False
                    else:
                        indice = 0
                        while indice < len(puntaje_texto):
                            if not puntaje_texto[indice].isdigit():
                                es_numero = False
                            indice = indice + 1
                    if nombre != "" and es_numero:
                        lista_puntajes.append([nombre, int(puntaje_texto)])
        archivo.close()
    except FileNotFoundError:
        pass
    except Exception:
        print("Error al leer el archivo de puntajes.")
    return lista_puntajes


def guardar_puntajes(lista_puntajes):
    # Recibe la lista de puntajes actualizada desde finalizar_juego()
    # y la escribe en el archivo puntajes.txt
    try:
        archivo = open(ARCHIVO_PUNTAJES, "w", encoding="utf-8")
        indice = 0
        while indice < len(lista_puntajes):
            archivo.write(lista_puntajes[indice][0] + "," + str(lista_puntajes[indice][1]) + "\n")
            indice = indice + 1
        archivo.close()
    except Exception:
        print("Error al guardar los puntajes.")


# =====================================================================
#   FUNCIONES DE VALIDACION
# =====================================================================

def validar_palabra(palabra):
    if palabra == "" or len(palabra) == 0:
        return False
    if len(palabra) < 3:
        return False
    indice = 0
    while indice < len(palabra):
        if palabra[indice].isdigit():
            return False
        indice = indice + 1
    if " " in palabra:
        return False
    return True


def leer_numero_entero(mensaje):
    # Pide un numero entero al usuario y lo valida sin usar try/except
    # Repite la pregunta hasta recibir un numero valido
    # El parametro 'mensaje' es el texto que se le muestra al usuario
    entrada = input(mensaje).strip()
    es_valido = False
    while not es_valido:
        if entrada == "":
            entrada = input("Error: ingrese un numero entero. " + mensaje).strip()
            continue
        # Verificar caracter por caracter que todos sean digitos
        solo_digitos = True
        indice = 0
        while indice < len(entrada):
            if not entrada[indice].isdigit():
                solo_digitos = False
            indice = indice + 1
        if solo_digitos:
            es_valido = True
        else:
            entrada = input("Error: debe ingresar un numero entero. " + mensaje).strip()
    return int(entrada)


def obtener_puntos(complejidad):
    # Recibe la complejidad de una palabra (A, B o C)
    # y retorna cuantos puntos vale segun las constantes
    if complejidad == "A":
        return PUNTOS_A
    elif complejidad == "B":
        return PUNTOS_B
    else:
        return PUNTOS_C


def obtener_penalizacion(cantidad_pistas_usadas):
    # Recibe cuantas pistas uso el jugador (viene de jugar())
    # y retorna la penalizacion acumulada en puntos
    if cantidad_pistas_usadas == 1:
        return PENAL_1_PISTA
    elif cantidad_pistas_usadas == 2:
        return PENAL_2_PISTAS
    elif cantidad_pistas_usadas >= 3:
        return PENAL_3_PISTAS
    else:
        return 0


# =====================================================================
#   FUNCIONES DE MATRIZ
# =====================================================================

def crear_matriz_vacia(tamano):
    # Crea una matriz cuadrada de tamano x tamano llena de puntos "."
    # Los puntos indican celdas libres que luego se rellenan
    # Es llamada desde generar_matriz()
    matriz = []
    fila_actual = 0
    while fila_actual < tamano:
        fila = []
        col_actual = 0
        while col_actual < tamano:
            fila.append(".")
            col_actual = col_actual + 1
        matriz.append(fila)
        fila_actual = fila_actual + 1
    return matriz


def calcular_tamano(lista_palabras):
    # Calcula el tamano minimo de la matriz para que quepan todas las palabras
    # Recibe la lista de palabras que viene de cargar_palabras()
    longitud_maxima = 0
    indice = 0
    while indice < len(lista_palabras):
        if len(lista_palabras[indice][0]) > longitud_maxima:
            longitud_maxima = len(lista_palabras[indice][0])
        indice = indice + 1
    tamano = longitud_maxima + 5
    if len(lista_palabras) + 5 > tamano:
        tamano = len(lista_palabras) + 5
    if tamano < 12:
        tamano = 12
    return tamano


def puede_colocar(matriz, palabra, fila_inicio, col_inicio, dir_fila, dir_col, tamano):
    # Verifica si una palabra cabe en la posicion y direccion dadas
    # sin salir de la matriz ni pisar letras incompatibles
    # dir_fila y dir_col vienen de las listas DIRECCIONES_F y DIRECCIONES_C
    longitud_palabra = len(palabra)
    fila_fin = fila_inicio + dir_fila * (longitud_palabra - 1)
    col_fin  = col_inicio  + dir_col  * (longitud_palabra - 1)
    # Verificar que la posicion final este dentro de la matriz
    if fila_fin < 0 or fila_fin >= tamano or col_fin < 0 or col_fin >= tamano:
        return False
    # Verificar que cada celda este libre o tenga la misma letra
    indice = 0
    while indice < longitud_palabra:
        celda = matriz[fila_inicio + dir_fila * indice][col_inicio + dir_col * indice]
        if celda != "." and celda != palabra[indice]:
            return False
        indice = indice + 1
    return True


def colocar_palabra(matriz, palabra, fila_inicio, col_inicio, dir_fila, dir_col):
    # Escribe la palabra en la matriz letra por letra
    # Recibe los mismos parametros que puede_colocar() (ya validados)
    indice = 0
    while indice < len(palabra):
        matriz[fila_inicio + dir_fila * indice][col_inicio + dir_col * indice] = palabra[indice]
        indice = indice + 1


def rellenar_vacios(matriz, tamano):
    # Recorre toda la matriz y reemplaza los puntos "." con letras aleatorias
    # Es el ultimo paso dentro de generar_matriz()
    fila_actual = 0
    while fila_actual < tamano:
        col_actual = 0
        while col_actual < tamano:
            if matriz[fila_actual][col_actual] == ".":
                indice_letra = random.randint(0, 25)
                matriz[fila_actual][col_actual] = LETRAS_ABECEDARIO[indice_letra]
            col_actual = col_actual + 1
        fila_actual = fila_actual + 1


def generar_matriz(lista_palabras):
    # Genera la sopa de letras completa a partir de la lista de palabras
    # Llama internamente a: calcular_tamano, crear_matriz_vacia,
    #                       puede_colocar, colocar_palabra, rellenar_vacios
    # Retorna la matriz y sus dimensiones: matriz, filas, cols
    tamano = calcular_tamano(lista_palabras)
    matriz = crear_matriz_vacia(tamano)

    indice_palabra = 0
    while indice_palabra < len(lista_palabras):
        palabra  = lista_palabras[indice_palabra][0]
        colocada = False
        intentos = 0

        while not colocada and intentos < 500:
            # Elegir direccion y posicion aleatoria
            indice_dir = random.randint(0, 7)
            dir_fila   = DIRECCIONES_F[indice_dir]
            dir_col    = DIRECCIONES_C[indice_dir]
            fila_inicio = random.randint(0, tamano - 1)
            col_inicio  = random.randint(0, tamano - 1)

            if puede_colocar(matriz, palabra, fila_inicio, col_inicio, dir_fila, dir_col, tamano):
                colocar_palabra(matriz, palabra, fila_inicio, col_inicio, dir_fila, dir_col)
                colocada = True

            intentos = intentos + 1

        if not colocada:
            print("Advertencia: no se pudo colocar la palabra " + palabra)
        indice_palabra = indice_palabra + 1

    rellenar_vacios(matriz, tamano)
    return matriz, tamano, tamano


def buscar_palabra_en_matriz(matriz, palabra, filas, cols):
    # Busca la palabra en toda la matriz probando las 8 direcciones
    # Usada por dar_pista() para encontrar donde esta una palabra pendiente
    # Retorna [fila, col, dir_fila, dir_col] si la encuentra, o None si no
    fila_actual = 0
    while fila_actual < filas:
        col_actual = 0
        while col_actual < cols:
            indice_dir = 0
            while indice_dir < 8:
                dir_fila = DIRECCIONES_F[indice_dir]
                dir_col  = DIRECCIONES_C[indice_dir]
                # Intentar hacer coincidir la palabra desde esta posicion y direccion
                coincide = True
                indice = 0
                while indice < len(palabra):
                    fila_siguiente = fila_actual + dir_fila * indice
                    col_siguiente  = col_actual  + dir_col  * indice
                    if fila_siguiente < 0 or fila_siguiente >= filas or col_siguiente < 0 or col_siguiente >= cols:
                        coincide = False
                        break
                    if matriz[fila_siguiente][col_siguiente].upper() != palabra[indice].upper():
                        coincide = False
                        break
                    indice = indice + 1
                if coincide:
                    return [fila_actual, col_actual, dir_fila, dir_col]
                indice_dir = indice_dir + 1
            col_actual = col_actual + 1
        fila_actual = fila_actual + 1
    return None


def mostrar_matriz(tablero_display, filas, cols):
    # Muestra el tablero en consola con colores
    # tablero_display viene de jugar() (letras min/MAY) o de main() (vista previa)
    # Verde con [ ] = palabras encontradas
    # Azul           = bordes y separadores
    # Amarillo       = numeros de fila y columna
    print()
    # Encabezado con numeros de columna en amarillo
    print("      ", end="")
    col_actual = 0
    while col_actual < cols:
        if col_actual < 10:
            print(AMARILLO + " " + str(col_actual) + " " + RESET, end="")
        else:
            print(AMARILLO + str(col_actual) + " " + RESET, end="")
        col_actual = col_actual + 1
    print()
    # Linea separadora en azul
    print(AZUL + "      " + "---" * cols + RESET)

    fila_actual = 0
    while fila_actual < filas:
        # Numero de fila en amarillo, borde en azul
        if fila_actual < 10:
            print(AMARILLO + "  " + str(fila_actual) + RESET + AZUL + "  |" + RESET, end="")
        else:
            print(AMARILLO + " " + str(fila_actual) + RESET + AZUL + "  |" + RESET, end="")
        col_actual = 0
        while col_actual < cols:
            celda = tablero_display[fila_actual][col_actual]
            if celda.isupper():
                print(VERDE + "[" + celda + "]" + RESET, end="")  # encontrada: verde
            else:
                print(" " + celda + " ", end="")                  # normal: sin color
            col_actual = col_actual + 1
        print()
        fila_actual = fila_actual + 1


# =====================================================================
#   FUNCIONES DE PUNTAJE Y RANKING
# =====================================================================

def calcular_puntaje(palabras_encontradas, cantidad_pistas_usadas):
    # Suma los puntos de cada palabra encontrada y resta la penalizacion por pistas
    # palabras_encontradas viene de jugar() (se va llenando durante la partida)
    # cantidad_pistas_usadas tambien viene de jugar()
    total = 0
    indice = 0
    while indice < len(palabras_encontradas):
        # palabras_encontradas[indice][1] es la complejidad (A, B o C)
        total = total + obtener_puntos(palabras_encontradas[indice][1])
        indice = indice + 1
    total = total - obtener_penalizacion(cantidad_pistas_usadas)
    if total < 0:
        total = 0
    return total


def ordenar_ranking(lista_ranking):
    # Ordena la lista de puntajes de mayor a menor usando Bubble Sort
    # Modifica la lista directamente (no retorna nada)
    # Es llamada desde actualizar_ranking() cada vez que se agrega un jugador
    # Creo que este por ser punto extra no lleva diagrama / debo confirmar
    total_elementos = len(lista_ranking)
    i = 0
    while i < total_elementos:
        j = 0
        while j < total_elementos - i - 1:
            # lista_ranking[j][1] es el puntaje (segundo elemento de la sublista)
            if lista_ranking[j + 1][1] > lista_ranking[j][1]:
                temp                  = lista_ranking[j]
                lista_ranking[j]      = lista_ranking[j + 1]
                lista_ranking[j + 1]  = temp
            j = j + 1
        i = i + 1


def buscar_en_ranking(lista_ranking, nombre_jugador):
    # Busca al jugador por nombre en la lista del ranking
    # Retorna su posicion (1, 2, 3...) o -1 si no esta
    # Es llamada desde main() para saludar y desde actualizar_ranking()
    indice = 0
    while indice < len(lista_ranking):
        if lista_ranking[indice][0].upper() == nombre_jugador.upper():
            return indice + 1  # posicion 1-based (no desde 0)
        indice = indice + 1
    return -1


def actualizar_ranking(lista_ranking, nombre_jugador, puntaje_nuevo):
    # Agrega o actualiza al jugador en el ranking
    # lista_ranking viene de main() (o es una copia temporal en jugar())
    # Retorna la posicion del jugador, o -1 si no califico para entrar

    posicion_existente = buscar_en_ranking(lista_ranking, nombre_jugador)

    if posicion_existente != -1:
        # El jugador ya existe: actualizar solo si el puntaje es mayor
        if puntaje_nuevo > lista_ranking[posicion_existente - 1][1]:
            lista_ranking[posicion_existente - 1][1] = puntaje_nuevo
        ordenar_ranking(lista_ranking)
        while len(lista_ranking) > MAX_RANKING:
            lista_ranking.pop()
        return buscar_en_ranking(lista_ranking, nombre_jugador)

    # El jugador es nuevo
    if len(lista_ranking) < MAX_RANKING:
        lista_ranking.append([nombre_jugador, puntaje_nuevo])
        ordenar_ranking(lista_ranking)
        return buscar_en_ranking(lista_ranking, nombre_jugador)
    elif puntaje_nuevo > lista_ranking[-1][1]:
        # Supera al ultimo del ranking, lo reemplaza
        lista_ranking[-1] = [nombre_jugador, puntaje_nuevo]
        ordenar_ranking(lista_ranking)
        return buscar_en_ranking(lista_ranking, nombre_jugador)
    else:
        return -1


def puntos_para_avanzar(lista_ranking, nombre_jugador, puntaje_actual):
    # Calcula cuantos puntos le faltan al jugador para subir una posicion
    # o para entrar al ranking si no esta en el
    # lista_ranking y nombre_jugador vienen de jugar() o finalizar_juego()
    posicion = buscar_en_ranking(lista_ranking, nombre_jugador)

    if posicion == -1:
        if len(lista_ranking) < MAX_RANKING:
            return 0
        return lista_ranking[-1][1] - puntaje_actual + 1

    if posicion == 1:
        return 0  # ya es el primero

    # Puntos necesarios para superar al jugador que esta una posicion arriba
    return lista_ranking[posicion - 2][1] - puntaje_actual + 1


def mostrar_ranking(lista_ranking):
    # Muestra el top 10 en consola
    # lista_ranking viene de main() o de finalizar_juego()
    print()
    print("=" * 40)
    print("      RANKING - TOP 10 JUGADORES")
    print("=" * 40)
    if len(lista_ranking) == 0:
        print("  No hay puntajes registrados aun.")
    else:
        indice = 0
        while indice < len(lista_ranking):
            nombre  = lista_ranking[indice][0]
            puntaje = lista_ranking[indice][1]
            print("  #" + str(indice + 1) + "  " + nombre + "  " + str(puntaje) + " pts")
            indice = indice + 1
    print("=" * 40)


# =====================================================================
#   OPCION I: CONFIGURAR JUEGO
# =====================================================================

def configurar_juego():
    # Permite ingresar las palabras del juego con su complejidad
    # Solo disponible si el archivo de palabras esta vacio
    # Al terminar llama a guardar_palabras() para guardar todo
    # Procedimiento

    palabras_existentes = cargar_palabras()
    if len(palabras_existentes) > 0:
        print("\nYa hay palabras configuradas.")
        print("Elimine el archivo '" + ARCHIVO_PALABRAS + "' para reiniciar.")
        return

    print("\n" + "=" * 40)
    print("         CONFIGURAR JUEGO")
    print("=" * 40)
    print("Complejidades: A = 2 pts | B = 3 pts | C = 5 pts")

    cantidad_palabras = leer_numero_entero("\n¿Cuantas palabras desea ingresar? ")
    while cantidad_palabras < 1:
        print("Error: debe ingresar al menos 1 palabra.")
        cantidad_palabras = leer_numero_entero("¿Cuantas palabras desea ingresar? ")

    lista_palabras = []
    numero_palabra = 1

    while numero_palabra <= cantidad_palabras:
        entrada = input("\nPalabra #" + str(numero_palabra) + ": ").strip().upper()

        if not validar_palabra(entrada):
            print("Error: palabra inválida (mínimo 3 letras, sin números ni espacios).")
            continue

        # Verificar que no este repetida
        es_repetida = False
        indice = 0
        while indice < len(lista_palabras):
            if lista_palabras[indice][0] == entrada:
                es_repetida = True
            indice = indice + 1
        if es_repetida:
            print("Error: esa palabra ya fue ingresada.")
            continue

        complejidad = input("  Complejidad de '" + entrada + "' (A/B/C): ").strip().upper()
        while complejidad != "A" and complejidad != "B" and complejidad != "C":
            print("  Error: ingrese A, B o C.")
            complejidad = input("  Complejidad de '" + entrada + "' (A/B/C): ").strip().upper()

        lista_palabras.append([entrada, complejidad])
        print("  OK: '" + entrada + "' agregada (" + str(obtener_puntos(complejidad)) + " pts).")
        numero_palabra = numero_palabra + 1

    guardar_palabras(lista_palabras)
    print("\n" + str(len(lista_palabras)) + " palabras guardadas correctamente.")


# =====================================================================
#   OPCION IV: SISTEMA DE PISTAS
# =====================================================================


def dar_pista(matriz, lista_palabras, palabras_encontradas, filas, cols):
    # Muestra la fila O la columna de la letra del medio de una palabra pendiente
    # No revela cual es la palabra ni en que direccion va
    # matriz y lista_palabras vienen de main() via jugar()
    # palabras_encontradas viene de jugar() (lista que crece durante la partida)
    # procedimiento

    # Construir lista de palabras que aun no fueron encontradas
    palabras_pendientes = []
    indice = 0
    while indice < len(lista_palabras):
        ya_encontrada = False
        indice_enc = 0
        while indice_enc < len(palabras_encontradas):
            if palabras_encontradas[indice_enc][0] == lista_palabras[indice][0]:
                ya_encontrada = True
            indice_enc = indice_enc + 1
        if not ya_encontrada:
            palabras_pendientes.append(lista_palabras[indice])
        indice = indice + 1

    if len(palabras_pendientes) == 0:
        print("No hay palabras pendientes.")
        return

    # Elegir una palabra pendiente al azar
    indice_palabra = random.randint(0, len(palabras_pendientes) - 1)
    palabra_pista  = palabras_pendientes[indice_palabra][0]

    # Buscar donde esta esa palabra en la matriz
    resultado = buscar_palabra_en_matriz(matriz, palabra_pista, filas, cols)

    if resultado is None:
        print("No se pudo generar una pista.")
        return

    fila_inicio = resultado[0]
    col_inicio  = resultado[1]
    dir_fila    = resultado[2]
    dir_col     = resultado[3]

    # Calcular la posicion de la letra del medio
    posicion_mitad = len(palabra_pista) // 2
    fila_mitad     = fila_inicio + dir_fila * posicion_mitad
    col_mitad      = col_inicio  + dir_col  * posicion_mitad

    # Revelar fila o columna al azar (sin decir cual es la palabra)
    if random.randint(0, 1) == 0:
        print("Pista: una letra de una palabra pendiente esta en la fila " + str(fila_mitad) + ".")
    else:
        print("Pista: una letra de una palabra pendiente esta en la columna " + str(col_mitad) + ".")


# =====================================================================
#   OPCION III: JUGAR
# =====================================================================

def jugar(matriz, lista_palabras, filas, cols, nombre_jugador, lista_ranking):
    # Controla el flujo completo de una partida
    # matriz, lista_palabras, filas, cols vienen de main() (generados en opcion 2)
    # nombre_jugador y lista_ranking vienen de main() (opcion 3)
    # Retorna tres valores a main(): palabras_encontradas, pistas_usadas, puntaje_final

    palabras_encontradas  = []   # se va llenando conforme el jugador encuentra palabras
    cantidad_pistas_usadas = 0
    total_palabras         = len(lista_palabras)

    # Crear el tablero de visualizacion:
    # letras en minuscula = no encontradas, MAYUSCULA = encontradas (en verde)
    tablero_display = []
    fila_actual = 0
    while fila_actual < filas:
        fila_display = []
        col_actual = 0
        while col_actual < cols:
            fila_display.append(matriz[fila_actual][col_actual].lower())
            col_actual = col_actual + 1
        tablero_display.append(fila_display)
        fila_actual = fila_actual + 1

    print("\n" + "=" * 40)
    print("  JUGADOR: " + nombre_jugador)
    print("  Palabras a encontrar: " + str(total_palabras))
    print("=" * 40)

    partida_activa = True
    while partida_activa and len(palabras_encontradas) < total_palabras:

        mostrar_matriz(tablero_display, filas, cols)

        # Mostrar lista de palabras con estado [X] o [ ]
        print("\nPalabras del juego:")
        indice = 0
        while indice < len(lista_palabras):
            ya_encontrada = False
            indice_enc = 0
            while indice_enc < len(palabras_encontradas):
                if palabras_encontradas[indice_enc][0] == lista_palabras[indice][0]:
                    ya_encontrada = True
                indice_enc = indice_enc + 1
            estado = "[X]" if ya_encontrada else "[ ]"
            pts = obtener_puntos(lista_palabras[indice][1])
            print("  " + estado + " " + lista_palabras[indice][0] + " (Complejidad " + lista_palabras[indice][1] + " - " + str(pts) + " pts)")
            indice = indice + 1

        # Mostrar estado del puntaje actual
        puntaje_actual = calcular_puntaje(palabras_encontradas, cantidad_pistas_usadas)
        penalizacion   = obtener_penalizacion(cantidad_pistas_usadas)
        print("\nEncontradas : " + str(len(palabras_encontradas)) + "/" + str(total_palabras))
        print("Puntaje     : " + str(puntaje_actual) + " pts  (penalizacion pistas: -" + str(penalizacion) + " pts)")
        print("Pistas disp.: " + str(MAX_PISTAS - cantidad_pistas_usadas) + "/" + str(MAX_PISTAS))
        print("\nOpciones: [1] Buscar palabra   [2] Pista   [3] Salir")

        opcion = input("Seleccione: ").strip()

        # ── Opcion 1: Buscar una palabra ──────────────────────────────
        if opcion == "1":
            entrada_palabra = input("Palabra a buscar: ").strip().upper()

            if not validar_palabra(entrada_palabra):
                print("Error: palabra inválida (mínimo 3 letras, sin números ni espacios).")
                continue

            # Verificar que no este ya encontrada
            ya_encontrada = False
            indice_enc = 0
            while indice_enc < len(palabras_encontradas):
                if palabras_encontradas[indice_enc][0] == entrada_palabra:
                    ya_encontrada = True
                indice_enc = indice_enc + 1
            if ya_encontrada:
                print("Esa palabra ya fue encontrada.")
                continue

            # Verificar que la palabra pertenezca al juego
            esta_en_juego = False
            indice = 0
            while indice < len(lista_palabras):
                if lista_palabras[indice][0] == entrada_palabra:
                    esta_en_juego = True
                indice = indice + 1
            if not esta_en_juego:
                print("Esa palabra no pertenece al juego.")
                continue

            # Leer las coordenadas del jugador
            fila_inicio = leer_numero_entero("Fila inicial: ")
            col_inicio  = leer_numero_entero("Columna inicial: ")
            fila_fin    = leer_numero_entero("Fila final: ")
            col_fin     = leer_numero_entero("Columna final: ")

            if fila_inicio >= filas or col_inicio >= cols or fila_fin >= filas or col_fin >= cols:
                print("Error: coordenadas fuera del tablero (0 a " + str(filas - 1) + ").")
                continue

            # Calcular diferencia de filas y columnas para determinar la direccion
            diferencia_filas = fila_fin - fila_inicio
            diferencia_cols  = col_fin  - col_inicio
            longitud_palabra = len(entrada_palabra)

            if diferencia_filas == 0 and diferencia_cols == 0:
                print("Error: las posiciones inicial y final son iguales.")
                continue

            dir_fila_valida = 0
            dir_col_valida  = 0

            if diferencia_filas == 0:
                # Movimiento horizontal
                if abs(diferencia_cols) != longitud_palabra - 1:
                    print("Error: el desplazamiento horizontal no coincide con la longitud (" + str(longitud_palabra) + " letras).")
                    continue
                dir_fila_valida = 0
                dir_col_valida  = 1 if diferencia_cols > 0 else -1

            elif diferencia_cols == 0:
                # Movimiento vertical
                if abs(diferencia_filas) != longitud_palabra - 1:
                    print("Error: el desplazamiento vertical no coincide con la longitud (" + str(longitud_palabra) + " letras).")
                    continue
                dir_fila_valida = 1 if diferencia_filas > 0 else -1
                dir_col_valida  = 0

            elif abs(diferencia_filas) == abs(diferencia_cols):
                # Movimiento diagonal (puntos extra)
                if abs(diferencia_filas) != longitud_palabra - 1:
                    print("Error: el desplazamiento diagonal no coincide con la longitud (" + str(longitud_palabra) + " letras).")
                    continue
                dir_fila_valida = 1 if diferencia_filas > 0 else -1
                dir_col_valida  = 1 if diferencia_cols  > 0 else -1

            else:
                print("Error: el movimiento debe ser horizontal, vertical o diagonal.")
                continue

            # Verificar que las letras en la matriz coincidan con la palabra
            letras_correctas = True
            indice = 0
            while indice < longitud_palabra:
                fila_check = fila_inicio + dir_fila_valida * indice
                col_check  = col_inicio  + dir_col_valida  * indice
                if matriz[fila_check][col_check].upper() != entrada_palabra[indice]:
                    letras_correctas = False
                indice = indice + 1

            if letras_correctas:
                # Buscar los datos completos de esa palabra en lista_palabras
                datos_palabra = ["", ""]
                indice = 0
                while indice < len(lista_palabras):
                    if lista_palabras[indice][0] == entrada_palabra:
                        datos_palabra = lista_palabras[indice]
                    indice = indice + 1

                palabras_encontradas.append(datos_palabra)

                # Marcar en el tablero de display con MAYUSCULAS (aparece en verde)
                indice = 0
                while indice < longitud_palabra:
                    tablero_display[fila_inicio + dir_fila_valida * indice][col_inicio + dir_col_valida * indice] = entrada_palabra[indice].upper()
                    indice = indice + 1

                pts_ganados   = obtener_puntos(datos_palabra[1])
                nuevo_puntaje = calcular_puntaje(palabras_encontradas, cantidad_pistas_usadas)
                print("\nCORRECTO! +" + str(pts_ganados) + " pts  →  Puntaje: " + str(nuevo_puntaje) + " pts")

                # Mostrar posicion en ranking en tiempo real (puntos extra)
                # Se usa una COPIA del ranking para no modificar el original todavia
                ranking_temporal = []
                indice_rk = 0
                while indice_rk < len(lista_ranking):
                    ranking_temporal.append([lista_ranking[indice_rk][0], lista_ranking[indice_rk][1]])
                    indice_rk = indice_rk + 1
                posicion_temporal = actualizar_ranking(ranking_temporal, nombre_jugador, nuevo_puntaje)

                if posicion_temporal != -1:
                    print("Tu posicion en el ranking: #" + str(posicion_temporal))
                    puntos_faltantes = puntos_para_avanzar(ranking_temporal, nombre_jugador, nuevo_puntaje)
                    if posicion_temporal == 1:
                        print("Eres el #1 del ranking!")
                    elif puntos_faltantes > 0:
                        print("Faltan " + str(puntos_faltantes) + " pts para subir al puesto #" + str(posicion_temporal - 1))
                else:
                    if len(ranking_temporal) >= MAX_RANKING:
                        puntos_faltantes = ranking_temporal[-1][1] - nuevo_puntaje + 1
                        if puntos_faltantes > 0:
                            print("Faltan " + str(puntos_faltantes) + " pts para entrar al ranking.")

                if len(palabras_encontradas) == total_palabras:
                    print("\nFELICITACIONES! Encontraste todas las palabras!")
                    mostrar_matriz(tablero_display, filas, cols)
                    partida_activa = False

            else:
                print("Incorrecto: la palabra '" + entrada_palabra + "' no esta en esa posicion.")

        # ── Opcion 2: Pedir pista ─────────────────────────────────────
        elif opcion == "2":
            if cantidad_pistas_usadas >= MAX_PISTAS:
                print("No te quedan mas pistas.")
            else:
                cantidad_pistas_usadas = cantidad_pistas_usadas + 1
                print()
                dar_pista(matriz, lista_palabras, palabras_encontradas, filas, cols)
                print("Penalizacion acumulada: -" + str(obtener_penalizacion(cantidad_pistas_usadas)) + " pts")

        # ── Opcion 3: Salir ───────────────────────────────────────────
        elif opcion == "3":
            confirmar = input("¿Desea salir del juego? (s/n): ").strip().lower()
            if confirmar == "s":
                partida_activa = False

        else:
            print("Opcion invalida. Ingrese 1, 2 o 3.")

    puntaje_final = calcular_puntaje(palabras_encontradas, cantidad_pistas_usadas)
    return palabras_encontradas, cantidad_pistas_usadas, puntaje_final


# =====================================================================
#   RESULTADO FINAL
# =====================================================================

def finalizar_juego(nombre_jugador, palabras_encontradas, cantidad_pistas_usadas, puntaje_final, lista_ranking, total_palabras):
    # Muestra el resumen de la partida, actualiza el ranking y lo guarda
    # Recibe los tres valores que retorno jugar() mas el ranking de main()
    # Retorna la lista_ranking actualizada para que main() la guarde

    penalizacion = obtener_penalizacion(cantidad_pistas_usadas)

    print("\n" + "=" * 40)
    print("         RESULTADO FINAL")
    print("=" * 40)
    print("Jugador           : " + nombre_jugador)
    print("Palabras halladas : " + str(len(palabras_encontradas)) + "/" + str(total_palabras))
    print("Pistas usadas     : " + str(cantidad_pistas_usadas) + "/3  (-" + str(penalizacion) + " pts)")
    print("PUNTAJE FINAL     : " + str(puntaje_final) + " pts")
    print("=" * 40)

    # Actualizar el ranking real y guardar en archivo
    posicion_final = actualizar_ranking(lista_ranking, nombre_jugador, puntaje_final)
    guardar_puntajes(lista_ranking)

    print()
    if posicion_final != -1:
        print("Ingresaste al ranking! Tu posicion: #" + str(posicion_final))
        puntos_faltantes = puntos_para_avanzar(lista_ranking, nombre_jugador, puntaje_final)
        if posicion_final == 1:
            print("Eres el MEJOR jugador!")
        elif puntos_faltantes > 0:
            print("Faltan " + str(puntos_faltantes) + " pts para subir al puesto #" + str(posicion_final - 1))
    else:
        print("No ingresaste al ranking esta vez.")
        if len(lista_ranking) >= MAX_RANKING:
            puntos_faltantes = lista_ranking[-1][1] - puntaje_final + 1
            if puntos_faltantes > 0:
                print("Te faltaron " + str(puntos_faltantes) + " pts para entrar al ranking.")

    mostrar_ranking(lista_ranking)
    return lista_ranking


# =====================================================================
#   MENU PRINCIPAL
# =====================================================================

def mostrar_menu():
    # Muestra las 5 opciones del menu principal
    print("\n" + "=" * 40)
    print("    SOPA DE LETRAS - CENFOTEC SOFT-01")
    print("=" * 40)
    print("  1. Configurar juego")
    print("  2. Cargar matriz")
    print("  3. Jugar")
    print("  4. Ver ranking")
    print("  5. Salir")
    print("=" * 40)


def main():
    # Funcion principal que controla todo el programa
    # Aqui se crean las variables principales que se pasan a las otras funciones:
    #   matriz       → se genera en opcion 2 y se pasa a jugar()
    #   lista_palabras → se carga en opcion 2 y se pasa a jugar() y dar_pista()
    #   filas, cols  → dimensiones del tablero, se pasan a mostrar_matriz() y jugar()
    #   lista_ranking  → se carga al inicio y se actualiza al terminar cada partida

    matriz         = None   # None indica que aun no se cargo la matriz
    filas          = 0
    cols           = 0
    lista_palabras = []
    lista_ranking  = cargar_puntajes()

    print("\n=== Bienvenido a la Sopa de Letras ===")
    print("    Universidad CENFOTEC - SOFT-01")

    programa_activo = True
    while programa_activo:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            # Configurar el juego (solo si no hay palabras guardadas)
            configurar_juego()

        elif opcion == "2":
            # Leer palabras del archivo y generar el tablero
            lista_palabras = cargar_palabras()
            if len(lista_palabras) == 0:
                print("\nNo hay palabras configuradas. Use la opcion 1 primero.")
            else:
                print("\nGenerando sopa de letras con " + str(len(lista_palabras)) + " palabras...")
                matriz, filas, cols = generar_matriz(lista_palabras)
                print("Matriz de " + str(filas) + "x" + str(cols) + " generada.")
                mostrar_matriz(matriz, filas, cols)

        elif opcion == "3":
            # Verificar que la matriz este lista antes de jugar
            if matriz is None:
                print("\nPrimero debe cargar la matriz (opcion 2).")
            else:
                lista_ranking  = cargar_puntajes()
                nombre_jugador = input("\nIngrese su nombre: ").strip()
                if nombre_jugador == "":
                    nombre_jugador = "Jugador"

                # Saludar si el jugador ya tiene puntaje registrado
                posicion_previa = buscar_en_ranking(lista_ranking, nombre_jugador)
                if posicion_previa != -1:
                    print("Bienvenido de nuevo, " + nombre_jugador + "!")
                    print("Tu mejor puntaje: " + str(lista_ranking[posicion_previa - 1][1]) + " pts (puesto #" + str(posicion_previa) + ")")
                else:
                    print("Bienvenido, " + nombre_jugador + "!")

                # Iniciar la partida y recibir sus resultados
                palabras_encontradas, cantidad_pistas_usadas, puntaje_final = jugar(
                    matriz, lista_palabras, filas, cols, nombre_jugador, lista_ranking
                )

                # Mostrar resultado final y actualizar ranking
                lista_ranking = finalizar_juego(
                    nombre_jugador, palabras_encontradas, cantidad_pistas_usadas,
                    puntaje_final, lista_ranking, len(lista_palabras)
                )

        elif opcion == "4":
            lista_ranking = cargar_puntajes()
            mostrar_ranking(lista_ranking)

        elif opcion == "5":
            print("\nHasta luego!")
            programa_activo = False

        else:
            print("Opcion invalida. Ingrese un numero del 1 al 5.")


# Punto de entrada del programa
main()