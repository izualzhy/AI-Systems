#!/bin/bash

function pause() {
    echo
    sleep 2
    #read -p ">>> Press [Enter] to continue, or [Ctrl+C] to exit."
}

curl http://0.0.0.0:8000/a
pause
curl http://0.0.0.0:8000/b
pause
curl http://0.0.0.0:8000/a
pause
curl http://0.0.0.0:8000/b
pause
curl http://0.0.0.0:8000/a
pause
curl http://0.0.0.0:8000/b
