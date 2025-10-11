# Exercises for Capitaine Python (function-first where possible for safe testing)
EXERCISES = [
  {
    "id": "01-print",
    "title": "Fais parler l'ordi",
    "stars": 1,
    "prompt": "Affiche exactement: Salut Capitaine Python !",
    "starter": 'print("Salut Capitaine Python !")',
    "solution_explanation": "Pour afficher du texte en Python, on utilise la fonction print(). Le texte doit être entre guillemets. print() affiche automatiquement un retour à la ligne après le texte.",
    "tests": [
      "out = run_with_input('')",
      "assert out.strip() == 'Salut Capitaine Python !'"
    ],
    "hints": ["Utilise print(...)", "N'oublie pas les guillemets", "Respecte espaces et ponctuation"]
  },
  {
    "id": "02-variables",
    "title": "Trésor dans une variable",
    "stars": 1,
    "prompt": "Crée une variable message avec 'Bonjour Hugo' et affiche-la.",
    "starter": 'message = "Bonjour Hugo"\nprint(message)',
    "solution_explanation": "Une variable stocke une valeur. Ici, on crée la variable 'message' et on y met le texte 'Bonjour Hugo'. Ensuite, print(message) affiche le contenu de la variable. C'est comme une boîte qui contient une valeur !",
    "tests": [
      "out = run_with_input('')",
      "assert 'Bonjour Hugo' in out"
    ],
    "hints": ["message = 'Bonjour Hugo'", "Puis print(message)"]
  },
  {
    "id": "03-conditions",
    "title": "Feu rouge/vert",
    "stars": 2,
    "prompt": "Lis un mot (rouge/vert) et affiche 'STOP' si rouge, 'GO' si vert.",
    "starter": 'couleur = input()\nif couleur == "rouge":\n    print("STOP")\nelif couleur == "vert":\n    print("GO")',
    "solution_explanation": "input() lit ce que l'utilisateur tape. Le if/elif permet de faire des choix : si la couleur est 'rouge', on affiche 'STOP', sinon si c'est 'vert', on affiche 'GO'. Les conditions permettent à ton programme de réagir différemment selon la situation.",
    "tests": [
      "out1 = run_with_input('rouge\n')",
      "out2 = run_with_input('vert\n')",
      "assert out1.strip() == 'STOP'",
      "assert out2.strip() == 'GO'"
    ],
    "hints": ["if couleur == 'rouge': print('STOP')", "elif couleur == 'vert': print('GO')"]
  },

  # ---- NEW EXERCISES ----
  {
    "id": "04-boucle-for",
    "title": "Compte 1 à 5",
    "stars": 1,
    "prompt": "Affiche les nombres de 1 à 5 chacun sur sa ligne.",
    "starter": "for i in range(1, 6):\n    print(i)",
    "solution_explanation": "La boucle for répète des actions. range(1,6) génère les nombres 1,2,3,4,5. Pour chaque nombre, la boucle l'affiche avec print(i). C'est parfait pour répéter une tâche plusieurs fois !",
    "tests": [
      "out = run_with_input('')",
      "assert out.strip().splitlines() == ['1','2','3','4','5']"
    ],
    "hints": ["range(1,6) va de 1 à 5", "print(i) dans la boucle"]
  },
  {
    "id": "05-fonction-bonjour",
    "title": "Dis Bonjour",
    "stars": 2,
    "prompt": "Écris une fonction bonjour(nom) qui renvoie 'Bonjour <nom>' (sans l'afficher).",
    "starter": "def bonjour(nom):\n    return 'Bonjour ' + nom",
    "solution_explanation": "Une fonction est un bloc de code réutilisable. def bonjour(nom): crée la fonction. return renvoie une valeur sans l'afficher. On peut l'utiliser plusieurs fois avec différents noms. C'est comme une recette de cuisine !",
    "tests": [
      "assert ns.get('bonjour'), 'La fonction bonjour(nom) doit exister'",
      "assert ns['bonjour']('Hugo') == 'Bonjour Hugo'",
      "assert ns['bonjour']('Ava') == 'Bonjour Ava'"
    ],
    "hints": ["def bonjour(nom):", "return 'Bonjour ' + nom"]
  },
  {
    "id": "06-somme-1-a-n",
    "title": "Addition magique",
    "stars": 2,
    "prompt": "Écris une fonction somme(n) qui renvoie 1 + 2 + ... + n.",
    "starter": "def somme(n):\n    total = 0\n    for i in range(1, n+1):\n        total += i\n    return total",
    "solution_explanation": "On utilise une variable 'total' qui commence à 0. La boucle ajoute chaque nombre de 1 à n. total += i signifie total = total + i. À la fin, on retourne le total. C'est comme compter dans un pot !",
    "tests": [
      "assert ns.get('somme'), 'La fonction somme(n) doit exister'",
      "assert ns['somme'](1) == 1",
      "assert ns['somme'](5) == 15",
      "assert ns['somme'](10) == 55"
    ],
    "hints": ["Commence à 0", "Boucle de 1 à n", "Ajoute i à total", "Retourne total"]
  },
  {
    "id": "07-fizzbuzz",
    "title": "FizzBuzz rigolo",
    "stars": 3,
    "prompt": "Écris une fonction fizzbuzz(n) qui renvoie une liste de 1..n en remplaçant multiples de 3 par 'Fizz', de 5 par 'Buzz', et de 3 et 5 par 'FizzBuzz'.",
    "starter": "def fizzbuzz(n):\n    res = []\n    for i in range(1, n+1):\n        s = ''\n        if i % 3 == 0: s += 'Fizz'\n        if i % 5 == 0: s += 'Buzz'\n        res.append(s or i)\n    return res",
    "solution_explanation": "Le modulo (%) donne le reste d'une division. Si i % 3 == 0, i est multiple de 3. On construit une chaîne vide et on y ajoute 'Fizz' et/ou 'Buzz'. s or i retourne i si s est vide. C'est un jeu de logique !",
    "tests": [
      "assert ns.get('fizzbuzz'), 'La fonction fizzbuzz(n) doit exister'",
      "fb = ns['fizzbuzz'](15)",
      "assert fb[2] == 'Fizz'",
      "assert fb[4] == 'Buzz'",
      "assert fb[14] == 'FizzBuzz'",
      "assert fb[0] == 1 and fb[1] == 2"
    ],
    "hints": ["Utilise % (modulo)", "Ajoute 'Fizz' si multiple de 3, 'Buzz' si multiple de 5"]
  },
  {
    "id": "08-max-de-trois",
    "title": "Le plus grand",
    "stars": 2,
    "prompt": "Écris une fonction max_de_trois(a,b,c) qui renvoie le plus grand sans utiliser max().",
    "starter": "def max_de_trois(a,b,c):\n    m = a\n    if b > m: m = b\n    if c > m: m = c\n    return m",
    "solution_explanation": "On commence avec m = a comme plus grand provisoire. Ensuite on compare avec b et c. Si on trouve un plus grand, on met à jour m. C'est comme une compétition où le vainqueur change si quelqu'un de plus grand arrive !",
    "tests": [
      "assert ns.get('max_de_trois'), 'La fonction max_de_trois doit exister'",
      "assert ns['max_de_trois'](1,2,3) == 3",
      "assert ns['max_de_trois'](9,1,2) == 9",
      "assert ns['max_de_trois'](-1,-5,-3) == -1"
    ],
    "hints": ["Garde une variable m", "Compare b puis c"]
  }
]

# star map for DB
EX_STARS = {e["id"]: e["stars"] for e in EXERCISES}
