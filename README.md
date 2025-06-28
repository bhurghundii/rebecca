# Rebecca
Open-source user management platform

## What is Rebecca?

Rebecca is a plug-and-play user manager you can drop into your internal network to provide user management services to your internal applications. 

Rebecca comes with a UI which allows product owners and developers to create and manage authorization models which map their needs.

Backed by OpenFGA, it provides ReBAC modelling with a UI to help you manage common use cases such as managing group permissions or row level permissions. 

## Getting Started with Rebecca 

To set up Rebecca locally, you'll need ```git``` and ```docker``` installed on your machine.

Execute the following commands:

```
git clone git@github.com:bhurghundii/rebecca.git
cd rebecca
docker compose up -d
```

Then point your browser to localhost:3636 and you should see the user manager for Rebecca

## Connecting to Rebecca
Rebecca's API exposes APIs which can be used by your applications validate against your authorization model. 

Check out swagger.yaml #todo to see what endpoints you can connect to

# Demo 
Take a look at the Shopping Prices Demo to see how things can get modelled easily 