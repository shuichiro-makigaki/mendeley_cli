FROM python

ARG SOURCE_BRANCH
RUN pip install git+https://github.com/shuichiro-makigaki/mendeley_cli@${SOURCE_BRANCH}

ENTRYPOINT [ "mendeley" ]
CMD [ "--help" ]
