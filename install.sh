pip install -r requirements.txt
sudo cp src/cprun /usr/local/bin/cprun
sudo cp src/cpget /usr/local/bin/cpget
mkdir ~/.sample-test-runner
sudo cp src/parse.py ~/.sample-test-runner/parse.py
sudo chmod 755 /usr/local/bin/cprun
sudo chmod 755 /usr/local/bin/cpget
sudo chmod 755 ~/.sample-test-runner/parse.py
