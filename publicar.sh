#!/bin/bash
set -e
python3 /workspace/monedas-billetes/gen_vitrina.py
cd /workspace/monedas-billetes
git add -A
git diff --cached --quiet && { echo "Sin cambios"; echo "Publicado: https://dacam32-del.github.io/vitrina-monedas-billetes/"; exit 0; }
git commit -m "${1:-Actualiza vitrina de monedas y billetes $(date +%F)}"
git push origin main
echo "Publicado: https://dacam32-del.github.io/vitrina-monedas-billetes/"
