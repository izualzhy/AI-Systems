#!/usr/bin/env python
# coding=utf-8


# 设置OpenAI API密钥
# 导入所需的库和模块
from collections import deque
from typing import Dict, List, Optional, Any

import faiss
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.vectorstores.base import VectorStore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field

from doubao_embedding import DoubaoEmbedding
from misc import getDoubaoSeed16Thinking

# 定义嵌入模型
doubao_embedding = DoubaoEmbedding()

# 初始化向量数据库
# embedding_size = 1536
embedding_size = len(doubao_embedding.embed_query("test"))
print(f"embedding_size: {embedding_size}")
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embedding_function=doubao_embedding, index=index, docstore=InMemoryDocstore({}), index_to_docstore_id={})

# 定义任务生成链
class TaskCreationChain(LLMChain):
    """负责生成任务的链"""
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """从大模型获取响应解析器"""
        task_creation_template = (
            "You are a task creation AI that uses the result of an execution agent"
            " to create new tasks with the following objective: {objective},"
            " The last completed task has the result: {result}."
            " This result was based on this task description: {task_description}."
            " These are incomplete tasks: {incomplete_tasks}."
            " Based on the result, create new tasks to be completed"
            " by the AI system that do not overlap with incomplete tasks."
            " Return the tasks as an array."
            "**Important constraints:**  "
            "- Each task must be written in Chinese.  "
            "- **Each task should be concise and no longer than 10 Chinese characters.**  "
            "- Avoid overlapping content with any existing incomplete tasks."
        )
        prompt = PromptTemplate(
            template=task_creation_template,
            input_variables=[
                "result",
                "task_description",
                "incomplete_tasks",
                "objective",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)

# 定义任务优先级链
class TaskPrioritizationChain(LLMChain):
    """负责任务优先级排序的链"""
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """从大模型获取响应解析器"""
        task_prioritization_template = (
            "You are a task prioritization AI tasked with cleaning the formatting of and reprioritizing"
            " the following tasks: {task_names}."
            " Consider the ultimate objective of your team: {objective}."
            " Do not remove any tasks. Return the result as a numbered list, like:"
            " 1. First task"
            " 2. Second task"
            "**Important:**  "
            "- Start the task list with number **{next_task_id}**.  "
            "- Each subsequent task must increment the number by **1** (i.e., strictly increasing by 1).  "
            "- Do **not** skip or reuse numbers."
            ""
            "Only return the final cleaned and renumbered list."
        )
        prompt = PromptTemplate(
            template=task_prioritization_template,
            input_variables=["task_names", "next_task_id", "objective"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)

# 定义任务执行链
class ExecutionChain(LLMChain):
    """负责执行任务的链"""
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """从大模型获取响应解析器"""
        execution_template = (
            "You are an AI who performs one task based on the following objective: {objective}."
            " Take into account these previously completed tasks: {context}."
            " Your task: {task}."
            " Response:"
            "**Please keep the response as concise and direct as possible.**"
            "Avoid unnecessary explanations, verbose descriptions, or redundant phrasing."
        )
        prompt = PromptTemplate(
            template=execution_template,
            input_variables=["objective", "context", "task"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)

# 获取下一个任务
def get_next_task(
        task_creation_chain: LLMChain,
        result: Dict,
        task_description: str,
        task_list: List[str],
        objective: str,
) -> List[Dict]:
    """Get the next task."""
    log_print(f"get_next_task objective:{objective} task_description: {task_description}")
    incomplete_tasks = ", ".join(task_list)
    log_print(f"get_next_task \n\tresult: {result}")
    log_print(f"get_next_task \n\ttask_description: {task_description}")
    log_print(f"get_next_task \n\tincomplete_tasks: {incomplete_tasks}")
    log_print(f"get_next_task \n\tobjective: {objective}")
    response = task_creation_chain.run(
        result=result,
        task_description=task_description,
        incomplete_tasks=incomplete_tasks,
        objective=objective,
    )
    log_print(f"get_next_task \n\tresponse: {response}")
    new_tasks = response.split("\n")
    log_print(f"get_next_task, parse new_tasks from response, new_tasks:")
    for t in new_tasks:
        log_print(f"\tnew_task: {t}")
    return [{"task_name": task_name} for task_name in new_tasks if task_name.strip()]
# 设置任务优先级
def prioritize_tasks(
        task_prioritization_chain: LLMChain,
        this_task_id: int,
        task_list: List[Dict],
        objective: str,
) -> List[Dict]:
    """Prioritize tasks."""
    task_names = [t["task_name"] for t in task_list]
    next_task_id = int(this_task_id) + 1
    log_print("prioritize_tasks")
    for task_name in task_names:
        log_print(f"prioritize_tasks task_name: {task_name}")
    log_print(f"prioritize_tasks task_names: {task_names} next_task_id: {next_task_id} objective: {objective}")
    response = task_prioritization_chain.run(
        task_names=task_names, next_task_id=next_task_id, objective=objective
    )
    log_print(f"prioritize_tasks response: {response}")
    new_tasks = response.split("\n")
    log_print(f"prioritize_tasks")
    prioritized_task_list = []
    for task_string in new_tasks:
        log_print(f"\ttask_string: {task_string}")
        if not task_string.strip():
            continue
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = task_parts[0].strip()
            task_name = task_parts[1].strip()
            prioritized_task_list.append({"task_id": task_id, "task_name": task_name})
    return prioritized_task_list
# 获取头部任务
def _get_top_tasks(vectorstore, query: str, k: int) -> List[str]:
    """Get the top k tasks based on the query."""
    log_print(f'_get_top_tasks query: {query} k: {k}')
    results = vectorstore.similarity_search_with_score(query, k=k)
    if not results:
        log_print(f'got no results from vectorstore')
        return []
    sorted_results, _ = zip(*sorted(results, key=lambda x: x[1], reverse=True))
    for i in sorted_results:
        log_print(f'_get_top_tasks item: {i}')
    return [str(item.metadata["task"]) for item in sorted_results]
# 执行任务
def execute_task(
        vectorstore, execution_chain: LLMChain, objective: str, task: str, k: int = 5
) -> str:
    """Execute a task."""
    context = _get_top_tasks(vectorstore, query=objective, k=k)
    log_print(f"execute_task objective:{objective} context: {context} task: {task}")
    return execution_chain.run(objective=objective, context=context, task=task)

f = open("babyagi_round.out", "w")
def log_print(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, **kwargs, file=f)

def dump_vector_store():
    log_print("dump_vector_store")
    data = {}
    i = 1
    for doc_id in vectorstore.index_to_docstore_id.values():
        doc = vectorstore.docstore.search(doc_id)
        data[doc_id] = doc
        log_print(f"\ti: {i}")
        log_print(f"\t\tdoc_id: {doc_id}")
        log_print(f"\t\tcontent: {doc.page_content}")
        log_print(f"\t\tmetadata: {doc.metadata}")
        i += 1

# BabyAGI 主类
class BabyAGI(Chain, BaseModel):
    """BabyAGI Agent的控制器模型"""
    task_list: deque = Field(default_factory=deque)
    task_creation_chain: TaskCreationChain = Field(...)
    task_prioritization_chain: TaskPrioritizationChain = Field(...)
    execution_chain: ExecutionChain = Field(...)
    task_id_counter: int = Field(1)
    vectorstore: VectorStore = Field(init=False)
    max_iterations: Optional[int] = None
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
    def add_task(self, task: Dict):
        log_print(f"add_task task: {task}")
        self.task_list.append(task)
    def print_task_list(self):
        log_print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
        for t in self.task_list:
            log_print(str(t["task_id"]) + ": " + t["task_name"])
    def print_next_task(self, task: Dict):
        log_print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
        log_print(str(task["task_id"]) + ": " + task["task_name"])
    def print_task_result(self, result: str):
        log_print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
        log_print(result)
    @property
    def input_keys(self) -> List[str]:
        return ["objective"]
    @property
    def output_keys(self) -> List[str]:
        return []

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent."""
        objective = inputs["objective"]
        first_task = inputs.get("first_task", "Make a todo list")
        log_print(f"Running with objective: {objective} first_task: {first_task}")
        self.add_task({"task_id": 1, "task_name": first_task})
        num_iters = 0
        global f

        while True:
            if f:
                f.close()
            f = open(f"./babyagi_round_{num_iters}.out", "w")
            log_print("\n" + "-" * 16 + f"Running loop: {num_iters}" + "-" * 16 + "\n")
            log_print("current task in task_list")
            for i in self.task_list:
                log_print(f"\ti : {i}")
            if self.task_list:
                self.print_task_list()
                # 第1步：获取第一个任务
                task = self.task_list.popleft()
                log_print(f"we got a task: {task}")
                self.print_next_task(task)
                # 第2步：执行任务
                result = execute_task(
                    self.vectorstore, self.execution_chain, objective, task["task_name"]
                )
                log_print(f"current task: {task}")
                this_task_id = int(task["task_id"])
                self.print_task_result(result)
                # 第3步：将结果存储到向量数据库中
                result_id = f"result_{task['task_id']}_{num_iters}"
                log_print(f"add_texts to vectorstore...\n\ttexts=[{result}]\n\tmetadatas:{[{"task": task["task_name"]}]}\n\tids=[{result_id}]")
                self.vectorstore.add_texts(
                    texts=[result],
                    metadatas=[{"task": task["task_name"]}],
                    ids=[result_id],
                )
                # 第4步：创建新任务并重新根据优先级排到任务列表中
                new_tasks = get_next_task(
                    self.task_creation_chain,
                    result,
                    task["task_name"],
                    [t["task_name"] for t in self.task_list],
                    objective,
                )
                for new_task in new_tasks:
                    self.task_id_counter += 1
                    new_task.update({"task_id": self.task_id_counter})
                    self.add_task(new_task)
                self.task_list = deque(
                    prioritize_tasks(
                        self.task_prioritization_chain,
                        this_task_id,
                        list(self.task_list),
                        objective,
                    )
                )
                log_print("tasks after priority:")
                for t in self.task_list:
                    log_print(f"\ttask: {t}")
                dump_vector_store()
            num_iters += 1
            f.close()
            f = open(f"./babyagi_round_{num_iters}.out", "w")
            if self.max_iterations is not None and num_iters == self.max_iterations:
                log_print(
                    f"\033[91m\033[1m" + "\n*****TASK ENDING {num_iters} {self.max_iterations}*****\n" + "\033[0m\033[0m"
                )
                break
        return {}
    @classmethod
    def from_llm(
            cls, llm: BaseLLM, vectorstore: VectorStore, verbose: bool = False, **kwargs
    ) -> "BabyAGI":
        """Initialize the BabyAGI Controller."""
        task_creation_chain = TaskCreationChain.from_llm(llm, verbose=verbose)
        task_prioritization_chain = TaskPrioritizationChain.from_llm(
            llm, verbose=verbose
        )
        execution_chain = ExecutionChain.from_llm(llm, verbose=verbose)
        return cls(
            task_creation_chain=task_creation_chain,
            task_prioritization_chain=task_prioritization_chain,
            execution_chain=execution_chain,
            vectorstore=vectorstore,
            **kwargs,
        )

# 主函数执行部分
if __name__ == "__main__":
    OBJECTIVE = "分析一下北京市今天的天气，写出花卉存储策略"
    llm = getDoubaoSeed16Thinking()
    verbose = False
    max_iterations: Optional[int] = 6
    baby_agi = BabyAGI.from_llm(llm=llm, vectorstore=vectorstore,
                                verbose=verbose,
                                max_iterations=max_iterations)
    baby_agi({"objective": OBJECTIVE})