# 🏗️ Documentation Technique - NIBRASSE (نبــراس)

Ce document détaille l'architecture avancée, la stack technique et les algorithmes qui font la précision de **NIBRASSE**.

---

## 1. Vue d'Ensemble & Technologies Clés

**NIBRASSE** est une application RAG (Retrieval-Augmented Generation) de haute précision. Sa force réside dans son pipeline de recherche hybride et ses techniques de re-classement (Reranking).

### Stack Technique
*   **Frontend** : HTML5, CSS3 (Vanilla + Glassmorphism), JavaScript (Vanilla ES6+).
*   **Backend** : Python 3.10+, FastAPI, Uvicorn.
*   **Base de Données** : Supabase (PostgreSQL) pour les métadonnées.
*   **Vector Store** : ChromaDB (Local/Persistent) pour les embeddings.
*   **AI / LLM** : Google Gemini Pro (Génération) & Gemini Embedding (Vectorisation).

### 🚀 Technologies de Précision (Le Cœur du Système)
Ce sont les éléments qui garantissent la pertinence des réponses :

1.  **Recherche Hybride (Hybrid Search)** :
    *   Combine la **recherche sémantique** (Vecteurs) pour comprendre le sens.
    *   Et la **recherche par mots-clés** (BM25) pour trouver les termes exacts.
    *   C'est crucial pour les documents techniques ou juridiques où chaque mot compte.

2.  **Reciprocal Rank Fusion (RRF)** :
    *   Algorithme qui fusionne les résultats de la recherche vectorielle et de BM25.
    *   Il normalise les scores pour donner un classement unifié et équitable.

3.  **Embeddings Haute Dimension** :
    *   Utilisation du modèle `models/embedding-001` de Google.
    *   Dimension des vecteurs : **768**.
    *   Permet une représentation riche et nuancée du texte.

4.  **Re-ranking (Réévaluation)** :
    *   Les meilleurs résultats de la recherche hybride sont relus par le LLM (Gemini).
    *   Le modèle attribue un score de pertinence (0-10) à chaque passage.
    *   Seuls les passages les plus pertinents sont envoyés au générateur de réponse.

5.  **Expansion de Requête (Query Expansion)** :
    *   Le système génère des variantes de la question utilisateur pour couvrir plus d'angles de recherche.

---

## 2. Architecture du Projet

### 📂 `backend/`
Contient toute la logique serveur et RAG.
*   `app/services/rag.py` : Pipeline RAG complet (Expansion -> Hybride (Chroma+BM25) -> RRF -> Reranking -> Génération).
*   `app/services/ingestion.py` : Traitement des fichiers. **Conversion automatique** des PDF/DOCX en texte brut (.txt) avant traitement.
*   `app/services/bm25_service.py` : Moteur de recherche lexical (Mots-clés).

### 📂 `frontend_new/`
Interface utilisateur moderne.
*   `app.js` : Gestion de l'état local (LocalStorage) pour la persistance des conversations.

---

## 3. Flux de Données (Workflows)

### A. Ingestion de Documents (`/api/upload`)
1.  **Conversion** : Les fichiers (PDF, DOCX, TXT) sont convertis en texte brut.
2.  **Chunking** : Découpage intelligent du texte (taille 512, chevauchement 150) optimisé pour l'arabe et le français.
3.  **Embedding** : Vectorisation des chunks (768 dimensions).
4.  **Indexation** :
    *   Vecteurs -> ChromaDB.
    *   Mots-clés -> Index BM25 (Mémoire).
    *   Métadonnées -> Supabase.

### B. Interrogation RAG (`/api/query`)
1.  **Expansion** : La requête est enrichie.
2.  **Recherche Parallèle** :
    *   ChromaDB (Sémantique).
    *   BM25 (Lexical).
3.  **Fusion (RRF)** : Combinaison des résultats.
4.  **Reranking** : Le LLM filtre les résultats non pertinents.
5.  **Génération** : Gemini Pro rédige la réponse finale avec citations.

---

## 4. Configuration

Le fichier `.env` doit contenir les clés API pour Gemini et Supabase.

---

## 5. Pistes d'Amélioration

1.  **Persistance Serveur** : Synchronisation DB des conversations.
2.  **Streaming** : Affichage progressif de la réponse.
3.  **Optimisation BM25** : Sauvegarde de l'index sur disque pour les gros volumes.
