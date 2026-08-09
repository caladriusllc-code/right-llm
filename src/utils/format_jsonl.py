import json
import re
import os

def generate_jsonl_dataset(input_md_path, output_jsonl_path):
    print(f"🔄 Lecture du fichier : {input_md_path}...")
    
    # 1. Le prompt système exigé
    system_prompt = (
        "Tu es un assistant expert en droit OHADA. Avant de donner ta réponse finale, "
        "tu dois impérativement réfléchir étape par étape à la résolution du problème juridique. "
        "Place ton raisonnement entre des balises <think> et </think>, puis donne ta réponse finale."
    )
    
    # Lecture du fichier Markdown nettoyé
    try:
        with open(input_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {input_md_path} est introuvable.")
        return

    # 2. Séparation du texte en blocs (en se basant sur "## Bloc")
    blocs = re.split(r'^##\s+Bloc\s+\d+', content, flags=re.MULTILINE)
    
    dataset = []
    
    for bloc in blocs:
        bloc = bloc.strip()
        # Ignorer l'en-tête du fichier ou les blocs vides
        if not bloc or "Nombre total de chunks juridiques" in bloc:
            continue
            
        # 3. Extraction intelligente du titre (Ex: "ARTICLE 2/21")
        lines = bloc.split('\n')
        titre_element = "ce texte de loi"
        sous_titre = ""
        
        for line in lines:
            line_stripped = line.strip()
            # On cherche la ligne qui commence par ARTICLE, CHAPITRE, etc.
            if re.match(r'^(ARTICLE|CHAPITRE|SECTION|TITRE|LIVRE)', line_stripped, re.IGNORECASE):
                titre_element = line_stripped
            # On cherche un sous-titre entre parenthèses juste après (ex: "(Conflit entre clauses-types...)")
            elif line_stripped.startswith('(') and line_stripped.endswith(')'):
                sous_titre = line_stripped
                break # On s'arrête de chercher après avoir trouvé le titre et le sous-titre
                
        # 4. Génération de la question (User)
        if titre_element != "ce texte de loi":
            sujet = f" {sous_titre}" if sous_titre else ""
            user_question = f"Que dispose l'{titre_element}{sujet} en droit OHADA ?"
        else:
            user_question = "Que dit cette disposition du droit OHADA ?"
            
        # 5. Génération de la réflexion <think> et de la réponse
        # Étant donné qu'on génère par script, on crée une structure de réflexion logique générique
        think_process = (
            "<think>\n"
            f"1. Analyse de la requête : L'utilisateur s'interroge sur {titre_element}{sous_titre}.\n"
            "2. Recherche dans la base de connaissances OHADA : Identification des dispositions applicables.\n"
            "3. Synthèse : Je dois formuler la règle juridique de manière précise telle qu'elle est rédigée dans l'Acte uniforme.\n"
            "</think>"
        )
        
        # Le contenu de la réponse est le texte de loi brut (nettoyé de ses tirets horizontaux s'il y en a)
        bloc_propre = bloc.replace("---", "").strip()
        assistant_response = f"{think_process}\n\n{bloc_propre}"
        
        # 6. Assemblage au format ChatML / HuggingFace
        record = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": assistant_response}
            ]
        }
        dataset.append(record)

    # 7. Sauvegarde au format JSONL (une ligne = un objet JSON)
    print(f"💾 Sauvegarde en cours...")
    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"✅ Processus terminé ! {len(dataset)} exemples juridiques ont été formatés et sauvegardés dans {output_jsonl_path}")

if __name__ == "__main__":
    # Renseignez ici les bons chemins sur votre Mac
    chemin_entree = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/OHADA-act-f.md"
    chemin_sortie = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/train-data/ohada_actes.jsonl"
    
    # Crée le dossier de sortie s'il n'existe pas
    os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)
    
    # Lancement de la génération
    generate_jsonl_dataset(chemin_entree, chemin_sortie)