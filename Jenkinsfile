node {
    stage('Clone') {
        /* Let's make sure we have the repository cloned to our workspace */
        checkout scm
    }

    stage('Test') {
        docker.image('redis:5.0.3-alpine').withRun('--name redis') { container ->
            docker.image('dsanderscan/jenkins-py3-0.1').inside('--link redis:redis') {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    checkout scm
                    sh """
                        pwd
                        ls -als
                        python3 -m venv env
                        source ./env/bin/activate 
                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                        export PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
                        echo "*** PYTHONPATH=\${PYTHONPATH}"
                        python3 -m pip install -r requirements.txt --no-cache --user
                        python3 -m unittest tests
                    """
                }
            }
        }
    }

    stage('Build') {
        sh """
            docker build -t dsanders/cowbull:"${params.Environment}"-"${params.Version}"-"${env.BUILD_NUMBER}" -f vendor/docker/Dockerfile .
        """
    }

    stage('Push') {
        withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'dockerhub',
usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
            sh """
            docker login -u "${USERNAME}" -p "${PASSWORD}"
            # docker tag dsanderscan/cowbull dsanderscan/cowbull:jenkins-test-"${env.BUILD_NUMBER}"
            docker push dsanderscan/cowbull:"${params.Environment}"-"${params.Version}"-"${env.BUILD_NUMBER}"
            """
        }
    }
}