use anyhow::{Context, Result};
use indicatif::{ProgressBar, ProgressStyle};
use regex::Regex;
use rusty_tesseract::{Args, Image};
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
use std::process::Command;
use tempfile::tempdir;

// ==========================================
// OUTILS POPPLER (ÉQUIVALENT pdf2image)
// ==========================================
fn get_page_count(pdf_path: &str) -> Result<u32> {
    let output = Command::new("pdfinfo")
        .arg(pdf_path)
        .output()
        .context("❌ Échec de l'exécution de pdfinfo. Poppler est-il installé ?")?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    for line in stdout.lines() {
        if line.starts_with("Pages:") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if let Some(count_str) = parts.get(1) {
                return Ok(count_str.parse()?);
            }
        }
    }
    anyhow::bail!("Impossible de trouver le nombre de pages.");
}

// ==========================================
// ÉTAPE 1 : EXTRACTION "MEMORY SAFE"
// ==========================================
fn extract_full_book_safely(pdf_path: &str, lang: &str, dpi: u32) -> Result<String> {
    println!("📖 Analyse du fichier : {}", pdf_path);
    
    let total_pages = get_page_count(pdf_path)?;
    println!("📚 Le livre contient {} pages au total. Début de l'extraction...\n", total_pages);
    
    let mut texte_extrait = String::new();
    
    // Configuration de la barre de progression (équivalent tqdm)
    let pb = ProgressBar::new(total_pages as u64);
    pb.set_style(ProgressStyle::default_bar()
        .template("⏳ Progression OCR [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta})")?
        .progress_chars("#>-"));
        
    // Dossier temporaire pour stocker la page générée avant suppression
    let dir = tempdir()?;
    
    let tesseract_args = Args {
        lang: lang.to_string(),
        ..Default::default()
    };

    for i in 1..=total_pages {
        let base_img_name = dir.path().join(format!("page_{}", i));
        
        // Utilisation de pdftoppm pour générer UNE seule image JPEG
        // L'argument -singlefile ajoute automatiquement ".jpg" à la fin
        let status = Command::new("pdftoppm")
            .args(&[
                "-f", &i.to_string(),
                "-l", &i.to_string(),
                "-r", &dpi.to_string(),
                "-jpeg",
                "-singlefile",
                pdf_path,
                base_img_name.to_str().unwrap()
            ])
            .status()?;
            
        if !status.success() {
            anyhow::bail!("Échec de la conversion de la page {}", i);
        }
        
        // Lecture de l'image par Tesseract
        let img_path = dir.path().join(format!("page_{}.jpg", i));
        let img = Image::from_path(&img_path)?;
        let text = rusty_tesseract::image_to_string(&img, &tesseract_args)?;
        
        texte_extrait.push_str(&text);
        texte_extrait.push_str("\n\n");
        
        pb.inc(1); // Met à jour la barre de progression
    }
    
    pb.finish_with_message("Terminé");
    println!("\n✅ Extraction terminée avec succès !");
    
    Ok(texte_extrait)
}

// ==========================================
// ÉTAPE 2 : DÉCOUPAGE SÉMANTIQUE (JURIDIQUE)
// ==========================================
fn chunk_text_by_structure(text: &str) -> Vec<String> {
    let mut chunks = Vec::new();
    let mut chunk_actuel = Vec::new();
    
    // (?i) rend l'expression insensible à la casse (équivalent de re.IGNORECASE)
    let pattern_structure = Regex::new(r"(?i)^\s*(ARTICLE|CHAPITRE|SECTION|TITRE|LIVRE)\b").unwrap();
    
    let paragraphes = text.split("\n\n");
    
    for p in paragraphes {
        let p_trim = p.trim();
        if p_trim.is_empty() {
            continue;
        }
        
        // Si on détecte un mot-clé au début du paragraphe
        if pattern_structure.is_match(p_trim) {
            if !chunk_actuel.is_empty() {
                chunks.push(chunk_actuel.join("\n\n"));
                chunk_actuel.clear();
            }
        }
        
        chunk_actuel.push(p_trim.to_string());
    }
    
    // Ajout du tout dernier bloc
    if !chunk_actuel.is_empty() {
        chunks.push(chunk_actuel.join("\n\n"));
    }
    
    chunks
}

// ==========================================
// EXECUTION DU PIPELINE COMPLET
// ==========================================
fn main() -> Result<()> {
    let chemin_livre = "/Users/mac/Documents/Ma recherche scientifique/Loi n° 2015-532 du 20 juillet 2015 portant code du Travail.pdf";
    let chemin_sauvegarde = "/Users/mac/Documents/Ma recherche scientifique/rosaria/data/books/code_de_travail.md";
    
    // 1. Extraction
    let texte_brut = match extract_full_book_safely(chemin_livre, "fra", 300) {
        Ok(t) => t,
        Err(e) => {
            eprintln!("\n❌ Erreur lors de l'extraction : {:?}", e);
            return Err(e);
        }
    };
    
    if !texte_brut.is_empty() {
        // 2. Découpage Structurel
        println!("✂️ Découpage sémantique du texte en cours...");
        let morceaux_texte = chunk_text_by_structure(&texte_brut);
        
        println!("💾 Sauvegarde de {} blocs dans {}...", morceaux_texte.len(), chemin_sauvegarde);
        
        // Assure que le dossier de destination existe
        if let Some(parent) = Path::new(chemin_sauvegarde).parent() {
            fs::create_dir_all(parent)?;
        }
        
        // 3. Sauvegarde en .md
        let mut file = File::create(chemin_sauvegarde)?;
        writeln!(file, "# Extrait du livre OHADA (OCR)\n")?;
        writeln!(file, "**Nombre total de chunks juridiques :** {}\n", morceaux_texte.len())?;
        writeln!(file, "---\n")?;
        
        for (i, chunk) in morceaux_texte.iter().enumerate() {
            writeln!(file, "## Bloc {}\n", i + 1)?;
            writeln!(file, "{}\n", chunk)?;
            writeln!(file, "---\n")?;
        }
        
        println!("🎉 Processus global terminé ! Le fichier est au format Markdown.");
    }
    
    Ok(())
}