# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
from dotenv import load_dotenv

from camel.models import ModelFactory
from camel.toolkits import (
    SearchToolkit,
    WebToolkit,
    FileWriteToolkit,
    TerminalToolkit
)
from camel.types import ModelPlatformType, ModelType
from camel.logger import set_log_level

from utils import OwlRolePlaying, run_society

load_dotenv()
set_log_level(level="DEBUG")
import os
# Get current script directory
base_dir = os.path.dirname(os.path.abspath(__file__))

def construct_society(question: str) -> OwlRolePlaying:
    r"""Construct a society of agents based on the given question.

    Args:
        question (str): The task or question to be addressed by the society.

    Returns:
        OwlRolePlaying: A configured society of agents ready to address the
            question.
    """

    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
        "web": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
    }

    # Configure toolkits
    tools = [
        *WebToolkit(
            headless=False,  # Set to True for headless mode (e.g., on remote servers)
            web_agent_model=models["web"],
            planning_agent_model=models["planning"],
        ).get_tools(),
        SearchToolkit().search_duckduckgo,
        SearchToolkit().search_wiki,
        *FileWriteToolkit(output_dir="./").get_tools(),
        *TerminalToolkit().get_tools(),
    ]

    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {"model": models["assistant"], "tools": tools}

    # Configure task parameters
    task_kwargs = {
        "task_prompt": question,
        "with_task_specify": False,
    }

    # Create and return the society
    society = OwlRolePlaying(
        **task_kwargs,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

    return society


def main():
    r"""Main function to run the OWL system with an example question."""
    # Example research question
    question = f"""打开百度搜索，总结一下camel-ai的camel框架的github star、fork数目等，并把数字用plot包写成python文件保存到"+{os.path.join
(base_dir, 'final_output')}+"，用本地终端执行python文件显示图出来给我"""
#     question=f"""Create 'app.log' in the logs directory at '{os.path.join
# (base_dir, 'logs')}' with content: 'INFO: Application started successfully at 
# 2024-03-10'"""
    # Construct and run the society
    society = construct_society(question)
    answer, chat_history, token_count = run_society(society)

    # Output the result
    print(f"\033[94mAnswer: {answer}\nChat History: {chat_history}\ntoken_count:{token_count}\033[0m")


if __name__ == "__main__":
    main()
