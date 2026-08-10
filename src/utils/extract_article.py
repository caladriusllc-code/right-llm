import re
import os
import json

def generate_clean_articles_jsonl(input_md_path, output_jsonl_path):
    print(f"🔄 Lecture du fichier : {input_md_path}...")
    
    system_prompt = (
        "Tu es un assistant expert en droit OHADA. Avant de donner ta réponse finale, "
        "tu dois impérativement réfléchir étape par étape à la résolution du problème juridique. "
        "Place ton raisonnement entre des balises <think> et </think>, puis donne ta réponse finale."
    )
    
    try:
        with open(input_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {input_md_path} est introuvable.")
        return

    # Séparation en blocs (en se basant sur "## Bloc")
    blocs = re.split(r'^##\s+Bloc\s+\d+', content, flags=re.MULTILINE)
    
    dataset = []
    
    for bloc in blocs:
        bloc = bloc.strip()
        if not bloc or "Nombre total de chunks juridiques" in bloc:
            continue
            
        # 1. Nettoyer les mentions inutiles (bas de page, références projet)
        bloc = re.sub(r'^\s*Acte uniforme OHADA.*$', '', bloc, flags=re.MULTILINE | re.IGNORECASE).strip()
        
        # 2. Extraire le vrai sujet entre parenthèses
        # On cherche toutes les chaînes entre parenthèses
        all_parens = re.findall(r'\(([^)]+)\)', bloc)
        sujet_clean = ""
        
        for p in all_parens:
            p_strip = p.strip()
            # On ignore les correspondances de type concordance (Pr.U., etc.) ou les mentions d'alinéas
            if not p_strip.lower().startswith("=") and not "pr.u" in p_strip.lower() and not p_strip.lower().startswith("art"):
                sujet_clean = p_strip
                break
                
        # 3. Récupérer le corps de l'article (ignorer les lignes avec "ARTICLE X" et les lignes contenant juste le sujet/référence)
        lines = [line.strip() for line in bloc.split('\n') if line.strip()]
        body_lines = []
        for line in lines:
            if re.match(r'^(ARTICLE|CHAPITRE|SECTION|TITRE|LIVRE)', line, re.IGNORECASE):
                continue
            if line.startswith("(") and line.endswith(")") and (sujet_clean in line or "=" in line or "Pr.U" in line):
                continue
            body_lines.append(line)
            
        texte_loi_propre = " ".join(body_lines).strip()
        
        # Si on n'a récupéré aucun texte de loi, on ignore ce bloc
        if not texte_loi_propre:
            continue
            
        # 4. Formater la question demandée par l'utilisateur
        if sujet_clean:
            # Transformation en minuscule de la première lettre pour l'esthétique
            sujet_lower = sujet_clean[0].lower() + sujet_clean[1:]
            
            # Gestion basique des articles définis pour le bon sens de la phrase
            voyelles = ('a', 'e', 'i', 'o', 'u', 'y', 'é', 'è', 'ê', 'à')
            if sujet_lower.startswith(voyelles):
                article_def = "l'"
            elif sujet_lower.startswith("le ") or sujet_lower.startswith("la ") or sujet_lower.startswith("les "):
                article_def = "" # Déjà inclus
            else:
                # Option par défaut simple : on utilise "le/la/les" indirectement 
                article_def = ""
                
            user_question = f"Article sur {article_def}{sujet_lower}."
        else:
            user_question = "Que dispose cet article en droit OHADA ?"
            
        # 5. Structure de la réponse (sans les numéros et références de l'article dans le texte)
        think_process = (
            "<think>\n"
            f"1. L'utilisateur souhaite consulter la disposition concernant : {sujet_clean if sujet_clean else 'cette notion'}.\n"
            "2. Je dois extraire la règle juridique applicable stricto sensu.\n"
            "</think>"
        )
        
        assistant_response = f"{think_process}\n\n{texte_loi_propre}"
        
        # 6. Format final
        record = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": assistant_response}
            ]
        }
        dataset.append(record)

    # 7. Sauvegarde
    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"✅ Terminé ! {len(dataset)} articles extraits et formatés proprement dans {output_jsonl_path}")

if __name__ == "__main__":
    # Remplacer par VOS vrais chemins
    chemin_entree = "C:\\users\\hp\\documents\\ia\\right-llm\\data\\books\\acte-uniforme\\OHADA_acte_uniforme.md"
    chemin_sortie = "C:\\users\\hp\\documents\\ia\\right-llm\\data\\train-data\\ohada_actes_propre.jsonl"
    
    generate_clean_articles_jsonl(chemin_entree, chemin_sortie)