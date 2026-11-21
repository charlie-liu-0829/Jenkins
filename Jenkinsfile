pipeline{
    agent any
    environment {
        DB_HOST = '127.0.0.1'
        DB_PORT = '3306'
        DB_USER = 'root'
        DB_PASSWORD = 'Lym030829'
        DB_NAME = 'ecommerce_demo'
    }

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
    post {
  always {
        emailext body: '''<html>
              <h1>total cases: ${TEST_COUNTS,var="total"} <h1>
              <h1>pass cases: ${TEST_COUNTS,var="pass" <h1>
              <h1>fail cases: ${TEST_COUNTS,var="fail" <h1>
            </html>''', subject: '自动化测试脚本运行结果通知', to: '18600988847@163.com'
          }
    }

}