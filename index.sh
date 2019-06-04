#!/bin/bash

mkdir -p /usr/share/nginx/html

cat > /usr/share/nginx/html/index.html <<EOF
<html>
<body>
<h1>Lucky 13!</h1>
<p>My node name: ${MY_NODE_NAME}</p>
</body>
</html>
EOF

nginx -g "daemon off;"

