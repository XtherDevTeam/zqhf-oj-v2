# zqhf-oj-v2

It's an "*online judge system*" based on vue2 and elements-ui

- How does it works?
  
  It's easy.
  Backend is in the `backend` directory, it's an api server.
  Frontend is in the `frontend` directory, it serves requests from web-server.
  It also can work with electron.

- Setup

  1. Install the necessary libraries with pip:

  ```sh
  pip3 install flask flask_cors requests
  ``` 

  2. Install the [judger](https://github.com/QingdaoU/Judger) for judge machine follow the [instructions](https://opensource.qduoj.com/#/judger/api)

  ```sh
  git clone https://github.com/QingdaoU/Judger.git
  cd Judger
  sudo apt-get install libseccomp-dev
  mkdir build && cd build && cmake .. && make && sudo make install
  cd bindings/Python ; sudo python setup.py install
  ```

  3. Setup web interface on web interface machine

    ```sh
    sudo apt install nginx nodejs -y
    cd path/to/zqhf-oj-v2/frontend ; npm install
    cd path/to/zqhf-oj-v2/scripts 
    sudo ./daemon.py install page
    sudo ./daemon.py install nginx
    sudo service nginx restart
    ```

  4. Install the new spj backend according to [the document](https://github.com/XtherDevTeam/zqhf-oj-v2-spj-backend#readme).

  5. Initialize and start api

    On web interface machine:

    ```sh
    cd path/to/zqhf-oj-v2/scripts
    cd path/to/zqhf-oj-v2/backend/src
    python3
    > import backend
    > backend.connect_db()
    > backend.init_db()
    ./daemon.py start api
    ```

    Edit your `path/to/zqhf-oj-v2/backend/src/config.json` on your web interface machine.
    Change the settings, like `web-server-port`, `web-server-address` and `judge-server-address`.

    On judge machine:

    ```sh
    cd path/to/zqhf-oj-v2/scripts
    ./daemon.py start judge
    ```

  