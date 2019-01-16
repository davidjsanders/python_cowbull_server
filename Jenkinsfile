node {
    environment {
        def temp_image_id = UUID.randomUUID().toString()
    }
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
            docker build -t "${env.temp_image_id}-${env.BUILD_NUMBER}" -f vendor/docker/Dockerfile .
        """
    }

    stage{'SysTest'} {
        docker.image('redis:5.0.3-alpine').withRun('--name redis') { container ->
            docker.image('"${env.temp_image_id}-${env.BUILD_NUMBER}"').inside('--link redis:redis') {
                sh """
                    python3 -m unittest tests
                """
            }
        }
    }

    stage('Push') {
        withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'dockerhub',
usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
            sh """
            docker login -u "${USERNAME}" -p "${PASSWORD}"
            docker tag "${env.temp_image_id}-${env.BUILD_NUMBER}" "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
            docker push "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
            """
        }
    }
}