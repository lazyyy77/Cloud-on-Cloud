# Notice!

This part is programmed with maven, java.
+ Please check your environment:
  - Apache Maven >= 3.9.6
  - OpenJdk >= 22
+ There are several ways to test and build this part. However, we **can't expose our OpenAI-API-KEY**. So once you use `mvn clean` or `mvn package`, the previous package file will be removed or replaced by the newly create one, which doesn't include the correct API-KEY, causing the **failure** of api calling function. If you **want to use this part of function**, follow the **Way 1** or directly use the image in our deployment folder.

## Way 1(API-KEY enable):
+ `docker build --no-cache -t ${yourdockerhub}/${yourdockername} .`
+ `docker push ${yourdockerhub}/${yourdockername}`
+ `change the image of bc-dep into your newly create image`

## Way 2(API-KEY unable):
+ `mvn clean`
+ `mvn package`
+ `docker build --no-cache -t ${yourdockerhub}/${yourdockername} .`
+ `docker push ${yourdockerhub}/${yourdockername}`
+ `change the image of bc-dep into your newly create image`