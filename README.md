PalletManagementSystem

Getting Started : 

**Step 1 : Creating a Virtual Environment**

    curl https://pyenv.run | bash
    nano ~/.bashrc
    
Add the code below at the end of the line. 

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

Reload Shell Configuration : 

    source ~/.bashrc

    pyenv install <version> #YoloV5 requires Python 3.8.10

    sudo apt install -y build-essential libssl-dev libbz2-dev libreadline-dev libsqlite3-dev zlib1g-dev libffi-dev libgdbm-dev #Run this command if got error during installation

Set global or local Python

    pyenv global <version>
    pyenv local <version>

Create Virtual Environment

    pyenv virtualenv <version> <env-name>
    pyenv activate <env-name>

To deactivate

    pyenv deactivate

**Clone this repository and install the dependencies and packages**

    git clone https://github.com/AmDerp/PalletManagementSystem.git
    cd PalletManagementSystem
    pip install -r requirements.txt

    
