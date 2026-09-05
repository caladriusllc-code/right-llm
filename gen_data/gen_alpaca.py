import json
import re
import os

def extraire_blocs(fichier_md):
    """Extrait les blocs sémantiques depuis le fichier markdown."""
    with open(fichier_md, 'r', encoding='utf-8') as f:
        contenu = f.read()

    blocs = []
    # On récupère le texte situé sous chaque '## Bloc X'
    pattern = re.compile(r"## Bloc \d+\n+(.*?)(?=\n+---|\\Z)", re.DOTALL)

    for match in pattern.finditer(contenu):
        texte_bloc = match.group(1).strip()
        if texte_bloc:
            blocs.append(texte_bloc)

    return blocs

def extraire_reference_juridique(texte):
    """
    Tente de trouver le chapitre, la section ou l'article pour personnaliser
    légèrement la question (sans LLM).
    """
    reference = "ce texte juridique" # Par défaut

    # Cherche "ARTICLE X", "CHAPITRE X", etc.
    match = re.search(r"^(ARTICLE\s+\d+|CHAPITRE\s+\w+|Art\.\s*\d+\.\d+)", texte, re.IGNORECASE)
    if match:
        reference = match.group(1).strip()

    return reference

def construire_dataset_jsonl(chemin_entree, chemin_sortie):
    print(f"📖 Lecture du fichier : {chemin_entree}")
    blocs = extraire_blocs(chemin_entree)

    if not blocs:
        print("❌ Aucun bloc trouvé dans le fichier Markdown.")
        return

    # Ouverture du fichier de sortie en mode écriture (JSON Lines)
    with open(chemin_sortie, 'w', encoding='utf-8') as f_out:
        for bloc in blocs:

            reference = extraire_reference_juridique(bloc)

            # --- STRATÉGIE SANS LLM ---
            # On utilise une question générique (template)
            instruction = f"Quelles sont les dispositions prévues par {reference} ?"

            # Format Alpaca :
            # Puisque nous n'avons pas d'IA pour formuler une réponse concise,
            # la réponse "idéale" (output) est le texte brut de l'article lui-même.
            # L'input est vide car la question se suffit à elle-même, ou inversement.

            item_alpaca = {
                "instruction": instruction,
                "input": "", # Ou "Contexte juridique de la Côte d'Ivoire"
                "output": bloc.strip()
            }

            # Conversion en ligne JSON valide et écriture
            ligne_json = json.dumps(item_alpaca, ensure_ascii=False)
            f_out.write(ligne_json + "\n")

    print(f"🎉 Dataset .jsonl généré avec succès ! ({len(blocs)} lignes créées)")
    print(f"📁 Fichier sauvegardé sous : {chemin_sortie}")

if __name__ == '__main__':
    # Remplacez par le chemin exact issu de votre étape 3 (sauvegarde en .md)
    CHEMIN_MD = r"/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/code_de_travail_cleaned.md"
    CHEMIN_JSONL = r"/Users/mac/Documents/Ma recherche scientifique/rosaria/data/alpaca-data/ohada_data/dataset_code_travail.jsonl"

    if os.path.exists(CHEMIN_MD):
        construire_dataset_jsonl(CHEMIN_MD, CHEMIN_JSONL)
    else:
        print(f"❌ Le fichier introuvable : {CHEMIN_MD}")
