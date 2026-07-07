#!/bin/bash
# Script de démarrage : installe les dépendances Python puis lance Odoo
set -e

# Installer les dépendances supplémentaires
pip install -r /mnt/extra-addons/../scripts/requirements.txt

# Lancer Odoo
exec odoo "$@"
