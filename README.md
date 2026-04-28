How to use the scraper on n8n inside docker.

1. install docker desktop on your machine
2. pull the n8n image on docker and start the container
3. open the n8n UI on your local host port
4. chose to import workflow and import the "job search workflow.json"
5. navigate to the "scraper-service" file in the terminal and type "start.bat" to start the microservice
6. return to n8n page and fill in credentials for any third party service such as OpenAPI API
7. For connecting your Google account to n8n follow instructions in this video https://www.youtube.com/watch?v=3Ai1EPznlAc
8. finally on the http request node use the microservice url "http://host.docker.internal:8000/scrape"
