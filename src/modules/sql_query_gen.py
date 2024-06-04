import re
import os
import time
import pandas as pd
import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain.prompts import ChatPromptTemplate

from modules.query_exec import DatabaseQueryExecutor

class SQLQueryGenerator():
    def __init__(self, model, db_link, prompt_hub_link, db_path) -> None:
        self.model = model
        self.db_link = db_link
        self.prompt_hub_link = prompt_hub_link
        self.db_path = db_path

    def __db__(self):
        print(self.db_link)
        return SQLDatabase.from_uri(self.db_link)

    def __prompt__(self, hub_link, key):
        if key == 'INIT':
            prompt = hub.pull(self.prompt_hub_link)
        elif key == 'REGEN':
            prompt = ChatPromptTemplate.from_template("""
You are a SQL professional designed to generate perfect SQL queries based on given suggestions also make sure with utmost precision that the table name is correct and the column names are correct for that table sometimes the name is divided into 2 halves firstname and lastname so, make sure you double check it and don't make mistake you will lose your job if you made mistakes. Each suggestion includes a query template and an explanation. Your task is to produce an optimized, syntactically correct SQL query formatted using best practices.

Suggestion and explanation:
<suggestion> {suggestion} </suggestion>

Your Task:

Generate the SQL query from the suggestion and explanation provided. Format the output as follows:

Please use the proper attribute names as mentioned in database details. This is a competition. Only give one query in a single line; it doesn't matter how big it is. Don't make it multi-line, and wrap it in ```sql\n\n```.

Example Output: Make sure the query should be in a single like WIHTOUT any escape carachters
```sql\nSELECT COUNT(*) FROM playlists;\n```
Use this format ```sql\n(.*)\n``` this regex should work to generate the required SQL query based on the provided suggestion and explanation.""")
        else:
            raise KeyError
        return prompt
    
    def __inputs__(self):
        db = self.__db__()
        inputs = {
            "table_info": lambda x: db.get_table_info(),
            "input": lambda x: x["question"],
            "few_shot_examples": lambda x: "",
            "dialect": lambda x: db.dialect,
        }
        return inputs
    
    def get_table_info(self):
        return self.__db__().get_table_info()
    

    def __llm_output_parser__(self, unparsed_query):
        query_extractor = r"```sql (.*) ```"
        unparsed_query=unparsed_query.replace('\n', ' ')
        query_extractor_regex = re.compile(query_extractor)
        regex_object = re.search(query_extractor_regex, unparsed_query)
     
        if regex_object:
            return regex_object.groups()[0]
        return "Cannot form the Query for the request"
    
    def SQL_query_generator(self, user_input, key):
        model = ChatOllama(model=self.model, temperature=0)

        if key == 0:
            print('INIT')
            sql_response = (
                self.__inputs__()
                | self.__prompt__(hub_link=self.prompt_hub_link, key='INIT')
                | model.bind(stop=["\nSQLResult:"])
                | StrOutputParser()
            )
            start = time.time()
            unparsed_query = sql_response.invoke({"question": str(user_input) + "yDont add anything extra the query should only serve the purpose, do not assume anything. It is a competition, Only Give one query, and wrap it in ```sql\nquery\n```"})
            end = time.time()
            parsed_query = self.__llm_output_parser__(unparsed_query=unparsed_query)

            return {'query': parsed_query, 'response_time': (end-start)}
        else:
            print('REGEN')
            sql_response = (
            {'suggestion': lambda x: x['question']}
            | self.__prompt__(hub_link=self.prompt_hub_link, key='REGEN')
            | model.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
            )
            start = time.time()
            unparsed_query = sql_response.invoke({"question": str(user_input) + "you are always giving wrong answer, Please use the proper attribute name as mentioned in database details. It is a competition, Only Give one query, and wrap it in ```sql\nquery\n```"})
            print('*'*20)
            print('From REGEN: \n')
            print(unparsed_query)
            print('*'*20)
            end = time.time()
            parsed_query = self.__llm_output_parser__(unparsed_query=unparsed_query)

            return {'query': parsed_query, 'response_time': (end-start)}
    
    def SQL_query_regen(self, user_input):
        model = ChatOllama(model=self.model, temperature=0)

        sql_response = (
            {'suggestion': lambda x: x['question']}
            | self.__prompt__(hub_link=self.prompt_hub_link, key='REGEN')
            | model
            | StrOutputParser()
        )
        start = time.time()
        unparsed_query = sql_response.invoke({"question": str(user_input) + "you are always giving wrong answer, Please use the proper attribute name as mentioned in database details. It is a competition, Only Give one query, and wrap it in ```sql\nquery\n```"})
        print(unparsed_query)
        end = time.time()
        parsed_query = self.__llm_output_parser__(unparsed_query=unparsed_query)

        return {'query': parsed_query, 'response_time': (end-start)}
    
    # def sql_query_generator(self, user_input, type_of_gen):
    #     if (type_of_gen == 'INIT'):
    #         print('init')
    #         model = ChatOllama(model=self.model, temperature=0)
    #         sql_response = (
    #             self.__inputs__()
    #             | self.__prompt__(hub_link=self.prompt_hub_link, key=type_of_gen)
    #             | model.bind(stop=["\nSQLResult:"])
    #             | StrOutputParser()
    #         )
    #     elif (type_of_gen == 'REGEN'):
    #         print('regen')
    #         model_regen = ChatOllama(model=self.model, temperature=0)
    #         print(self.__prompt__(hub_link=self.prompt_hub_link, key=type_of_gen))
    #         sql_response = (
    #             {'suggestion': lambda x: x['question']}
    #             | self.__prompt__(hub_link=self.prompt_hub_link, key=type_of_gen)
    #             | model_regen.bind(stop=['\nSQLResult:'])
    #             | StrOutputParser()
    #         )
    #     else:
    #         raise KeyError
       
    #     start = time.time()
    #     unparsed_query = sql_response.invoke({"question": str(user_input) + "you are always giving wrong answer, Please use the proper attribute name as mentioned in database details. It is a competition, Only Give one query, and wrap it in ```sql\nquery\n```"})
    #     end = time.time()
    #     print(unparsed_query)
    #     parsed_query = self.__llm_output_parser__(unparsed_query=unparsed_query)

    #     return {'query': parsed_query, 'response_time': (end-start)}

def main():
    st.title("SQL Query Generator and Executor")
    
    user_input = st.text_input("Enter what you want to find")
    if user_input:
        sql_query_generator = SQLQueryGenerator(model='llama3', 
                                                db_link="sqlite:///database/chinook.db",
                                                db_path="/home/tanmaypatil/Documents/Vanquisher_Tech/templates/sql-langchain/database/chinook.db",
                                                prompt_hub_link="rlm/text-to-sql"
                                                )
        print(sql_query_generator.get_table_info())
        query_response = sql_query_generator.SQL_query_generator(user_input, 'REGEN')
        
        st.write("="*20)
        st.write("Query: ", query_response['query'])
        st.write("*"*20)
        st.write("Response Time: ", query_response['response_time'])
        st.write("="*20)
        
        database_link = '/home/tanmaypatil/Documents/Vanquisher_Tech/templates/sql-langchain/database/chinook.db'
        if not os.path.exists(database_link):
            st.error(f"Database file not found at {database_link}")
        else:
            executor = DatabaseQueryExecutor(database_link)
            result = executor.execute_query(query_response['query'])
            
            st.write("Query Response:")
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], tuple):
                df_result = pd.DataFrame(result)
                st.dataframe(df_result)
            else:
                st.write(result)
        
        st.write("="*20)
        
if __name__ == '__main__':
    main()