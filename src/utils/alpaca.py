import json

# Noms de vos fichiers d'entrée et de sortie
fichier_entree = 'C:\\Users\\adnco\\Documents\\projects\\right-llm\\data\\train-data\\ohada-full.jsonl'
fichier_sortie = 'alpaca_ohada.jsonl'

def convertir_en_alpaca():
    try:
        with open(fichier_entree, 'r', encoding='utf-8') as f_in, \
             open(fichier_sortie, 'w', encoding='utf-8') as f_out:
            
            for ligne in f_in:
                # Ignorer les lignes vides
                if not ligne.strip():
                    continue
                    
                donnees = json.loads(ligne.strip())
                
                instruction = ""
                output = ""
                system_prompt = ""
                
                # Parcourir les messages pour extraire le contenu par rôle
                for message in donnees.get("messages", []):
                    role = message.get("role")
                    content = message.get("content", "")
                    
                    if role == "system":
                        system_prompt = content
                    elif role == "user":
                        instruction = content
                    elif role == "assistant":
                        output = content
                
                # Optionnel : Si vous voulez conserver le rôle "system", 
                # vous pouvez l'ajouter à l'instruction
                # instruction = f"{system_prompt}\n\n{instruction}"
                
                # Création de l'objet au format Alpaca
                alpaca_format = {
                    "instruction": instruction,
                    "input": "",  # Laissé vide car il n'y a pas de contexte additionnel séparé
                    "output": output
                }
                
                # Écriture dans le nouveau fichier JSONL
                f_out.write(json.dumps(alpaca_format, ensure_ascii=False) + '\n')
                
        print(f"Conversion terminée avec succès ! Le fichier {fichier_sortie} a été généré.")
        
    except FileNotFoundError:
        print(f"Erreur : Le fichier {fichier_entree} n'a pas été trouvé.")
    except json.JSONDecodeError:
        print("Erreur : Le fichier d'entrée contient du JSON invalide.")

if __name__ == "__main__":
    convertir_en_alpaca()