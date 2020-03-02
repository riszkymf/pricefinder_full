#!/bin/bash

set -f

CRONJOBS_FILE='crontab/cron'
not_null_re='^(\*\/[0-9])|([0-9])+$'

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

truncate -s 0 ./cron

if [[ ! "$CRONJOB_COMMAND" ]]
then
    echo -e "\e[31mERROR : CRONJOB_COMMAND does not exist!\e[0m"
    exit
fi

if [[ "$CRON_MONTH" =~ $not_null_re ]] && [[ ! "$CRON_DoM" =~ $not_null_re ]] && [[ ! "$CRON_DoW" =~ $not_null_re ]]
then 
    CRON_DoM="1"
    CRON_DoW="*"
    DAY=true
fi

if [[ "$CRON_DoM" =~ $not_null_re ]] || [[ "$CRON_DoW" =~ $not_null_re ]]
then 
    DAY=true
fi

if [[ ! "$CRON_HOUR" =~ $not_null_re ]]
then
    if [[ $DAY = true ]]
    then
    CRON_HOUR=0
    HOUR=true
    fi
else
    HOUR=true
fi

if [[ ! "$CRON_MIN" =~ $not_null_re ]] && [[ $HOUR = true ]]
then
    CRON_MIN=0
fi
declare -a ARR=( ${CRON_MIN:-'*'} ${CRON_HOUR:-'*'} ${CRON_DoM:-'*'} ${CRON_MONTH:-'*'} ${CRON_DoW:-'*'} )

echo -e "\e[92mCRON SCHEDULE :" ${ARR[*]}
echo -e "------------------------------------------------------------------------------------------------------\e[0m"
# PUT YOUR CRONJOB HERE

cat >> ./cron << EOF 
${ARR[*]} $CRONJOB_COMMAND

EOF
crontab cron
crontab -u nobody cron
echo "Listing Crontab"
echo "------------------------------------------------------------------------------------------------------"
crontab -l
#crond -f -L /dev/stdout

