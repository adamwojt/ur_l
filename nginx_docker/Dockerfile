FROM nginx:1.18.0-alpine

# Credit: https://github.com/kreuzwerker/envplate

RUN echo $UR_L_PORT
RUN rm /etc/nginx/conf.d/default.conf
RUN curl -sLo /usr/local/bin/ep https://github.com/kreuzwerker/envplate/releases/download/v0.0.8/ep-linux && chmod +x /usr/local/bin/ep

RUN mkdir /home/nginx

COPY nginx_docker/nginx.conf /etc/nginx/conf.d

CMD [ "/usr/local/bin/ep", "-v", "/etc/nginx/conf.d/nginx.conf", "--", "/usr/sbin/nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]

