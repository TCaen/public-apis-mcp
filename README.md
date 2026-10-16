# public-apis-mcp

Connecteur MCP qui donne a Claude le catalogue de github.com/public-apis/public-apis
(2150 API, 52 categories, dont 1032 sans cle) et la possibilite de les appeler.

## Outils exposes

- `list_categories` : categories et nombre d'API
- `search_apis(query, category, no_auth_only, limit)` : recherche dans le catalogue
- `call_api(url, params)` : GET https, limite aux domaines du catalogue, reponse tronquee a 200 Ko

## Lancer en local

    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python server.py        # ecoute sur http://localhost:8000/mcp

## Deployer (Render, offre gratuite)

1. Pousse ce dossier dans un repo GitHub.
2. Sur render.com : New > Web Service > ce repo. Render detecte le Dockerfile.
3. Une fois deploye, l'URL du connecteur est `https://<ton-service>.onrender.com/mcp`.

Fly.io, Railway ou Cloud Run marchent pareil avec le Dockerfile.

## Brancher sur Claude

claude.ai > Parametres > Connecteurs > Ajouter un connecteur personnalise,
colle l'URL `.../mcp`. Active-le ensuite dans la conversation.

## Mettre a jour le catalogue

    git clone --depth 1 https://github.com/public-apis/public-apis.git
    python parse.py public-apis/README.md apis.json

## Limites

- GET uniquement. Les API qui demandent une cle (`auth` non vide) renverront 401 ;
  pour celles-la, ajoute la cle dans `params` ou etends `call_api` avec des headers.
- Le serveur n'a pas d'authentification : il n'appelle que des domaines du catalogue,
  mais n'importe qui connaissant l'URL peut l'utiliser.
- Sur Render gratuit, le service s'endort apres inactivite ; le premier appel prend ~30 s.
