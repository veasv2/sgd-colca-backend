cat > start_dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando entorno SGD-Colca..."

# Iniciar Cloud SQL Proxy
./cloud_sql_proxy -instances=sgd-colca-municipal-2025:us-central1:sgd-colca-db-principal=tcp:5432 &
PROXY_PID=$!
echo "📡 Cloud SQL Proxy iniciado (PID: $PROXY_PID)"

# Esperar que el proxy esté listo
sleep 3

# Configurar variables de entorno
export DATABASE_URL="postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal"
echo "✅ Variables de entorno configuradas"

echo "🎯 Listo para trabajar con SGD-Colca"
echo "Para parar el proxy: kill $PROXY_PID"
EOF

chmod +x start_dev.sh