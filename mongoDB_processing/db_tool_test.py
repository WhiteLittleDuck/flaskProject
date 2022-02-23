import json
from mongoDB_processing.db_tool import DBTool

db_tool=DBTool('current_data/')
# test sort
# for k in db_tool.sort_to_rank('ui_neg_rate',1):
#     print(k['appId']+':'+str(k['ui_pos_rate']))

# write the db message in local area
db_tool.write_rank_record_after_sort()

# test find app_info
# print(db_tool.find_app_info('air.com.KalromSystems.SandDrawLite'))
