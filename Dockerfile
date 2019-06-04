FROM nginx:1

COPY index.sh /

ENTRYPOINT ["bash", "/index.sh"]

