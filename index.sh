#!/bin/bash

mkdir -p /usr/share/nginx/html

cat > /usr/share/nginx/html/index.html <<EOF
<html>
<body>
<h1>Lucky 13!</p>
<p>My node name...</p>
<p>${MY_NODE_NAME}</p>
</body>
</html>
EOF

nginx -g "daemon off;"

