#!/bin/bash


function rep_ok(){
    echo -e '\e[32m'$1'\e[m'
}

function rep_warn(){
    echo -e '\e[1;33mWARNING: '$1'\e[m'
}

function rep_die(){
    echo -e '\e[1;31mWARNING: '$1'\e[m'
    exit
}


function run_gunicorn(){
    apphost=$1
    port=$2
    worker=$3
    if [[ -z $1 ]]; then
        rep_warn "Using Default Host"
        apphost=localhost
    fi

    if [[ -z $2 ]]; then
        rep_warn "Using Default Port"
        port=5000
    fi

    if [[ -z $3 ]]; then
        rep_warn "Using Default Worker"
        worker=2
    fi
    gunicorn production:app -b $apphost:$port -w $worker --keep-alive 150
}




command=$COMMAND
env=$ENVIRONMENT
worker=$WORKER


if [[ -z $COMMAND ]]; then
    command=$1
    rep_warn "Using Default Host $command"
fi

if [[ -z $ENVIRONMENT ]]; then
    env=$2
    rep_warn "Using Default Host $env"
fi

if [ $command = 'server' ]
    then
    if [ $env = 'production' ]
        then
        rep_ok 'STARTING | SERVER'
        run_gunicorn $APP_HOST $APP_PORT $worker
    elif [ $env = 'staging' ]
        then
        rep_ok 'STARTING | SERVER STAGING'
        python3 manage.py server
    fi
else
    rep_die 'USAGE : ./run.sh server [env].'
fi

