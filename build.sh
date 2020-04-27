echo "Performing PIP install for python_cowbull_server"
source ~/virtuals/python_cowbull_server/bin/activate
pip install -r requirements.txt --upgrade --quiet
echo
echo "Performing PIP install for p2_cowbull_server"
source ~/virtuals/p2_cowbull_server/bin/activate
pip install -r requirements.txt --upgrade --quiet
echo
echo "Performing PIP install in local lib for GCloud"
pip install -t lib -r requirements.txt --upgrade --quiet
echo
echo "Building Docker image dsanderscan/cowbull_v5"
docker build -t dsanderscan/cowbull_v5 -f vendor/docker/Dockerfile .
echo
echo "Pushing Docker image dsanderscan/cowbull_v5"
docker push dsanderscan/cowbull_v5
echo
echo "Pushing to GCloud"
gcloud app deploy --quiet
echo
echo "Done."
