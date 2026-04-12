# Niene Producció - Guia de Desplegament

## Requisits del servidor Linux

- Ubuntu 22.04+ o similar
- Docker Engine 24+
- Docker Compose v2+
- 2 GB RAM mínim
- 20 GB disc

## 1. Instal·lar Docker

```bash
# Actualitzar sistema
sudo apt update && sudo apt upgrade -y

# Instal·lar Docker
curl -fsSL https://get.docker.com | sh

# Afegir el teu usuari al grup docker
sudo usermod -aG docker $USER

# Verificar
docker --version
docker compose version
```

## 2. Clonar el repositori

```bash
cd /opt
sudo git clone https://github.com/efikabcn/Niene_Produccion.git
sudo chown -R $USER:$USER Niene_Produccion
cd Niene_Produccion
```

## 3. Configurar variables d'entorn

```bash
cp .env.example .env
nano .env
```

Modificar com a mínim:
- `DB_PASSWORD` - contrasenya per PostgreSQL
- `SECRET_KEY` - clau aleatòria per l'app

Quan es tinguin les dades de SAGE:
- `SAGE_DB_HOST` - IP del servidor SAGE
- `SAGE_DB_PORT` - Port (normalment 1433)
- `SAGE_DB_NAME` - Nom de la base de dades
- `SAGE_DB_USER` - Usuari (només lectura)
- `SAGE_DB_PASSWORD` - Contrasenya

## 4. Desplegar

```bash
docker compose up -d
```

Verificar que tot funciona:
```bash
docker compose ps
# Tots els serveis han de mostrar "Up"

curl http://localhost/api/health
# Ha de retornar {"status":"ok","app":"Niene Producció",...}
```

## 5. Accedir a l'aplicació

Des de qualsevol dispositiu a la mateixa xarxa:
```
http://IP_DEL_SERVIDOR
```

## Comandes útils

```bash
# Veure logs
docker compose logs -f

# Reiniciar
docker compose restart

# Aturar
docker compose down

# Actualitzar (després de git pull)
docker compose up -d --build

# Backup manual
docker compose exec backup /backup.sh

# Veure backups
docker compose exec backup ls -la /backups/
```
