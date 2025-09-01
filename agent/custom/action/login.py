import json
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger


@AgentServer.custom_action("OverrideLoginInfo")
class OverrideLoginInfo(CustomAction):
    """
    在登录角色任务中使用，重写账号角色信息
    """

    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult:
        # logger.debug(f"OverrideLoginInfo argv.custom_action_param: {argv.custom_action_param}")
        cus_param = json.loads(argv.custom_action_param)

        account = cus_param["account"]
        platform = cus_param["platform"]
        servername = cus_param["servername"]

        context.override_pipeline(
            {"TASK-A-3-0识别到当前账号就是要登录的账号": {"expected": account}}
        )
        context.override_pipeline(
            {"TASK-A-4找到匹配的账号了并点击": {"expected": account}}
        )

        context.override_pipeline(
            {
                "TASK-A-6检测平台按钮并点击": {
                    "template": "平台区服/" + platform + ".png"
                }
            }
        )

        context.override_pipeline(
            {"TASK-A-7-0识别到当前区服就是要登录的区服": {"expected": servername}}
        )
        context.override_pipeline(
            {
                "TASK-A-9查找区服图标并点击选择该角色": {
                    "template": "平台区服/" + servername + ".png"
                }
            }
        )
        logger.info(
            f"#OverrideLoginInfoAction# 覆写登录账号为：{account}, 平台：{platform}, 区服：{servername}"
        )

        return CustomAction.RunResult(success=True)
