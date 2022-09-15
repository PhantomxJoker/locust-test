FROM locustio/locust

WORKDIR /home/locust

RUN mkdir -p /home/locust/shortened-urls/

ADD shortened-url.py /home/locust/
ADD .env /home/locust/


RUN pip install python-dotenv
RUN pip install pyjwt

EXPOSE 8089

#For run user test
ENTRYPOINT ["locust", "-f", "./shortened-url.py"]