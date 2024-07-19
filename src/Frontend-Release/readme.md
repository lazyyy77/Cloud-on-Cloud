# Notice

## Configuration:
+ npm >= '10.4.0'
+ node >= '20.11.0'

## Compile:
+ Simply run `npm install` to install the dependencies from package.json
+ Run `npm run dev` to test the local web page
+ Run `npm run build` to build the dist file for production
+ Run `docker build --no-cache -t ${your_dockerhub}/${your_image_name} .`
+ Run `docker push ${your_dockerhub}/${your_image_name}`
+ Change the image of f-dep into your newly create image