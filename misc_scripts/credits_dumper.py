import os
from pydecima.resources import DataSourceCreditsResource
import pydecima

game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')

script_objects = {}
pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')
credits_file = os.path.join(pydecima.reader.game_root, r'interface/menu/datasources/datasourcecreditsresource.core')
pydecima.reader.read_objects(credits_file, script_objects)
credits_resource = [v for v in script_objects.values() if isinstance(v, DataSourceCreditsResource)][0]
for row in credits_resource.rows:
    row_obj = row.follow(script_objects)
    for column in row_obj.columns:
        column_obj = column.follow(script_objects)
        print('{:20}'.format(column_obj.credits_name), end=' ')
    print()
