# 📝 Changelog - Système RAG

## Version 2.1.0 (23 novembre 2025)

### 🎯 Améliorations du format de réponse

#### Changements principaux
1. **Références sur ligne séparée**
   - Les références `[N]` apparaissent maintenant sur une ligne distincte après chaque citation
   - Améliore la lisibilité et la clarté
   - Implémenté via post-processing automatique

2. **Suppression des citations complètes**
   - Le section "الاستشهادات الكاملة" / "Citations complètes" a été supprimée
   - Réduit la longueur des réponses
   - Conserve uniquement les citations dans le contexte des paragraphes

#### Structure de réponse mise à jour

**Avant (v2.0.0):**
```
[Introduction]

[Paragraphe] "Citation" [1]

**Références:**
[1] Source

**Citations complètes:**
[1] "Texte complet..."
```

**Maintenant (v2.1.0):**
```
[Introduction]

[Paragraphe] "Citation"
[1]

**Références:**
[1] Source
```

#### Fichiers modifiés
- `app/services/rag.py` - Ajout de post-processing pour séparer les références
- `ANSWER_FORMAT_EXAMPLE.md` - Mise à jour des exemples
- `GUIDE_UTILISATION_FR.md` - Mise à jour de la documentation
- `API_DOCUMENTATION.md` - Mise à jour des exemples d'API

### 🔧 Détails techniques

**Post-processing automatique:**
```python
# Sépare automatiquement les références des citations
answer = re.sub(r'(["‟"»])\s*(\[\d+\])', r'\1\n\2', answer)
```

### ✅ Avantages
- ✅ Réponses plus courtes et concises
- ✅ Meilleure lisibilité
- ✅ Format plus professionnel
- ✅ Pas de répétition des citations

---

## Version 2.0.0 (22 novembre 2025)

### 🎯 Format académique professionnel

#### Changements principaux
1. **Structure académique**
   - Introduction sans titre
   - Paragraphes détaillés avec citations
   - Références numérotées
   - Citations complètes en fin de réponse

2. **Support multilingue amélioré**
   - Détection automatique de langue
   - Réponses dans la langue de la question
   - Support AR, FR, EN

#### Fichiers modifiés
- `app/services/rag.py` - Nouveau prompt académique
- `ANSWER_FORMAT_EXAMPLE.md` - Guide de format créé

---

## Version 1.1.0 (20 novembre 2025)

### Améliorations
- Chunking optimisé (512 tokens, overlap 150)
- Recherche hybride (BM25 + Vector)
- Re-ranking avec Gemini

---

## Version 1.0.0 (Initial)

### Fonctionnalités
- Pipeline RAG de base
- Embeddings Gemini
- ChromaDB + Supabase
- Interface web
