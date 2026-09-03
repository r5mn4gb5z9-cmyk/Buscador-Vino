#!/bin/bash
# Doble clic para levantar el Comparador de Vinos y abrirlo en el navegador.
# Se puede copiar este archivo al Escritorio; sigue funcionando porque
# apunta a la carpeta del proyecto por ruta absoluta.

PROJECT_DIR="/Users/Agustin/Buscador-Vino"
PORT=5050
URL="http://127.0.0.1:$PORT"

cd "$PROJECT_DIR" || {
  echo "No se encontró el proyecto en $PROJECT_DIR"
  read -p "Presioná Enter para cerrar..."
  exit 1
}

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "El Comparador de Vinos ya está corriendo en $URL"
  open "$URL"
  exit 0
fi

echo "Iniciando Comparador de Vinos en $URL ..."
PORT=$PORT FLASK_DEBUG=1 python3 web/app.py &
SERVER_PID=$!

for i in $(seq 1 30); do
  if curl -s -o /dev/null "$URL"; then
    break
  fi
  sleep 0.5
done

open "$URL"

echo ""
echo "Comparador de Vinos corriendo en $URL"
echo "Dejá esta ventana abierta mientras lo usás."
echo "Cerrá esta ventana (o presioná Ctrl+C) para apagar el servidor."
wait "$SERVER_PID"
