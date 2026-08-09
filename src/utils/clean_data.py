import re
import os

def clean_legal_text(text):
    """
    Nettoie le texte en retirant les marqueurs de listes et numéros isolés.
    """
    # 1. Retire les numéros ou lettres suivis d'une parenthèse en début de ligne
    # Exemples matchés : "5) ", "a) ", " 12) ", "B) "
    cleaned = re.sub(r'^\s*(\d+|[a-zA-Z])\)\s*', '', text, flags=re.MULTILINE)
    
    # 2. Retire les éléments avec parenthèses des deux côtés en début de ligne
    # Exemples matchés : "(a) ", "(1) "
    cleaned = re.sub(r'^\s*\(\s*(\d+|[a-zA-Z])\s*\)\s*', '', cleaned, flags=re.MULTILINE)

    # 3. Retire les numéros complètement isolés sur une seule ligne
    cleaned = re.sub(r'^\s*\d+\s*$', '', cleaned, flags=re.MULTILINE)
    
    # 4. Nettoie les sauts de lignes multiples potentiellement créés par la suppression des numéros isolés
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()

if __name__ == "__main__":
    # === TEST RAPIDE AVEC VOTRE EXEMPLE ===
    texte_brut = """5) La perte occasionnée par l’insolvabilité de l’un des débiteurs solidaires se répartit entre
        les autres codébiteurs, selon leurs parts contributoires respectives.

        a) Une autre phrase avec lettre.
        (b) Encore une autre forme.

        12

        Suite du texte normal."""

    print("--- AVANT NETTOYAGE ---")
    print(texte_brut)
    print("\n--- APRÈS NETTOYAGE ---")
    print(clean_legal_text(texte_brut))
    
    print("\n" + "="*50 + "\n")
    
    # === POUR TRAITER VOS FICHIERS RÉELS ===
    # Décommentez et modifiez les chemins ci-dessous pour utiliser le script sur vos fichiers
    
    
    chemin_entree = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/OHADA-act-f.md" # ou .json / .txt
    chemin_sortie = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/acte-uniforme/OHADA_acte_uniforme.md"
    
    if os.path.exists(chemin_entree):
        with open(chemin_entree, 'r', encoding='utf-8') as f:
            contenu = f.read()
            
        contenu_propre = clean_legal_text(contenu)
        
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            f.write(contenu_propre)
            
        print(f"✅ Fichier nettoyé et sauvegardé dans : {chemin_sortie}")
    else:
        print(f"❌ Le fichier {chemin_entree} est introuvable.")
    