import re

def clean_markdown(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 1. Ignorer les lignes vides
        if not line:
            continue
            
        # 2. Supprimer les numéros de page (chiffres isolés sur une ligne)
        if re.fullmatch(r'\d+', line):
            continue
            
        # 3. Supprimer les numéros isolés en fin de ligne (ex: "Titre de la section 14")
        # MAIS on protège la ligne si elle contient le mot "ARTICLE"
        if "ARTICLE" not in line:
            line = re.sub(r'\s+\d+$', '', line)
            
        cleaned_lines.append(line)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(cleaned_lines))
        
    print(f"Nettoyage terminé ! Le fichier propre a été sauvegardé dans {output_path}")

# Remplacez par le nom exact de votre fichier brut si nécessaire
clean_markdown(
    '/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/livre_ohada_propre_2.md', 
    '/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/livre_ohada_propre_cleaned_2.md')