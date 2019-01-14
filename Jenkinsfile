node {
    def app

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */
        checkout scm
    }

    stage('Test') {
        /* Ideally, we would run a test framework against our image.
         * For this example, we're using a Volkswagen-type approach ;-) */
        docker.image('dsanderscan/jenkins-py3-0.1').inside('-p 6379:6379') { c ->
            checkout scm
            sh """
                pwd
                ls -als
                python3 -m venv env
                source ./env/bin/activate 
                export PYTHONPATH="\$(pwd)/:\$(pwd)/tests"
                echo "*** PYTHONPATH=\${PYTHONPATH}"
                python3 -m pip install -r requirements.txt
                python3 -m unittest tests
            """
        }

        // app.inside {
        //     sh 'echo "Tests passed"'
        // }
    }

    stage('Build image') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */
        app = docker.build("dsanderscan/cowbull", "-f vendor/docker/Dockerfile .")
    }

    stage('Push image') {
        /* Finally, we'll push the image with two tags:
         * First, the incremental build number from Jenkins
         * Second, the 'latest' tag.
         * Pushing multiple tags is cheap, as all the layers are reused. */
        docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
            app.push("jenkins-test-${env.BUILD_NUMBER}")
            // app.push("latest")
        }
    }
}