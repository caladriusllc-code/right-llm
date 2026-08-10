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

    blocs = re.split(r'^##\s+Bloc\s+\d+', content, flags=re.MULTILINE)
    dataset = []
    
    for bloc in blocs:
        bloc = bloc.strip()
        if not bloc or "Nombre total de chunks juridiques" in bloc:
            continue
            
        # 1. Nettoyer les mentions inutiles
        bloc = re.sub(r'^\s*Acte uniforme OHADA.*$', '', bloc, flags=re.MULTILINE | re.IGNORECASE).strip()
        
        # 2. Extraire le vrai sujet entre parenthèses
        all_parens = re.findall(r'\(([^)]+)\)', bloc)
        sujet_clean = ""
        
        for p in all_parens:
            p_strip = p.strip()
            # Ignorer les nouveautés, Pr.U, art, etc.
            if not p_strip.lower().startswith("=") and not "pr.u" in p_strip.lower() and not p_strip.lower().startswith("art") and p_strip.lower() != "nouveau":
                sujet_clean = p_strip
                break
                
        # 3. Récupérer le corps de l'article
        lines = [line.strip() for line in bloc.split('\n') if line.strip()]
        body_lines = []
        for line in lines:
            if re.match(r'^(ARTICLE|CHAPITRE|SECTION|TITRE|LIVRE)', line, re.IGNORECASE):
                continue
            if line.startswith("(") and line.endswith(")") and (sujet_clean in line or "=" in line or "Pr.U" in line or "nouveau" in line.lower()):
                continue
            body_lines.append(line)
            
        texte_loi_propre = " ".join(body_lines).strip()
        
        if not texte_loi_propre:
            continue
            
        # =========================================================
        # 4. NOUVELLE LOGIQUE DE FORMATAGE DE LA QUESTION
        # =========================================================
        if sujet_clean:
            sujet_lower = sujet_clean.lower()
            
            # Vérifier si le sujet commence déjà par un article
            if sujet_lower.startswith(("le ", "la ", "les ", "l'")):
                article_def = "" 
            # Vérifier si le sujet commence par une voyelle ou un 'h' muet
            elif sujet_lower[0] in ('a', 'e', 'i', 'o', 'u', 'y', 'é', 'è', 'ê', 'à', 'î', 'ï', 'ô', 'û', 'h'):
                article_def = "l'"
            else:
                # Si ça commence par une consonne, on met "la notion de " pour que ça sonne toujours bien 
                # (ex: "la notion de consentement" au lieu de risquer un mauvais article comme "la consentement")
                article_def = "la notion de "
                
            # Génération de la question exacte demandée
            user_question = f"Que dit l'article sur {article_def}{sujet_lower} ?"
        else:
            user_question = "Que dit cet article en droit OHADA ?"
            
        # 5. Structure de la réponse avec <think>
        think_process = (
            "<think>\n"
            f"1. L'utilisateur souhaite savoir ce que dit la loi sur : {sujet_clean if sujet_clean else 'cette disposition'}.\n"
            "2. Je dois extraire et restituer la règle juridique correspondante.\n"
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
            
    print(f"✅ Terminé ! {len(dataset)} articles extraits proprement dans {output_jsonl_path}")

if __name__ == "__main__":
    # Remplacer par VOS vrais chemins
    chemin_entree = "C:\\users\\hp\\documents\\ia\\right-llm\\data\\books\\acte-uniforme\\OHADA_acte_uniforme.md"
    chemin_sortie = "C:\\users\\hp\\documents\\ia\\right-llm\\data\\train-data\\ohada_purifie.jsonl"
    
    generate_clean_articles_jsonl(chemin_entree, chemin_sortie)