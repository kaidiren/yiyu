# -*- coding: utf-8 -*-
import pymongo
import datetime


db = pymongo.Connection().yiyu


one_yanxian = [{"title": "%s" % '第一个',
                "post_time": datetime.datetime.utcnow(),
                "content": '第一个',
                "text": '第一个', }]
db.yiyu.insert(one_yanxian)
one_yusui = [{"title": "%s" % '',
            "post_time": datetime.datetime.utcnow(),
            "content": '第一个',
            "text": '第一个', }]
db.yiyu.insert(one_yusui)

