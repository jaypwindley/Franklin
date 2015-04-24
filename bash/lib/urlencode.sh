# ***********************************************************************
#  File:              TAG( urlencode.sh )
#  Description:       Encode a string for use in a URL
#  Author:            nil <jwindley>
#  Created:           Thu Jan 23 20:50:10 2014
#  Copyright:         (c) 2014 Jay Windley
#                     All rights reserved.
# ***********************************************************************

urlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"
}
