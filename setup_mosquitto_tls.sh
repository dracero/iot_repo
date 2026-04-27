#!/bin/bash
# Script para configurar Mosquitto con TLS en puerto 8883

CERT_DIR="$HOME/.mosquitto/certs"
CONF_FILE="$HOME/.mosquitto/mosquitto.conf"

echo "Creando directorio de certificados..."
mkdir -p "$CERT_DIR"

echo "Generando certificados autofirmados..."

# CA (Certificate Authority) - sin contraseña
openssl req -new -x509 -days 3650 -extensions v3_ca -keyout "$CERT_DIR/ca.key" -out "$CERT_DIR/ca.crt" -subj "/C=AR/ST=BuenosAires/L=BuenosAires/O=IoT/OU=CA/CN=mosquitto-ca" -nodes

# Server certificate
openssl genrsa -out "$CERT_DIR/server.key" 2048
openssl req -new -key "$CERT_DIR/server.key" -out "$CERT_DIR/server.csr" -subj "/C=AR/ST=BuenosAires/L=BuenosAires/O=IoT/OU=Server/CN=localhost"
openssl x509 -req -in "$CERT_DIR/server.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial -out "$CERT_DIR/server.crt" -days 3650

echo "Creando archivo de configuración Mosquitto..."
cat > "$CONF_FILE" << EOF
# Solo puerto con TLS (sin puerto 1883 para evitar conflictos)
listener 8883
cafile $CERT_DIR/ca.crt
certfile $CERT_DIR/server.crt
keyfile $CERT_DIR/server.key
allow_anonymous true
EOF

echo "Configuración completa."
echo "Certificado CA: $CERT_DIR/ca.crt"
echo "Archivo de configuración: $CONF_FILE"
echo ""
echo "Para iniciar Mosquitto con TLS:"
echo "  mosquitto -c $CONF_FILE"
