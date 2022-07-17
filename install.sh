pip install -r requirements.txt
sudo cp src/cprun /bin/cprun
sudo cp src/cpget /bin/cpget
mkdir ~/.sample-test-runner
sudo cp src/parse.py ~/.sample-test-runner/parse.py
sudo chmod 755 /bin/cprun
sudo chmod 755 /bin/cpget
sudo chmod 755 ~/.sample-test-runner/parse.py
