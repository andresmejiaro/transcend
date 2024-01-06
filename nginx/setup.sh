#! /bin/sh

js_file="/usr/share/nginx/html/srcs/utils/utils.js"

sed -i '1,2d' $js_file

sed -i "1i window.DJANGO_API_BASE_URL = \"$DJANGO_BACKEND_URL\";" $js_file
sed -i "2i window.DAPHNE_BASE_URL = \"$DAPHNE_URL\";" $js_file

exec nginx -g "daemon off;"