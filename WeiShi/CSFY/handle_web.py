import web
from CSFY.handle_sql import *

urls = (
    # '/(.*)', 'hello',
    '/started_house', 'started_house',
    '/finished_house', 'finished_house',
)


class started_house:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        db_cudr = CUDRDataBase('line_info')
        sql = """
            SELECT have FROM started_warehouse;
        """
        tuple_have = db_cudr.select_one_machine_id(sql)
        list_have = []
        string_have = ''
        for i in range(0, 12):
            list_have.append(tuple_have[i][0])
            string_have += str(tuple_have[i][0]) + ','
        string_have = string_have[:-1]
        return string_have


class finished_house:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        db_cudr = CUDRDataBase('line_info')
        sql = """
            SELECT have FROM finished_warehouse;
        """
        tuple_have = db_cudr.select_one_machine_id(sql)
        string_have = ''
        for i in range(0, 12):
            string_have += str(tuple_have[i][0]) + ','
        string_have = string_have[:-1]
        return string_have


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

