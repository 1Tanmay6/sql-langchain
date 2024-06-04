# from sql_query_gen import SQLQueryGenerator
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

class QueryAssuringUtilities:
    def __init__(self, query, query_results, user_input, model, db_table_info, query_error):
        self.query = query
        self.query_results = query_results
        self.user_input = user_input
        self.model = model
        self.db_table_info = db_table_info
        self.query_error = query_error
    def __llm__(self):
        return ChatOllama(model=self.model, temperature=0)

    def __prompt_text__(self, type):
        if (type == 'VALIDATE_ANSWER'):
            return """
            You are an AI model tasked with evaluating the relevance of SQL query results to a given user question, go easy on the checks even if it resembles a little say 'YES' and if the data is empty then also say 'YES'. Your goal is to decide if the provided SQL query and its results answer the user's question or not.

            Input:

            1. User Question
            2. SQL Query
            3. Query Results

            Output:

            If the query results sufficiently answer the user question, respond with "YES".
            If the query results do not answer the user question, respond with "NO".
            Guidelines:

            The query results must directly address the specific details asked in the user question.
            Consider the completeness and accuracy of the query results in relation to the user question.
            Examples:

            Example 1:

            User Question: "What is the total number of employees in the company?"
            SQL Query: "SELECT COUNT() FROM employees;"
            Query Results: "COUNT(): 250"

            Output: YES

            Example 2:

            User Question: "List all employees who joined in 2021."
            SQL Query: "SELECT * FROM employees WHERE joining_year = 2021;"
            Query Results: "employee_id: 123, name: John Doe, joining_year: 2021; employee_id: 124, name: Jane Smith, joining_year: 2021"

            Output: YES

            Example 3:

            User Question: "What is the average salary of employees?"
            SQL Query: "SELECT MAX(salary) FROM employees;"
            Query Results: "MAX(salary): 120000"

            Output: NO

            Example 4:

            User Question: "How many employees have a salary greater than $100,000?"
            SQL Query: "SELECT COUNT() FROM employees WHERE salary > 100000;"
            Query Results: "COUNT(): 50"

            Output: YES

            Example 5:

            User Question: "What are the names of employees who joined in 2022?"
            SQL Query: "SELECT name FROM employees WHERE joining_year = 2021;"
            Query Results: "name: John Doe; name: Jane Smith"

            Output: NO

            Now, evaluate the following:

            User Question: "{user_input}"
            SQL Query: "{sql_query}"
            Query Results: "{query_results}"

            Output: YES/NO (Pick one dont write anything else or else marks would be deducted)
            """
        elif (type == 'OUTPUT'):
            return """You are an AI model tasked with providing detailed explanations based on user input, SQL queries, and their results. Your goal is to write comprehensive and clear explanations, including ASCII tables when dealing with tabular data. Only provide a short explanation if explicitly requested by the user.

            Input:

            User Question: {user_input}
            SQL Query: {sql_query}
            Query Results: {query_results}
            Output:

            Restate the user question.
            Describe the purpose of the SQL query.
            Present the query results in an easy-to-understand format, using ASCII tables if applicable.
            Provide a detailed explanation of how the query results answer the user question.
            If the user specifically requests a short explanation, provide a concise summary instead.
            Guidelines:

            Ensure the explanation is thorough and clear.
            Use ASCII tables to represent tabular data for better visualization.
            Only shorten the explanation if explicitly asked by the user.
            Examples:

            Example 1:

            User Question: "What is the total number of employees in the company?"
            SQL Query: "SELECT COUNT() FROM employees;"
            Query Results: "COUNT(): 250"

            Output:

            User Question: "What is the total number of employees in the company?"
            SQL Query: The query counts the total number of records in the 'employees' table, which represents the total number of employees.
            Query Results:
            sql
            Copy code
            +----------+
            | COUNT(*) |
            +----------+
            |   250    |
            +----------+
            Explanation: The result shows that there are 250 employees in the company. This is derived from the 'COUNT(*)' function which counts all rows in the 'employees' table.
            Example 2:

            User Question: "List all employees who joined in 2021."
            SQL Query: "SELECT * FROM employees WHERE joining_year = 2021;"
            Query Results:

            diff
            Copy code
            +-------------+------------+--------------+
            | employee_id | name       | joining_year |
            +-------------+------------+--------------+
            | 123         | John Doe   | 2021         |
            | 124         | Jane Smith | 2021         |
            +-------------+------------+--------------+
            Output:

            User Question: "List all employees who joined in 2021."
            SQL Query: The query selects all records from the 'employees' table where the 'joining_year' is 2021.
            Query Results:
            diff
            Copy code
            +-------------+------------+--------------+
            | employee_id | name       | joining_year |
            +-------------+------------+--------------+
            | 123         | John Doe   | 2021         |
            | 124         | Jane Smith | 2021         |
            +-------------+------------+--------------+
            Explanation: The result shows the employees who joined the company in 2021. It includes their employee IDs, names, and the year they joined. According to the table, John Doe and Jane Smith both joined in 2021.
            Example 3:

            User Question: "What is the average salary of employees?"
            SQL Query: "SELECT MAX(salary) FROM employees;"
            Query Results: "MAX(salary): 120000"

            Output:

            User Question: "What is the average salary of employees?"
            SQL Query: The query retrieves the maximum salary from the 'employees' table, not the average.
            Query Results:
            sql
            Copy code
            +-------------+
            | MAX(salary) |
            +-------------+
            |   120000    |
            +-------------+
            Explanation: The result shows the maximum salary of employees, which is 120,000. This does not answer the user question, which asked for the average salary. To find the average salary, a different query should be used, such as "SELECT AVG(salary) FROM employees;".
            Now, evaluate the following:

            User Question: "{user_input}"
            SQL Query: "{sql_query}"
            Query Results: "{query_results}"

            Output: (Only must be a table(ASCII make it presentable) with the column names as mentioned in the query, strict warning donot change the column names and explanation and nothing else. Just answer the user's answer and nothing else don't add anything which is not asked for except explanations.)

            """
        elif (type == 'FIND_ERROR'):
            return """
            You are an amazing SQL helping assistant.
          Use context all the information avaiable in the database and user input to formulate a simple query in SQL always output in format ```sql\nquery\n```
          NOTE: Provide an accurate SQL query with the proper format.
          NOTE: Remember you can never create or update the tables you can only fetch.
          NOTE: Always cross check your answer, Check if your answer can solve the user query.
          NOTE: Always keep the query short and up to the mark, also don't add any information into the query from your side.
            """
        else:
            raise KeyError

    def validate_answer(self):
        prompt_text = self.__prompt_text__("VALIDATE_ANSWER")
        prompt = ChatPromptTemplate.from_template(
            prompt_text)
        inputs = {
            "sql_query": lambda x: self.query,
            "query_results": lambda x: self.query_results,
            "user_input": lambda x: self.user_input
        }
        chain = inputs | prompt | self.__llm__() | StrOutputParser()
        response = chain.invoke({})
        return response
    
    def formatter(self):
        prompt_text = self.__prompt_text__("OUTPUT")
        prompt = ChatPromptTemplate.from_template(
            prompt_text)
        inputs = {
            "sql_query": lambda x: self.query,
            "query_results": lambda x: self.query_results,
            "user_input": lambda x: self.user_input
        }
        chain = inputs | prompt | self.__llm__() | StrOutputParser()
        response = chain.invoke({})
        return response
 
    def find_error(self):
        prompt_text = self.__prompt_text__("FIND_ERROR")
        prompt = ChatPromptTemplate.from_template(
            prompt_text + """Database Information: {context}
            User Input: {user_input}
            """)
        inputs = {
            "context": lambda x: self.db_table_info,
            "query_generated": lambda x: self.query,
            "user_input": lambda x: self.user_input,
            "error_due_to_query": lambda x : self.query_error
        }
        chain = inputs | prompt | self.__llm__() | StrOutputParser()
        
        response = chain.invoke({})
        return response
    
if __name__ == '__main__':
    llm_validator = QueryAssuringUtilities(
        query='SELECT t.Name AS TrackName, a.Title AS AlbumTitle FROM tracks t JOIN albums a ON t.AlbumId = a.AlbumId;',
        query_results='TrackName\tAlbumTitle\nFor Those About To Rock (We Salute You)\tFor Those About To Rock We Salute You\nPut The Finger On You\tFor Those About To Rock We Salute You\nLet\'s Get It Up\tFor Those About To Rock We Salute You\nInject The Venom\tFor Those About To Rock We Salute You\nSnowballed\tFor Those About To Rock We Salute You',
        # user_input='Get the email addresses of customers who either don\'t have a fax number or have a fax number ending with 1234.',
        user_input='List all tracks along with their album names.',
        model='llama3',
        query_error='None',
        db_table_info="""CREATE TABLE albums (
        "AlbumId" INTEGER NOT NULL, 
        "Title" NVARCHAR(160) NOT NULL, 
        "ArtistId" INTEGER NOT NULL, 
        PRIMARY KEY ("AlbumId"), 
        FOREIGN KEY("ArtistId") REFERENCES artists ("ArtistId")
)

/*
3 rows from albums table:
AlbumId Title   ArtistId
1       For Those About To Rock We Salute You   1
2       Balls to the Wall       2
3       Restless and Wild       2
*/


CREATE TABLE artists (
        "ArtistId" INTEGER NOT NULL, 
        "Name" NVARCHAR(120), 
        PRIMARY KEY ("ArtistId")
)

/*
3 rows from artists table:
ArtistId        Name
1       AC/DC
2       Accept
3       Aerosmith
*/


CREATE TABLE customers (
        "CustomerId" INTEGER NOT NULL, 
        "FirstName" NVARCHAR(40) NOT NULL, 
        "LastName" NVARCHAR(20) NOT NULL, 
        "Company" NVARCHAR(80), 
        "Address" NVARCHAR(70), 
        "City" NVARCHAR(40), 
        "State" NVARCHAR(40), 
        "Country" NVARCHAR(40), 
        "PostalCode" NVARCHAR(10), 
        "Phone" NVARCHAR(24), 
        "Fax" NVARCHAR(24), 
        "Email" NVARCHAR(60) NOT NULL, 
        "SupportRepId" INTEGER, 
        PRIMARY KEY ("CustomerId"), 
        FOREIGN KEY("SupportRepId") REFERENCES employees ("EmployeeId")
)

/*
3 rows from customers table:
CustomerId      FirstName       LastName        Company Address City    State   Country PostalCode      Phone   Fax     Email   SupportRepId
1       Luís    Gonçalves       Embraer - Empresa Brasileira de Aeronáutica S.A.        Av. Brigadeiro Faria Lima, 2170 São José dos Campos     SP      Brazil  12227-000       +55 (12) 3923-5555  +55 (12) 3923-5566       luisg@embraer.com.br    3
2       Leonie  Köhler  None    Theodor-Heuss-Straße 34 Stuttgart       None    Germany 70174   +49 0711 2842222        None    leonekohler@surfeu.de   5
3       François        Tremblay        None    1498 rue Bélanger       Montréal        QC      Canada  H2G 1A7 +1 (514) 721-4711       None    ftremblay@gmail.com     3
*/


CREATE TABLE employees (
        "EmployeeId" INTEGER NOT NULL, 
        "LastName" NVARCHAR(20) NOT NULL, 
        "FirstName" NVARCHAR(20) NOT NULL, 
        "Title" NVARCHAR(30), 
        "ReportsTo" INTEGER, 
        "BirthDate" DATETIME, 
        "HireDate" DATETIME, 
        "Address" NVARCHAR(70), 
        "City" NVARCHAR(40), 
        "State" NVARCHAR(40), 
        "Country" NVARCHAR(40), 
        "PostalCode" NVARCHAR(10), 
        "Phone" NVARCHAR(24), 
        "Fax" NVARCHAR(24), 
        "Email" NVARCHAR(60), 
        PRIMARY KEY ("EmployeeId"), 
        FOREIGN KEY("ReportsTo") REFERENCES employees ("EmployeeId")
)

/*
3 rows from employees table:
EmployeeId      LastName        FirstName       Title   ReportsTo       BirthDate       HireDate        Address City    State   Country PostalCode      Phone   Fax     Email
1       Adams   Andrew  General Manager None    1962-02-18 00:00:00     2002-08-14 00:00:00     11120 Jasper Ave NW     Edmonton        AB      Canada  T5K 2N1 +1 (780) 428-9482       +1 (780) 428-3457    andrew@chinookcorp.com
2       Edwards Nancy   Sales Manager   1       1958-12-08 00:00:00     2002-05-01 00:00:00     825 8 Ave SW    Calgary AB      Canada  T2P 2T3 +1 (403) 262-3443       +1 (403) 262-3322       nancy@chinookcorp.com
3       Peacock Jane    Sales Support Agent     2       1973-08-29 00:00:00     2002-04-01 00:00:00     1111 6 Ave SW   Calgary AB      Canada  T2P 5M5 +1 (403) 262-3443       +1 (403) 262-6712   jane@chinookcorp.com
*/


CREATE TABLE genres (
        "GenreId" INTEGER NOT NULL, 
        "Name" NVARCHAR(120), 
        PRIMARY KEY ("GenreId")
)

/*
3 rows from genres table:
GenreId Name
1       Rock
2       Jazz
3       Metal
*/


CREATE TABLE invoice_items (
        "InvoiceLineId" INTEGER NOT NULL, 
        "InvoiceId" INTEGER NOT NULL, 
        "TrackId" INTEGER NOT NULL, 
        "UnitPrice" NUMERIC(10, 2) NOT NULL, 
        "Quantity" INTEGER NOT NULL, 
        PRIMARY KEY ("InvoiceLineId"), 
        FOREIGN KEY("TrackId") REFERENCES tracks ("TrackId"), 
        FOREIGN KEY("InvoiceId") REFERENCES invoices ("InvoiceId")
)

/*
3 rows from invoice_items table:
InvoiceLineId   InvoiceId       TrackId UnitPrice       Quantity
1       1       2       0.99    1
2       1       4       0.99    1
3       2       6       0.99    1
*/


CREATE TABLE invoices (
        "InvoiceId" INTEGER NOT NULL, 
        "CustomerId" INTEGER NOT NULL, 
        "InvoiceDate" DATETIME NOT NULL, 
        "BillingAddress" NVARCHAR(70), 
        "BillingCity" NVARCHAR(40), 
        "BillingState" NVARCHAR(40), 
        "BillingCountry" NVARCHAR(40), 
        "BillingPostalCode" NVARCHAR(10), 
        "Total" NUMERIC(10, 2) NOT NULL, 
        PRIMARY KEY ("InvoiceId"), 
        FOREIGN KEY("CustomerId") REFERENCES customers ("CustomerId")
)

/*
3 rows from invoices table:
InvoiceId       CustomerId      InvoiceDate     BillingAddress  BillingCity     BillingState    BillingCountry  BillingPostalCode       Total
1       2       2009-01-01 00:00:00     Theodor-Heuss-Straße 34 Stuttgart       None    Germany 70174   1.98
2       4       2009-01-02 00:00:00     Ullevålsveien 14        Oslo    None    Norway  0171    3.96
3       8       2009-01-03 00:00:00     Grétrystraat 63 Brussels        None    Belgium 1000    5.94
*/


CREATE TABLE media_types (
        "MediaTypeId" INTEGER NOT NULL, 
        "Name" NVARCHAR(120), 
        PRIMARY KEY ("MediaTypeId")
)

/*
3 rows from media_types table:
MediaTypeId     Name
1       MPEG audio file
2       Protected AAC audio file
3       Protected MPEG-4 video file
*/


CREATE TABLE playlist_track (
        "PlaylistId" INTEGER NOT NULL, 
        "TrackId" INTEGER NOT NULL, 
        PRIMARY KEY ("PlaylistId", "TrackId"), 
        FOREIGN KEY("TrackId") REFERENCES tracks ("TrackId"), 
        FOREIGN KEY("PlaylistId") REFERENCES playlists ("PlaylistId")
)

/*
3 rows from playlist_track table:
PlaylistId      TrackId
1       3402
1       3389
1       3390
*/


CREATE TABLE playlists (
        "PlaylistId" INTEGER NOT NULL, 
        "Name" NVARCHAR(120), 
        PRIMARY KEY ("PlaylistId")
)

/*
3 rows from playlists table:
PlaylistId      Name
1       Music
2       Movies
3       TV Shows
*/


CREATE TABLE tracks (
        "TrackId" INTEGER NOT NULL, 
        "Name" NVARCHAR(200) NOT NULL, 
        "AlbumId" INTEGER, 
        "MediaTypeId" INTEGER NOT NULL, 
        "GenreId" INTEGER, 
        "Composer" NVARCHAR(220), 
        "Milliseconds" INTEGER NOT NULL, 
        "Bytes" INTEGER, 
        "UnitPrice" NUMERIC(10, 2) NOT NULL, 
        PRIMARY KEY ("TrackId"), 
        FOREIGN KEY("MediaTypeId") REFERENCES media_types ("MediaTypeId"), 
        FOREIGN KEY("GenreId") REFERENCES genres ("GenreId"), 
        FOREIGN KEY("AlbumId") REFERENCES albums ("AlbumId")
)

/*
3 rows from tracks table:
TrackId Name    AlbumId MediaTypeId     GenreId Composer        Milliseconds    Bytes   UnitPrice
1       For Those About To Rock (We Salute You) 1       1       1       Angus Young, Malcolm Young, Brian Johnson       343719  11170334        0.99
2       Balls to the Wall       2       2       1       None    342562  5510424 0.99
3       Fast As a Shark 3       2       1       F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman     230619  3990994 0.99
*/
"""

    )

    print(llm_validator.formatter())