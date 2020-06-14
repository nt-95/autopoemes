# autopoemes
Generateur automatique de poèmes (Python).

generateur.py : script qui charge un fichier texte préalablement traité, estime un modèle de langue, et génère un nouveau texte de façon aléatoire. 

prepare_poesie.py : script qui a servi à l'élaboration du fichier texte pour le rendre utilisable par generateur.py. Il nettoie le texte d'origine d'éléments indésirables, pour ne conserver que des vers, qu'il encadre par les marqueurs BEGIN NOW et END.

extractor.py : script qui a servi à extraire les poèmes à l'état brut sur diverses bases de données en ligne. C'est le texte qu'il fournit qu'on passera ensuite dans prepare_poesie.py

--------------------------------------------------------

MODE D'EMPLOI 
- Sur le terminal, lancer ''python generateur.py poemes_1780k".

- Il est possible d'ajouter à la commande les arguments facultatifs --v (nombre de vers), --s (nombre de strophes), --p (pas de ponctuation), --m (minuscules uniquement).

- Par exemple "python generateur.py poemes_1780k --v 3 --s 6 --p" générera un poème composé de six strophes de trois vers chacune, sans ponctuation, mais en conservant la casse d'origine. 

--------------------------------------------------------

EXEMPLES DE TEXTES GÉNÉRÉS 

Cette série de poèmes à été générée automatiquement à partir de generateur.py.

I.
> 
    chaque fleur est une chose sotte ;
    mais le canal était désert
    des cieux doux, en les devinant;
    s'élève quelque prière!
II.
> 
    éternel et coupable.
    Le Printemps est évident, car
    Les verres tombèrent se brisèrent
    Un coeur à moi en n'étant rien
    Que le déroulement des vagues, des splendeurs et des accapareurs.
    De sentiment; 
    Les vents ont expiré couronnés d'anémones
III.
> 
    la chambre est glacée.on voit traîner à terre,
    un petit sac brodé de mousse noire, 
    j'aiguisais lentement sur la route,
    sa vieille vénus
IV.
> 
    rampe et meurs misérablement
    des baisers, des oiseaux chantant soir et matin, 
    je suis malade: oh! je veux taire
    quelle âme est un temple aux ombres bocagères
V.
> 
    Retiens les griffes de ta jupe large
    C'est le printemps des nouvelles douleurs
    J'ai vu l'horreur de leurs doigts;
    L'ennui, l'enluminure atroce et les coeurs mortels un divin opium !
    Le coeur plein de beauté, connaissez-vous les rides ? 
    Le soleil filtre à travers ma ruine allez donc sans remords

--------------------------------------------------------

DETAILS
1. La préparation du corpus

Le premier script prend simplement un corpus de poèmes déjà existants d'environ 180 000 vers (Baudelaire, De Nerval, Verlaine, Rimbaud, Mallarmé, Apollinaire, Roger Gilbert-Lecomte, Toukaram, Shankaracharya...) et encadre chaque vers par les mots ''BEGIN NOW'' et ''END'' : il renvoie ainsi un fichier texte avec ces poèmes un peu modifiés. 
Le deuxième programme analyse ce nouveau corpus, et mémorise sous forme de liste de sets1 chaque mot de chaque ver accompagné des deux mots qui le précèdent. 
Ainsi un fragment de texte comme :

    “Les métaux inconnus, les perles de la mer,”  
      (Baudelaire, Les Fleurs du Mal, “ Benediction ”)

devient avec le premier script : 

    BEGIN NOW Les métaux inconnus, les perles de la mer, END

et avec le deuxième script : 

    [(''BEGIN'', ''NOW'', ''Les''), (''NOW'', ''Les'', ''métaux''), (''Les'', ''métaux'', ''inconnus,''), … ]

2. L'estimation d'un modèle de langue à partir de probabilités

L'ensemble de ces poèmes est donc transformé en une longue liste de sets de trois mots (a, b, c). À partir d'elle, nous allons être capables d'établir une liste de tous les mots c qui apparaissent après les deux mots a et b. On mémorisera cette information dans un dictionnaire de la forme { (a, b) : [c1, c2, c3] } c'est à dire un dictionnaire qui à chaque suite de mots a et b associe une liste de différents mots c possibles. Par exemple, si dans notre corpus, en plus de ce vers de Baudelaire, nous avions d'autres vers où figurent les groupes de mots ''Les métaux lourds'', ''Les métaux brillants'', ''de la lune'', nous obtiendrions ce dictionnaire :

{ (''Les'', ''métaux'') : [''inconnus'', ''lourds'', ''brillants'' …] 
                  (''de'', ''la'') : [''mer'', ''lune'', …] 
	         (''la'', ''mer,'') : [''END'']
                 …  }

Si en plus de cela, nous trouvions trois autres fois le groupe de mots ''Les métaux inconnus'' , on aurait plusieurs fois ''inconnus'' dans la liste associée à (''Les'', ''métaux'') : 

{ (''Les'', ''métaux'') : [''inconnus'', ''lourds'', ''brillants'', ''inconnus'', ''inconnus'']  
     … }
     
Le programme peut alors compter la probabilité d'apparition d'un mot sachant les deux mots précédents. C'est une estimation de modèle de langue. 
C'est un calcul très simple : à partir d'un set de trois mots (a, b, c), on cherche P(c | a, b) c'est à dire la probabilité de trouver le mot c, sachant les deux mots précédents a et b. Cette probabilité s'obtient en comptant le nombre de fois ou le mot c apparaît précédé de a et b, et en divisant ce nombre par le nombre de fois où a et b apparaissent sans nécessairement être suivis de c, autrement dit : #(a b c) / #(a b). 
Si l'on reprend l'exemple précédent, pour trouver P(inconnus | Les, métaux) – la probabilité d'apparition du mot ''inconnus'' sachant ''Les'' et ''métaux'' –, on va calculer le nombre d'apparitions de (''Les'', ''métaux'', ''inconnus,'') et le diviser par le nombre d'apparitions de (''Les'', ''métaux'') pour l'ensemble du corpus. Cela donnera une probabilité d'apparition entre 0 et 1 pour ''inconnus''. Ici ''Les métaux inconnus'' apparaît 3 fois, tandis qu'on observe ''Les métaux'' 5 fois. On obtient  P(inconnus | Les métaux) = 3/5 = 0,6.  On fera ensuite ce calcul pour chaque mot possible après ''Les métaux'' : P(lourds | Les métaux) = 1/5 = 0.2,  P(brillants | Les métaux) = 1/5 = 0.2. Et ainsi de suite, pour chaque mot du corpus. 

3. La génération d'un nouveau poème

On peut désormais générer un poème. 
Pour générer un nouveau vers, on commence toujours par rechercher la probabilité d'apparition de tous les mots c qui peuvent apparaître après ''BEGIN'' et ''NOW'' (a et b). L'ordinateur choisit alors un de ces mots c au hasard, mais son choix est en partie influencé par les probabilités. C'est comme si certains angles d'un dé étaient limés. C'est un weighted random choice : il aura d'avantage tendance a choisir les mots dont la probabilité d'apparition est la plus haute, sans que cela soit toujours le cas. On recherchera ensuite la probabilité d'apparition de tous les mots d qui peuvent apparaître après ''	NOW'' et le mot c choisi toute à l'heure, et on choisira un mot d, et ainsi de suite pour un mot e sachant c et d, etc... 
Un vers se termine lorsque c'est le mot ''END'' qui est choisi. Après ''END'' il ne peut y avoir que ''BEGIN'' et ''NOW'', donc l'ordinateur fera un saut à la ligne et recommencera à chercher un mot c après ''BEGIN'' et ''NOW''. Le nombre de vers quant à lui est fixé par un chiffre n. Lorsque l'ordinateur est tombé n fois sur le mot ''END'', il affiche le poème à l'écran (en enlevant les ''BEGIN NOW'' et les ''END'') et le programme s'arrête. 

4. Observations

Ce type de génération de texte basé sur un modèle probabiliste est ici rudimentaire.
Le problème majeur de ce système par probabilités est qu'un trop petit corpus ne donne pas assez de probabilités pour que l'ordinateur puisse inventer par lui même une nouvelle phrase : il aura tendance à copier ce qui existe déjà, et souvent des vers entiers, car il n'aura trouvé à chaque fois qu'un seul mot c possible après a et b. C'est pourquoi on retrouve dans certains poèmes des citations entières de poèmes existants. Par conséquent, le fait d'ignorer les majuscules ou la ponctuation influence les probabilités, et les vers ont alors tendance à être plus inventifs, plus longs, mais ils contiennent aussi beaucoup plus d'erreurs. Se baser en effet seulement sur les deux mots précédents pour prédire le troisième mot ne permet pas d'assurer la cohérence grammaticale de phrases un peu longues ou complexes ; l'ordinateur n'a en fait pas de moyen de se souvenir de ce qu'il a dit au-delà des deux mots précédents.
Aussi, s'il y a un lien probabiliste entre les mots qui permet d'obtenir tout de même une cohérence grammaticale et sémantique minimale au sein du vers, il n'y a aucun lien d'un vers à l'autre. Leur combinaison est totalement aléatoire, et le fait qu'un poème entier semble évoquer un même sujet est le parfait fruit du hasard.
