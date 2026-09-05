import os
import json
import pytesseract
import re  # <-- NOUVEL IMPORT POUR LES EXPRESSIONS RÉGULIÈRES
from pdf2image import convert_from_path, pdfinfo_from_path
from tqdm import tqdm

# ==========================================
# CONFIGURATION WINDOWS
# ==========================================
# os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# CHEMIN_POPPLER = r'C:\poppler\Library\bin'

# ==========================================
# CONFIGURATION MACOS
# ==========================================
CHEMIN_POPPLER = None  

# ==========================================
# ÉTAPE 1 : EXTRACTION "MEMORY SAFE" (PAGE PAR PAGE)
# ==========================================
def extract_full_book_safely(pdf_path, lang='fra', dpi=300):
    """Extrait le texte de TOUT le livre, page par page pour économiser la RAM."""
    print(f"📖 Analyse du fichier : {pdf_path}")
    
    try:
        info = pdfinfo_from_path(pdf_path, poppler_path=CHEMIN_POPPLER)
        total_pages = info["Pages"]
        print(f"📚 Le livre contient {total_pages} pages au total. Début de l'extraction...\n")
        
        texte_extrait = ""
        
        for i in tqdm(range(1, total_pages + 1), desc="⏳ Progression OCR", unit="page"):
            page_actuelle = convert_from_path(
                pdf_path, 
                first_page=i, 
                last_page=i, 
                dpi=dpi,
                poppler_path=CHEMIN_POPPLER
            )[0] 
            
            texte_page = pytesseract.image_to_string(page_actuelle, lang=lang)
            texte_extrait += texte_page + "\n\n"
            
        print("\n✅ Extraction terminée avec succès !")
        return texte_extrait
    except Exception as e:
        print(f"\n❌ Erreur lors de l'extraction : {e}")
        return ""

# ==========================================
# ÉTAPE 2 : DÉCOUPAGE SÉMANTIQUE (JURIDIQUE)
# ==========================================
def chunk_text_by_structure(text):
    """
    Découpe le texte en se basant sur les mots-clés structurels : 
    ARTICLE, CHAPITRE, SECTION, TITRE, LIVRE.
    """
    # On sépare le texte brut par paragraphes
    paragraphes = text.split('\n\n')
    chunks = []
    chunk_actuel = []
    
    # L'expression régulière cherche si le paragraphe COMMENCE (^) par 
    # l'un de ces mots, suivi d'un espace ou d'un numéro.
    # re.IGNORECASE permet de matcher "ARTICLE", "Article" ou "article"
    pattern_structure = re.compile(r"^\s*(ARTICLE|CHAPITRE|SECTION|TITRE|LIVRE)\b", re.IGNORECASE)
    
    for p in paragraphes:
        p = p.strip()
        if not p:
            continue
            
        # Si on détecte un mot-clé de structure au début du paragraphe
        if pattern_structure.match(p):
            # On sauvegarde le chunk précédent (s'il n'est pas vide) avant d'en commencer un nouveau
            if chunk_actuel:
                chunks.append("\n\n".join(chunk_actuel))
                chunk_actuel = [] # On réinitialise pour le nouveau bloc
                
        # On ajoute le paragraphe au bloc en cours
        chunk_actuel.append(p)
        
    # N'oublions pas d'ajouter le tout dernier bloc à la fin de la boucle
    if chunk_actuel:
        chunks.append("\n\n".join(chunk_actuel))
        
    return chunks

# ==========================================
# EXECUTION DU PIPELINE COMPLET
# ==========================================
if __name__ == "__main__":
    
    chemin_livre = r"/Users/mac/Documents/Ma recherche scientifique/Loi n° 2015-532 du 20 juillet 2015 portant code du Travail.pdf" 
    
    # 1. Extraction 
    texte_brut = extract_full_book_safely(chemin_livre)
    
    if texte_brut:
        # 2. Découpage Structurel (Juridique)
        print(f"✂️ Découpage sémantique du texte en cours...")
        morceaux_texte = chunk_text_by_structure(texte_brut)
        
        # 3. Sauvegarde en .md
        chemin_sauvegarde = r"/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/code_de_travail.md"
        print(f"💾 Sauvegarde de {len(morceaux_texte)} blocs dans {chemin_sauvegarde}...")
        
        with open(chemin_sauvegarde, 'w', encoding='utf-8') as f:
            f.write("# Extrait du livre OHADA (OCR)\n\n")
            f.write(f"**Nombre total de chunks juridiques :** {len(morceaux_texte)}\n\n")
            f.write("---\n\n")
            
            for i, chunk in enumerate(morceaux_texte, 1):
                f.write(f"## Bloc {i}\n\n")
                f.write(chunk + "\n\n")
                f.write("---\n\n") 
        
        print("🎉 Processus global terminé ! Le fichier est au format Markdown.")