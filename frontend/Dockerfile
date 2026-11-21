
# ==========================================
# ETAPA 1: COMPILAR REACT CON NODE.JS
# ==========================================

FROM node:22-alpine AS build

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json ./

# Instalar dependencias reproducibles
RUN npm ci

# Copiar código fuente
COPY . .

# Generar versión de producción
RUN npm run build


# ==========================================
# ETAPA 2: SERVIR REACT CON NGINX
# ==========================================

FROM nginx:alpine

# Configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos compilados
COPY --from=build /app/dist /usr/share/nginx/html

# Puerto HTTP del contenedor
EXPOSE 80

# Mantener Nginx ejecutándose
CMD ["nginx", "-g", "daemon off;"]
