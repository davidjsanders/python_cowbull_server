def persisters = [
    '{"engine_name": "redis", "parameters": {"host": "db", "port": 6379, "db": 0}}',
    '{"engine_name": "mongodb", "parameters": {"host": "db", "port": 27017, "db": "cowbull"}}'
]
def engine_names = ['Redis', 'MongoDB']
def engines = ['redis:5.0.3-alpine', 'mongo:4.0.5']
def test_variable = readJson text: '{"persister":"redis", "foo":"bar"}'
def image_name = '${params.imageName}:test-${params.Version}.${env.BUILD_NUMBER}'

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
                        echo "Conducting unit tests with ${engine_names[i]} persister"
                        echo "---"
                        docker.image(engines[i]).withRun('--name persist') { container ->
                            docker.image('dsanderscan/jenkins-py3-0.1').inside('--link persist:db') {
                                withEnv(["HOME=${env.WORKSPACE}"]) {
                                    checkout scm
                                    sh """
                                        python3 -m venv env
                                        source ./env/bin/activate 
                                        export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                                        export PERSISTER='${persisters[i]}'
                                        python3 -m pip install --quiet -r requirements.txt --no-cache --user
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
                echo "Building temporary image"
                withEnv(["image_tag='${params.imageName}:test-${params.Version}.${env.BUILD_NUMBER}'"]) {
                    sh """
                        docker build -t ${image_tag} -f vendor/docker/Dockerfile .
                    """
                }
                    // docker build -t "${params.imageName}":test-${params.Version}.${env.BUILD_NUMBER} -f vendor/docker/Dockerfile .
            }
        }

        // stage('System Test') {
        //     steps {
        //         script {
        //             for (int i = 0; i < persisters.size(); i++) {
        //                 echo "Validating Docker image with the ${engine_names[i]} persister"
        //                 echo "---"
        //                 docker.image(engines[i]).withRun('--name persist') { container ->
        //                     withEnv(["image_tag='${params.imageName}:test-${params.Version}.${env.BUILD_NUMBER}'"]) {
        //                         docker.image('${image_tag}').inside('--link persist:db') {
        //                             sh """
        //                                 python3 -m unittest tests
        //                             """
        //                         }
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }

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