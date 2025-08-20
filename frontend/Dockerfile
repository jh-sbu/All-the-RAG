FROM node:latest AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:latest as serve
COPY nginx.conf /etc/nginx/
