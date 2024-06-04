import sqlite3

class DatabaseQueryExecutor:
    def __init__(self, database_link, user_input, db_table_info):
        self.database_link = database_link
        self.user_input = user_input
        self.db_table_info = db_table_info

    def execute_query(self, query):
        try:
            conn = sqlite3.connect(self.database_link)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            results_string = self.__results_to_string__(results, cursor)
            cursor.close()
            conn.close()
            return {
                'RESULTS': results_string,
                'ERROR': None
                }
        except sqlite3.Error as e:
            return {
                'ERROR': e, 
                'RESULTS': None
                }

    def __results_to_string__(self, results, cursor):    
        column_names = [description[0] for description in cursor.description]
    
        results_string = '\t'.join(column_names) + '\n' 
        for row in results:
            results_string += '\t'.join(map(str, row)) + '\n'

        return results_string