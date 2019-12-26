# python-cowbull-server
| step  | command |
| ----- | ------- |
| Build | gcloud builds submit --tag gcr.io/cowbull-k8s-project/python-cowbull-server:\<tag\> |
| Run   | gcloud run deploy --image gcr.io/cowbull-k8s-project/python-cowbull-server:\<tag\> --update-env-vars KEY1=VALUE1,KEY2=VALUE2 --platform managed |
| build | gcloud builds submit --tag gcr.io/cowbull-k8s-project/python-cowbull-server:\<tag\> |
