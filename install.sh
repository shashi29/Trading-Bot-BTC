curl https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh -o ~/Anaconda3.sh
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-Linux-x86_64.sh -O ~/Anaconda3.sh
bash ~/Anaconda3.sh -b -p $HOME/Anaconda3
source ~/.bashrc
conda init
