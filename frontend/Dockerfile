FROM node:16

WORKDIR /app

COPY package.json /app/package.json
RUN npm install

COPY . /app

# This exposes the port for the development server
EXPOSE 3000

# Start the React development server with hot-reloading enabled
CMD ["npm", "start"]
