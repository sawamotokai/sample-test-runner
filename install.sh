pip install -r requirements.txt
sudo cp src/cprun /usr/local/bin/cprun
sudo cp src/cpget /usr/local/bin/cpget
mkdir ~/.sample-test-runner
sudo cp src/parse.py ~/.sample-test-runner/parse.py
sudo chmod 755 /usr/local/bin/cprun
sudo chmod 755 /usr/local/bin/cpget
sudo chmod 755 ~/.sample-test-runner/parse.py
BLUE='\033[0;32m'
NC='\033[0m'
echo "alias cpget=\". cpget\"" >> ~/.bashrc
echo -e "${BLUE}\nRun the following commands to finish installation.\n${NC}"
echo "echo \"export ATCODER_USERNAME=<Your AtCoder username>\" >> ~/.bashrc"
echo "echo \"export ATCODER_PASSWORD=<Your AtCoder pasword>\" >> ~/.bashrc"
echo "echo \"export CODEFORCES_USERNAME=<Your CodeForces username>\" >> ~/.bashrc"
echo "echo \"export CODEFORCES_PASSWORD=<Your CodeForces pasword>\" >> ~/.bashrc"
echo "source ~/.bashrc"