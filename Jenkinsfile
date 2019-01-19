def persisters = [
    '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0}}',
    '{"engine_name": "mongodb", "parameters": {"host": "db", "port": 27017, "db": "cowbull"}}'
]
def engine_names = ['Redis', 'MongoDB']
def engines = ['redis:5.0.3-alpine', 'mongo:4.0.5']

pipeline {
    agent any
    environment {
        REDIS_PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
        MONGO_PERSISTER='{"engine_name": "mongodb", "parameters": {"host": "mongo", "port": 27017, "db": "cowbull"}}'
    }

    stages {
        stage('Clone') {
            steps {
                /* Let's make sure we have the repository cloned to our workspace */
                checkout scm
            }
        }

        stage('Test') {
            steps {
                script {
                    for (int i = 0; i < persisters.size(); i++) {
                        docker.image(engines[i]).withRun('--name persist') { container ->
                            docker.image('dsanderscan/jenkins-py3-0.1').inside('--link persist:db') {
                                withEnv(["HOME=${env.WORKSPACE}"]) {
                                    checkout scm
                                    echo "Validating build with ${engine_names[i]} persister"
                                    echo "---"
                                    sh """
                                        python3 -m venv env
                                        source ./env/bin/activate 
                                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                                        export PERSISTER='${persisters[i]}'
                                        printf "\n** Validating build with Redis\n\n"
                                        echo "*** PYTHONPATH=\${PYTHONPATH}"
                                        python3 -m pip install -r requirements.txt --no-cache --user
                                        python3 -m unittest tests
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Build') {
            steps {
                sh """
                    echo "Testing"
#                    docker build -t not_sustainable_image -f vendor/docker/Dockerfile .
                """
            }
        }

        // stage{'SysTest'} {
        //     docker.image('redis:5.0.3-alpine').withRun('--name redis') { container ->
        //         docker.image('not_sustainable_image').inside('--link redis:redis') {
        //             sh """
        //                 python3 -m unittest tests
        //             """
        //         }
        //     }
        // }

        // stage('Validate') {
        //     steps {
        //         docker.image('redis:5.0.3-alpine').withRun('--name redis') { c ->
        //             docker.image('not_sustainable_image').inside('--link redis:redis') {
        //                 sh """
        //                     export PERSISTER='{"engine_name": "redis", "parameters": {"host": "redis", "port": 6379, "db": 0}}'
        //                     python3 -m unittest tests
        //                 """
        //             }
        //         }
        //     }
        // }

        // stage('Push') {
        //     steps {
        //         withCredentials([
        //             [$class: 'UsernamePasswordMultiBinding', 
        //             credentialsId: 'dockerhub',
        //             usernameVariable: 'USERNAME', 
        //             passwordVariable: 'PASSWORD']
        //         ]) {
        //             sh """
        //             docker login -u "${USERNAME}" -p "${PASSWORD}"
        //             docker tag not_sustainable_image "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
        //             docker push "${params.imageName}":"${params.Environment}"-"${params.Version}"."${env.BUILD_NUMBER}"
        //             """
        //         }
        //     }
        // }
    }
}