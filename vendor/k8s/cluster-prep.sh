#!/usr/bin/env bash
echo
echo "NGINX Ingress Controller installation."
echo "For reference: https://kubernetes.github.io/ingress-nginx/deploy/"
echo
echo "Create cluster role binding for GKE"
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole cluster-admin \
  --user $(gcloud config get-value account)
echo "Apply mandatory"
kubectl apply \
    -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/mandatory.yaml
echo "Apply cloud generic"
kubectl apply \
    -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/provider/cloud-generic.yaml
echo "Apply generic"
kubectl apply \
    -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.30.0/deploy/static/provider/cloud-generic.yaml

echo
echo "Cert manager installation."
echo "For reference: https://cert-manager.io/docs/installation/kubernetes/"
echo "Note         : Version is set to 0.13.1"
echo
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.13.1/cert-manager.yaml
