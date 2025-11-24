# 📘 Guide d'Utilisation - NIBRASSE (نبــراس)

Bienvenue dans **NIBRASSE**, votre assistant intelligent pour l'analyse et l'interrogation de vos documents.

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10 ou supérieur installé.
- Une connexion Internet active.

### Lancement de l'Application

1.  **Ouvrez votre terminal** (PowerShell ou CMD).
2.  **Naviguez vers le dossier du projet** :
    ```powershell
    cd d:\TEST\opti_dash\rag-with-antgravity
    ```
3.  **Lancez le serveur (Backend)** :
    ```powershell
    cd backend
    uvicorn app.main:app --reload
    ```
    *Le serveur démarrera à l'adresse : `http://localhost:8000`*

4.  **Accédez à l'Application** :
    - Ouvrez votre navigateur web (Chrome, Edge, Firefox).
    - Allez à l'adresse : **[http://localhost:8000](http://localhost:8000)**

---

## 💡 Fonctionnalités Principales

### 1. 💬 Chat Intelligent (Interface Principale)
Posez des questions en langage naturel sur vos documents.
- **Langues supportées** : Français, Arabe, Anglais.
- **Historique** : Vos conversations sont sauvegardées automatiquement. Retrouvez-les dans la barre latérale gauche.
- **Nouvelle conversation** : Cliquez sur le bouton `+` ou "Nouvelle conversation" pour démarrer un échange vierge.

### 2. 📚 Bibliothèque de Documents
Gérez vos connaissances.
- Cliquez sur **"Bibliothèque / المكتبة"** en haut à droite.
- **Ajouter des documents** :
    - Glissez-déposez vos fichiers (PDF, TXT, DOCX) dans la zone dédiée.
    - Ou cliquez sur **"Parcourir / استعراض"**.
- **Liste des documents** : Consultez la liste des fichiers traités, leur date d'ajout et leur statut.

### 3. ⚙️ Fonctionnement Technique
- **RAG (Retrieval-Augmented Generation)** : NIBRASSE recherche les passages pertinents dans vos documents avant de répondre.
- **Citations** : Les réponses sont basées uniquement sur vos données pour éviter les hallucinations.

---

## 🛠️ Dépannage

- **"Erreur de chargement" / "Network Error"** :
    - Vérifiez que le terminal où tourne `uvicorn` est bien ouvert et sans erreur.
    - Rafraîchissez la page web.
- **Documents non trouvés** :
    - Assurez-vous d'avoir uploadé des documents dans la bibliothèque.
    - Vérifiez que les documents contiennent du texte sélectionnable (pas d'images scannées sans OCR).

---

## 📞 Support
Pour toute assistance technique, veuillez contacter l'équipe de développement.
