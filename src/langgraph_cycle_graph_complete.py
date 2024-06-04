import os
import time
import streamlit as st
from langgraph.graph import Graph

from modules.sql_query_gen import SQLQueryGenerator
from modules.query_exec import DatabaseQueryExecutor
from modules.query_assuring_utilities import QueryAssuringUtilities

class LangGraphCycleGraph:
    def __init__(self, state):
        self.state_sql = state

    def sql_query_gen(self, state):
        sql_query_generator = SQLQueryGenerator(model=state['model'], 
                                                    db_link=state['db_link'],
                                                    db_path=state['db_path'],
                                                    prompt_hub_link=state['prompt_hub_link']
                                                    )
        state['table_info'] = sql_query_generator.get_table_info()
        if state['current_iteration'] == 0:
            query_response = sql_query_generator.SQL_query_generator(user_input=state['user_inputs'][-1],  key=state['current_iteration'])
        else:
            query_response = sql_query_generator.SQL_query_generator(user_input=state['found_error_solutions'][-1],  key=state['current_iteration'])
        state['current_iteration'] += 1
        state['queries_generated_agent'].append(query_response)
        return state

    def sql_query_executor(self, state):
        if not os.path.exists(state['db_path']):
            raise (f"Database file not found at {state['db_path']}")
        else:
            executor = DatabaseQueryExecutor(
                database_link=state['db_path'], 
                user_input=state['user_inputs'][-1], 
                db_table_info=state['table_info'])
            result = executor.execute_query(state['queries_generated_agent'][-1]['query'])
            state['query_results'].append(result)
        return state

    def did_SQL_query_execute(self, state):
        latest_result = state['query_results'][-1]
        if not latest_result['ERROR']:
            state['current_iteration'] = 0
            return 'YES'
        else:
            return 'NO'


    def error_finder(self, state):
        error_finder = QueryAssuringUtilities(
                    model=state['model'],
                    user_input=state['user_inputs'][-1] + "See the table schema carefully",
                    query_error= state['query_results'][-1]['ERROR'],
                    query=state['queries_generated_agent'][-1]['query'],
                    query_results=state['query_results'][-1]['ERROR'],
                    db_table_info=state['table_info']
                )

        found_error_solution = error_finder.find_error()
        state['found_error_solutions'].append(found_error_solution)
        return state
    def validator(self, state):
        valid_finder = QueryAssuringUtilities(
                    model=state['model'],
                    user_input=state['user_inputs'][-1] + "See the table schema carefully",
                    query_error= state['query_results'][-1]['ERROR'],
                    query=state['queries_generated_agent'][-1]['query'],
                    query_results=state['query_results'][-1]['ERROR'],
                    db_table_info=state['table_info']
                )
        state['found_valid'].append(str(valid_finder.validate_answer()).strip())
        return state

    def is_valid(self, state):
        return state['found_valid'][-1]
        

    def formatter(self, state):
        formatter = QueryAssuringUtilities(
                    model=state['model'],
                    user_input=state['user_inputs'][-1] + "See the table schema carefully",
                    query_error= state['query_results'][-1]['ERROR'],
                    query=state['queries_generated_agent'][-1]['query'],
                    query_results=state['query_results'][-1]['RESULTS'],
                    db_table_info=state['table_info']
                )
        return formatter.formatter()
    
    def graphApp(self):
        workflow = Graph()

        workflow.add_node('sql_query_generator_agent', self.sql_query_gen)
        workflow.add_node('sql_query_exec_tool', self.sql_query_executor)
        workflow.add_node('error_finder', self.error_finder)
        workflow.add_node('validator', self.validator)
        workflow.add_node('output', self.formatter) 

        workflow.add_edge('sql_query_generator_agent', 'sql_query_exec_tool')

        workflow.add_conditional_edges('sql_query_exec_tool', self.did_SQL_query_execute, {'YES': 'validator', 'NO': 'error_finder'}) 
        workflow.add_conditional_edges('validator', self.is_valid ,{'YES': 'output', 'NO': 'error_finder'}) 
        workflow.add_edge('error_finder', 'sql_query_generator_agent')

        workflow.set_entry_point('sql_query_generator_agent')
        workflow.set_finish_point('output') 

        app = workflow.compile()

        return app
    
    def invoker(self, user_input):
        # user_input = str(input("Please enter your question: "))
        self.state_sql['user_inputs'].append(user_input)
        app = self.graphApp()
        result = app.invoke(self.state_sql)
        return result


if __name__ == '__main__':
    st.title("User Input Processor")
    state = {}
    init = True
    state['user_inputs'] = []
    state['db_link'] = "sqlite:///database/chinook.db"
    state['db_path'] = "/home/tanmaypatil/Documents/Vanquisher_Tech/templates/sql-langchain/database/chinook.db"
    state['prompt_hub_link'] = 'rlm/text-to-sql'
    state['queries_generated_agent'] = []
    state['query_results'] = []
    state['max_iteration'] = 10
    state['current_iteration'] = 0
    state['found_error_solutions'] = []
    state['found_valid'] = []

    model_options = ['llama3', 'llama2']
    db_options = ['SQLite', 'MySQL', 'Microsoft SQL', 'PostgresSQL']
    state['model'] = st.selectbox("Choose a model:", model_options)
    state['db_type'] = st.selectbox("Choose a database which you are using:", model_options)

    user_input = st.text_input("Please enter your question:")

    if st.button("Submit"):
        if user_input:
            with st.spinner("Processing..."):
                start = time.perf_counter()
                demo = LangGraphCycleGraph(state=state)
                output = demo.invoker(user_input=user_input)
                end = time.perf_counter()

            st.write("Processed Output:")
            st.write(output)
            st.write(f'Reponse Time: {end - start} secs')

        else:
            st.warning("Please enter a question.")

#? Example questions: Get the email addresses of customers who either don't have a fax number or have a fax number ending with '1234'.