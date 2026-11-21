pipeline{
    agent any
    stages{
        stage("auto_get_code"){
            steps{
                sh '''set -eu

                    export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                    export PATH="/Users/charlieliu/miniforge3/envs/pytest/bin:$JAVA_HOME/bin:/opt/homebrew/bin:/usr/bin:/bin"

                    python --version
                    python -m pip install -r requirements.txt
                    python main.py'''
            }
        }
    }
}