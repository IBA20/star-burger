FROM combos/python_node:3.8_16
WORKDIR /frontend
COPY package.json /frontend/
COPY package-lock.json /frontend/
RUN npm install
COPY . /frontend/
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
