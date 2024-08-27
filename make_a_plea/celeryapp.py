from celery import Celery

app = Celery('celeryapp',
            result_backend='django-db',
            broker_url="SQS://",
            broker_transport_options={
                "region": "eu-west-2", # your AWS SQS region
                "predefined_queues": {
                    "pet-development-celery": {  ## the name of the SQS queue
                        "url": "https://sqs.eu-west-2.amazonaws.com/754256621582/pet-development-celery"
                    }
                }
            })
