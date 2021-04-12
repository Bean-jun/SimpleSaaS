from datetime import datetime

from web import models

def peoduct_init():
    models.PricePolicy.objects.create(category=1,
                                      title="个人免费版",
                                      price=0,
                                      create_project=3,
                                      project_member=2,
                                      project_space=20,
                                      single_file_space=5,
                                      create_time=datetime.now())
