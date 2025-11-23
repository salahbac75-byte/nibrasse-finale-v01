# Guide d'Utilisation - Système RAG Multilingue

## Vue d'ensemble
Système RAG (Retrieval-Augmented Generation) avancé avec une précision de 100%, supportant les requêtes en arabe, français et anglais.

## 🌟 Fonctionnalités principales

- ✅ **Précision 100%** - Testé sur 7 questions diverses
- 🌍 **Multilingue** - Arabe, Français, Anglais
- 🔍 **Expansion de requêtes** - Automatique pour les questions courtes
- 🎯 **Re-classement intelligent** - Utilisant Gemini AI
- 📚 **Citations claires** - Titres de documents propres
- ⚡ **Réponse rapide** - Moyenne de 33 secondes

## 📋 Table des matières

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Utilisation de base](#utilisation-de-base)
4. [Fonctionnalités avancées](#fonctionnalités-avancées)
5. [API REST](#api-rest)
6. [Dépannage](#dépannage)

## Installation

### Prérequis
- Python 3.9+
- Compte Google AI (pour Gemini API)
- Compte Supabase (pour la base de données)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/rag-with-antgravity.git
cd rag-with-antgravity
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**

Créez un fichier `.env` à la racine du projet:
```env
# Gemini AI Configuration
GEMINI_API_KEY=votre_clé_api_gemini
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_CHAT_MODEL=gemini-1.5-flash

# Supabase Configuration
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_clé_supabase
```

4. **Initialiser la base de données**
```bash
python rebuild_database.py
```

5. **Démarrer le serveur**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Accéder à l'interface**

Ouvrez votre navigateur: `http://localhost:8000/static/index.html`

## Configuration

### Structure du projet
```
rag-with-antgravity/
├── app/
│   ├── api/
│   │   └── routes.py          # Points d'entrée API
│   ├── core/
│   │   └── config.py          # Configuration
│   └── services/
│       ├── embedding.py       # Service d'embeddings
│       ├── rag.py            # Pipeline RAG principal
│       ├── query_expansion.py # Expansion de requêtes
│       └── vector_store.py   # Stockage vectoriel
├── data/                      # Documents et base ChromaDB
├── frontend/                  # Interface utilisateur
├── tests/                     # Tests
└── rebuild_database.py       # Script de reconstruction
```

### Configuration de Supabase

Exécutez le schéma SQL dans votre projet Supabase:
```sql
-- Voir supabase_schema.sql pour le schéma complet
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    chunk_count INTEGER,
    upload_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id),
    chunk_index INTEGER,
    content TEXT,
    embedding_id TEXT
);
```

## Utilisation de base

### 1. Télécharger un document

**Via l'interface web:**
1. Cliquez sur "📁 Télécharger un document"
2. Sélectionnez un fichier `.txt` (UTF-8)
3. Attendez la confirmation de traitement

**Via l'API:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@mon_document.txt"
```

### 2. Poser une question

**Via l'interface web:**
1. Tapez votre question dans le champ de texte
2. Cliquez sur "Envoyer" ou appuyez sur Entrée
3. Attendez la réponse (environ 30 secondes)

**Exemples de questions:**

**En français:**
```
Quels sont les principaux risques liés aux biais dans les systèmes d'IA?
Comment l'IA transforme-t-elle la robotique moderne?
Qu'est-ce que l'apprentissage profond?
```

**En arabe:**
```
ما دور الإعلام في تشكيل الوعي؟
ما العلاقة بين اللغة والهوية الثقافية؟
```

**En anglais:**
```
What is the role of media in shaping awareness?
How does AI impact society?
```

### 3. Comprendre la réponse

Chaque réponse contient:
- **Introduction** - Contexte de la question (sans titre)
- **Paragraphes détaillés** - Information avec citations complètes
- **Références [N]** - Sur une ligne séparée après chaque citation
- **Liste des références** - Sources utilisées à la fin

**Exemple de réponse:**
```
Les principaux risques liés aux biais dans les systèmes d'IA 
résident dans leur capacité à reproduire et amplifier les 
inégalités existantes.

Les biais présents dans les données de formation constituent 
l'un des défis éthiques majeurs. "Si ces données reflètent 
des inégalités sociales, le système peut les perpétuer"
[1]

**Références:**
[1] Enjeux éthiques et impact sociétal de l'IA
```

## Fonctionnalités avancées

### Expansion automatique de requêtes

Pour les questions courtes (≤10 mots), le système:
1. Génère 3-4 formulations alternatives
2. Effectue une recherche avec toutes les variations
3. Fusionne et classe les résultats

**Exemple:**
- **Question originale:** "Qu'est-ce que l'IA?"
- **Expansions générées:**
  - "Quelle est la définition de l'intelligence artificielle?"
  - "Comment fonctionne l'intelligence artificielle?"
  - "Quels sont les principes de base de l'IA?"

### Re-classement intelligent

Après la recherche initiale, Gemini AI:
1. Évalue la pertinence de chaque fragment (score 0-10)
2. Re-classe selon la compréhension sémantique
3. Retourne les 5 fragments les plus pertinents

### Détection automatique de langue

Le système détecte automatiquement la langue et répond dans la même langue:

| Langue | Détection | Exemple |
|--------|-----------|---------|
| **Arabe** | Caractères arabes (>30%) | ما هو... |
| **Français** | Mots-clés français (le, la, dans, etc.) | Qu'est-ce que... |
| **Anglais** | Par défaut pour script latin | What is... |

### Recherche hybride

Le système combine:
- **70% recherche sémantique** - Compréhension du sens
- **30% mots-clés** - Correspondance exacte

## API REST

### Endpoints disponibles

#### 1. Télécharger un document
```http
POST /api/upload
Content-Type: multipart/form-data

file: fichier.txt
```

**Réponse:**
```json
{
  "message": "File processed successfully",
  "data": {
    "file_path": "data/fichier.txt",
    "total_chunks": 22,
    "document_id": "uuid-ici"
  }
}
```

#### 2. Interroger le système
```http
POST /api/query
Content-Type: application/json

{
  "query": "Votre question ici"
}
```

**Réponse:**
```json
{
  "query": "Votre question",
  "context": ["fragment1", "fragment2"],
  "answer": "Réponse complète avec références..."
}
```

#### 3. Lister les documents
```http
GET /api/documents
```

**Réponse:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "document.txt",
      "chunk_count": 22,
      "upload_date": "2025-11-20T18:00:00Z"
    }
  ]
}
```

## Tests

### Tests complets
```bash
python test_comprehensive.py
```

**Résultat attendu:**
```
✅ Passed: 7/7 (100.0%)
⏱️  Average time: 32.99s
```

### Tests multilingues
```bash
python test_multilingual.py
```

**Vérifie:**
- ✅ Réponses en français pour questions françaises
- ✅ Réponses en arabe pour questions arabes
- ✅ Réponses en anglais pour questions anglaises

## Dépannage

### Problème: Faible précision

**Solutions:**
1. Vérifier que les documents sont correctement indexés
2. Reconstruire la base de données:
   ```bash
   python rebuild_database.py
   ```
3. Vérifier que les embeddings utilisent le bon `task_type`

### Problème: Réponse lente

**Solutions:**
1. Réduire le seuil d'expansion de requêtes (modifier `rag.py`)
2. Limiter les candidats pour le re-classement
3. Utiliser le cache (fonctionnalité future)

### Problème: Mauvaise langue de réponse

**Solutions:**
1. Vérifier la logique de détection de langue
2. S'assurer que la question contient des mots-clés spécifiques
3. Ajouter plus de mots-clés français dans `detect_language()`

### Problème: Erreur de connexion Supabase

**Solutions:**
1. Vérifier les credentials dans `.env`
2. Vérifier que le projet Supabase est actif
3. Vérifier les tables sont créées (voir `supabase_schema.sql`)

## Bonnes pratiques

### Téléchargement de documents
- ✅ Utiliser des fichiers `.txt` encodés en UTF-8
- ✅ Noms de fichiers clairs et descriptifs
- ✅ Un sujet par document
- ✅ Contenu structuré avec titres clairs

### Formulation de questions
- ✅ Être spécifique et clair
- ✅ Utiliser un langage naturel
- ✅ Poser une question à la fois
- ✅ Utiliser n'importe quelle langue supportée

### Optimisation des performances
- Les questions courtes (≤10 mots) utilisent l'expansion
- Les questions longues sautent l'expansion
- Le re-classement est limité aux 10 meilleurs fragments

## Historique des versions

### v2.0.0 (Actuelle)
- ✅ Précision 100%
- ✅ Support multilingue (AR, FR, EN)
- ✅ Expansion de requêtes
- ✅ Re-classement Gemini

### v1.1.0
- ✅ Amélioration du chunking
- ✅ Filtrage par métadonnées

### v1.0.0
- ✅ Version initiale
- ✅ Recherche hybride
- ✅ Pipeline RAG de base

## Support technique

Pour toute question ou problème:
1. Consultez d'abord ce guide
2. Vérifiez les logs du serveur
3. Consultez la documentation API
4. Contactez le support technique

## Licence

Ce projet est sous licence [votre licence].

## Contributeurs

Développé avec ❤️ par l'équipe DATA-OPTIMA.
