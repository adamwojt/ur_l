FROM nginx:1.18.0-alpine

# Credit: https://github.com/kreuzwerker/envplate

RUN echo $UR_L_PORT
RUN rm /etc/nginx/conf.d/default.conf
RUN curl -sLo /usr/local/bin/ep https://github.com/kreuzwerker/envplate/releases/download/v0.0.8/ep-linux && chmod +x /usr/local/bin/ep

# Credit https://github.com/JensPiegsa/ab/blob/master/Dockerfile
RUN apk update \
 && apk add --no-cache apache2-utils \
 && apk add jq

COPY nginx_docker/nginx.conf /etc/nginx/conf.d

COPY ./nginx_docker/benchmark_script.sh /usr/sbin/benchmark
COPY ./nginx_docker/benchmark.json .
RUN chmod +x /usr/sbin/benchmark
RUN mkdir /staticfiles

CMD [ "/usr/local/bin/ep", "-v", "/etc/nginx/conf.d/nginx.conf", "--", "/usr/sbin/nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]
