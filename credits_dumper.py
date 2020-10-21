import decima
from functools import partial

script_objects = {}
decima.read_objects(r'E:\Game Files\HZDPC\interface\menu\datasources\datasourcecreditsresource.core', script_objects)
credits_resource = [v for v in script_objects.values() if isinstance(v, decima.DataSourceCreditsResource)][0]
for row in credits_resource.rows:
    row_obj = row.follow(script_objects)
    for column in row_obj.columns:
        column_obj = column.follow(script_objects)
        print('{:20}'.format(column_obj.credits_name), end=' ')
    print()
