import json
from time import sleep
from datetime import datetime
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils.account import find_role_info, get_all_rolenames
from utils import logger


@AgentServer.custom_action("RunTaskList")
class RunTaskList(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:
        logger.debug(f"argv.custom_action_param: {argv.custom_action_param}")
        cus_param = json.loads(argv.custom_action_param)

        tasks = cus_param["tasks"]
        logger.info(f"#RunTaskList# 传入的 tasks 参数为：{tasks}")

        for task in tasks:
            task_detail = context.run_task(task["taskname"])
            sleep(task["wait"])


@AgentServer.custom_action("ForRolesToRunTask")
class ForRolesToRunTask(CustomAction):

    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:
        logger.debug(f"argv.custom_action_param: {argv.custom_action_param}")
        cus_param = json.loads(argv.custom_action_param)
        logger.debug(f"cus_param： {cus_param}")

        tasks = cus_param["tasks"]
        logger.info(f"#ForRolesToRunTask# 传入的 tasks 参数为：{tasks}")

        rolenames_str = cus_param["rolenames"]
        logger.info(
            f"传入的 rolenames_str 参数：{rolenames_str}, 类型为：{type(rolenames_str)}"
        )

        if type(rolenames_str) == str:
            try:
                rolenames = eval(rolenames_str)
                logger.debug(f"eval 成功，结果：{rolenames}")
            except Exception as e:
                logger.debug(
                    f"rolenames_str 参数转换为列表失败: {str(e)}，尝试解析逗号分隔的格式",
                    exc_info=True,
                )
                rolenames = rolenames_str.split(",")
        elif type(rolenames_str) == list:
            rolenames = rolenames_str
        else:
            rolenames = []

        all_num = len(rolenames)
        logger.info(f"解析后的角色数量：{all_num}, 角色名：{rolenames}")

        if rolenames and rolenames[0] == "ALL":
            rolenames = get_all_rolenames()

        for index, rolename in enumerate(rolenames):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"{now} 当前任务角色 {rolename}, {index}/{all_num}")
            info = find_role_info(rolename)
            if not info:
                continue

            context.override_pipeline(
                {
                    "重写账号角色信息": {
                        "custom_action_param": {
                            "account": info["account"],
                            "platform": info["platform"],
                            "servername": info["servername"],
                        }
                    }
                }
            )

            for task in tasks:
                task_detail = context.run_task(task["taskname"])
                # print("##Task Detail##", task_detail)
                sleep(task["wait"])

        context.run_task("TASK-关闭游戏")
