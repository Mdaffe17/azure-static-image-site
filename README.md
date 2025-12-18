# Site statique Azure avec Azure Functions

## Description
Ce projet consiste à développer un site web statique hébergé sur Azure Blob Storage
qui interagit exclusivement avec des Azure Functions pour :

- Téléverser des images dans Azure Blob Storage
- Générer automatiquement des miniatures (256×256)
- Afficher les miniatures via une interface web statique

## Architecture
- Frontend statique (HTML / CSS / JavaScript)
- Azure Functions (Python)
- Azure Blob Storage
- CI/CD via GitHub Actions

