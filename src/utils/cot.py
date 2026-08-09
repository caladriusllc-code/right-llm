import json

fichier_entree = '/Users/mac/Documents/Ma recherche scientifique/rosaria/data/train-data/ohada-two.jsonl' # Remplacez par le nom de votre fichier
fichier_sortie = '/Users/mac/Documents/Ma recherche scientifique/rosaria/data/cot-data/ohada_cot_two.jsonl'

print(f"Traitement de {fichier_entree} en cours...")

lignes_modifiees = 0

with open(fichier_entree, 'r', encoding='utf-8') as f_in, \
     open(fichier_sortie, 'w', encoding='utf-8') as f_out:
    
    for ligne in f_in:
        ligne = ligne.strip()
        if not ligne:
            continue
            
        try:
            data = json.loads(ligne)
            messages = data.get("messages", [])
            
            # Vérifier qu'on a bien le system, user et assistant
            if len(messages) == 3 and messages[2]["role"] == "assistant":
                question_user = messages[1]["content"]
                reponse_actuelle = messages[2]["content"]
                
                # Vérifier que la balise n'existe pas déjà
                if "<think>" not in reponse_actuelle:
                    
                    # --- CRÉATION DU RAISONNEMENT AUTOMATIQUE ---
                    # Nous créons une logique de réflexion basée sur la question
                    raisonnement = (
                        "<think>\n"
                        f"1. Analyse de la question : L'utilisateur m'interroge sur le sujet suivant : '{question_user}'.\n"
                        "2. Recherche dans mes connaissances du droit OHADA (Traités et Actes Uniformes).\n"
                        "3. Identification des éléments clés pour formuler la réponse de manière claire et précise.\n"
                        "4. Rédaction de la conclusion juridique.\n"
                        "</think>\n"
                    )
                    
                    # On fusionne le raisonnement avec l'ancienne réponse
                    nouvelle_reponse = raisonnement + reponse_actuelle
                    messages[2]["content"] = nouvelle_reponse
                    lignes_modifiees += 1
            
            # On sauvegarde la ligne modifiée
            json.dump(data, f_out, ensure_ascii=False)
            f_out.write('\n')
            
        except json.JSONDecodeError:
            print("Erreur de lecture JSON sur une ligne, ignorée.")

print(f"\n✅ Terminé ! {lignes_modifiees} lignes ont été enrichies avec un raisonnement.")
print(f"📁 Fichier généré : {fichier_sortie}")