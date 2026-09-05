import re
import os

def nettoyer_bas_de_page(chemin_entree, chemin_sortie):
    """
    Lit un fichier texte/markdown, retire les bas de page de type
    '193 POUR REVENIR A LA TABLE DES MATIERES, CLIQUEZ ICI',
    puis sauvegarde le résultat.
    """
    try:
        # Ouverture du fichier source
        with open(chemin_entree, 'r', encoding='utf-8') as f:
            texte = f.read()

        # --- L'EXPRESSION RÉGULIÈRE ---
        # ^\s*       : Début de ligne (avec d'éventuels espaces)
        # \d+        : Un ou plusieurs chiffres (le numéro de page dynamique)
        # \s+        : Un ou plusieurs espaces
        # POUR...    : La phrase littérale ciblée
        # .*$        : Le reste éventuel de la ligne (ex: le ";" à la fin) jusqu'au saut de ligne
        pattern = r"^\s*\d+\s+POUR REVENIR A LA TABLE DES MATIERES, CLIQUEZ ICI.*$"

        # re.MULTILINE permet au ^ et $ de s'appliquer à chaque ligne du texte individuellement
        # re.IGNORECASE permet d'ignorer les majuscules/minuscules au cas où
        texte_nettoye = re.sub(pattern, '', texte, flags=re.IGNORECASE | re.MULTILINE)

        # Le nettoyage d'une ligne laisse souvent de gros trous (sauts de ligne consécutifs)
        # On réduit les espaces vides excessifs à un maximum de deux sauts de ligne (\n\n)
        texte_nettoye = re.sub(r'\n{3,}', '\n\n', texte_nettoye)

        # Sauvegarde du nouveau fichier
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            f.write(texte_nettoye.strip())

        print(f"✅ Nettoyage terminé avec succès ! Résultat sauvegardé dans : {chemin_sortie}")

    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {chemin_entree} n'a pas été trouvé.")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

# ==========================================
# UTILISATION
# ==========================================
if __name__ == "__main__":
    # Définissez ici les chemins vers vos fichiers
    FICHIER_SOURCE = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/code_de_travail.md"   # Le fichier à nettoyer
    FICHIER_PROPRE = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/code_de_travail_cleaned.md" # Le résultat

    # Lancer le nettoyage
    nettoyer_bas_de_page(FICHIER_SOURCE, FICHIER_PROPRE)
