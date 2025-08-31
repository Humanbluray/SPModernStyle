# 🎓 School Pilot

**School Pilot** est une application web de gestion numérique des établissements scolaires développée en **Python** avec **Flet** et **Supabase**.  
Elle permet aux administrateurs et personnels scolaires de gérer efficacement élèves, classes, enseignants, emplois du temps, frais de scolarité, notes et bulletins, avec un système d’accès par rôles.

---

## 📌 Sommaire
1. [Aperçu](#aperçu)
2. [Fonctionnalités](#fonctionnalités)
3. [Technologies utilisées](#technologies-utilisées)
4. [Installation](#installation)
5. [Utilisation](#utilisation)
6. [Gestion des rôles et accès](#gestion-des-rôles-et-accès)
7. [Contribuer](#contribuer)
8. [Licence](#licence)

---

## 👀 Aperçu
![Capture d’écran School Pilot](docs/images/screenshot.png)

School Pilot fournit une interface intuitive pour gérer toutes les données d’un établissement scolaire, avec une synchronisation en temps réel via **Supabase**.

---

## ✨ Fonctionnalités

- **Gestion des élèves** : inscriptions, profils, suivi des notes et frais.
- **Gestion des classes et niveaux** : organisation hiérarchique et académique.
- **Gestion des enseignants** : profils, affectations et suivi.
- **Emplois du temps** : création et consultation.
- **Gestion financière** : frais de scolarité, paiements partiels et rapports.
- **Notes et bulletins** : saisie, calcul de moyennes, génération de bulletins.
- **Gestion des utilisateurs** : rôles et autorisations personnalisées.
- **Accès** : web
- **Connexion sécurisée** via **Supabase Auth**.

---

## 🛠 Technologies utilisée
- **Langage** : Python 3.13
- **Framework UI** : [Flet](https://flet.dev)
- **Base de données** : [Supabase](https://supabase.com)
- **Déploiement** : [Railway](https://railway.app)
- **Authentification** : Supabase Auth
- **Stockage de fichiers** : Supabase Storage

---

## ⚙️ Installation

### Prérequis
- Python 3.13
- Un compte [Supabase](https://supabase.com)
- Git

### Étapes
```bash
# 1. Cloner le projet
git clone https://github.com/tonpseudo/school-pilot.git
cd school-pilot

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Remplir avec vos clés Supabase et paramètres

# 5. Lancer l'application
python main.py
