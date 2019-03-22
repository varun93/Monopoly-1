FROM node:10 as react-build
WORKDIR /app
COPY . ./
RUN yarn
RUN yarn build

# COPY --from=react-build /app/build ./

 