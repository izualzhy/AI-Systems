#!/usr/bin/env python
# coding=utf-8
import sys
import os

from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent



from operator import itemgetter

from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from utils.util import getDeepSeekR1, getDoubaoSeed16, getDoubaoSeed16Vision

db = SQLDatabase.from_uri("mysql+pymysql://root:1234@localhost:3306/test")
llm = getDoubaoSeed16Vision()


def test_sql_query_chain():
    def clean_sql_query(query_str: str) -> str:
        """Cleans the SQL query string from unwanted prefixes."""
        # The LLM sometimes adds a prefix like "SQLQuery: " to the query.
        # This function removes it before execution.
        sql_query_str = query_str
        if "SQLQuery:" in query_str:
            sql_query_str = query_str.split("SQLQuery:")[-1].strip()
        if "SQLResult:" in query_str:
            sql_query_str = sql_query_str.split("SQLResult:")[0].strip()
        print("sql_query_str: " + sql_query_str)
        return sql_query_str.strip()


    # Add a cleaning step to the chain
    query_cleaner = RunnableLambda(clean_sql_query)

    # 执行查询动作
    execute_query = QuerySQLDataBaseTool(db=db)
    # 获取sql 查询语句
    write_query = create_sql_query_chain(llm, db)

    # chain = write_query
    # response = chain.invoke({"question": "How many users are there"})
    # print("only write_query : \n" + response)
    # print("---------------------------\n")
    # #
    # # 先生成查询语句，再执行查询动作
    # print("--- Running first chain ---")
    # chain = write_query | query_cleaner | execute_query
    # response = chain.invoke({"question": "How many users are there"})
    # print("write_query | query_cleaner | execute_query : \n" + response)


    # 定义提示词，其中有 question、query、result 三个变量
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

    answer = answer_prompt | llm | StrOutputParser()
    # query通过write_query链的执行结果获取
    # result 通过 execute_query链获取
    chain = (
            RunnablePassthrough.assign(query=write_query | query_cleaner).assign(
                result=itemgetter("query") | execute_query
            )
            | answer
    )
    print("--- Running second chain ---")
    print(chain.invoke({"question": "How many rows does the table agent_to_tables have?"}))
    print("----------------------------")

def test_sql_agent():
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True
    )
    agent_executor.run("How many rows does the table agent_to_tables have?")


if __name__ == '__main__':
    test_sql_agent()

