if [ -z "$GGJ18_PYTHON_PATH" ]
then
    export GGJ18_PYTHON_PATH=$GGJ18_DIR/
    export GGJ18_DATA_DIR=$GGJ18_DIR/../data/
    export PYTHONPATH=$GGJ18_PYTHON_PATH:$PYTHONPATH
fi

alias ggj18-dungeoncrawler="python3 $GGJ18_DIR/games/dungeoncrawler.py"