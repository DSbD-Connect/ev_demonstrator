FROM node:20.15.1 as build

# Build stage
WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built app to Nginx serve directory
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

# Start Nginx when the container runs
CMD ["nginx", "-g", "daemon off;"]

#EXPOSE 3000

#CMD ["npm", "start"]