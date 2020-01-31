FROM python

ARG SOURCE_BRANCH
RUN pip install git+https://github.com/shuichiro-makigaki/mendeley_cli@${SOURCE_BRANCH}

ENV MENDELEY_CLIENT_ID=9999
ENV MENDELEY_CLIENT_SECRET=dummy
ENV MENDELEY_REDIRECT_URI=http://localhost:8888
ENTRYPOINT [ "mendeley" ]
CMD [ "--help" ]
