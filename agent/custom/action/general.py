import os
import json
from datetime import datetime
from time import sleep
import random

from PIL import Image
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger
from custom.reco import Count


@AgentServer.custom_action("Screenshot")
class Screenshot(CustomAction):
    """
    自定义截图动作，保存当前屏幕截图到指定目录。

    参数格式:
    {
        "save_dir": "保存截图的目录路径",
        "format": "jpeg 或 png，默认 jpeg",
        "quality": 70,  # jpeg 压缩质量（1-95），仅在 format=jpeg 时生效
        "gray": false   # 是否转为灰度图
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        # image array(BGR)
        screen_array = context.tasker.controller.cached_image

        # Check resolution aspect ratio
        height, width = screen_array.shape[:2]
        aspect_ratio = width / height
        target_ratio = 16 / 9
        # Allow small deviation (within 1%)
        if abs(aspect_ratio - target_ratio) / target_ratio > 0.01:
            logger.error(f"当前模拟器分辨率不是16:9! 当前分辨率: {width}x{height}")

        # BGR2RGB
        if len(screen_array.shape) == 3 and screen_array.shape[2] == 3:
            rgb_array = screen_array[:, :, ::-1]
        else:
            rgb_array = screen_array
            logger.warning("当前截图并非三通道")

        img = Image.fromarray(rgb_array)

        # 解析参数
        params = json.loads(argv.custom_action_param)
        save_dir = params["save_dir"]
        os.makedirs(save_dir, exist_ok=True)

        img_format = params.get("format", "jpeg").lower()
        quality = int(params.get("quality", 70))
        gray = bool(params.get("gray", False))

        # 灰度化
        if gray:
            img = img.convert("L")

        # 文件名
        node_info = context.get_node_data("重写账号角色信息")
        account_info_dict = node_info["action"]["param"]["custom_action_param"]
        now = datetime.now()
        ext = "jpg" if img_format == "jpeg" else "png"
        save_file_path = f"{save_dir}/{self._get_format_timestamp(now)}-{account_info_dict['rolename']}.{ext}"

        # 保存
        if img_format == "jpeg":
            img.save(save_file_path, "JPEG", quality=quality, optimize=True)
        else:
            img.save(save_file_path, "PNG", optimize=True)

        logger.info(f"截图保存至 {save_file_path}")

        context.tasker.get_task_detail(argv.task_detail.task_id)

        return CustomAction.RunResult(success=True)

    def _get_format_timestamp(self, now):

        date = now.strftime("%Y.%m.%d")
        time = now.strftime("%H.%M.%S")
        milliseconds = f"{now.microsecond // 1000:03d}"

        return f"{date}-{time}"


@AgentServer.custom_action("DisableNode")
class DisableNode(CustomAction):
    """
    将特定 node 设置为 disable 状态 。

    参数格式:
    {
        "node_name": "结点名称"
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        node_name = json.loads(argv.custom_action_param)["node_name"]

        context.override_pipeline({f"{node_name}": {"enabled": False}})

        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("NodeOverride")
class NodeOverride(CustomAction):
    """
    在 node 中执行 pipeline_override 。

    参数格式:
    {
        "node_name": {"被覆盖参数": "覆盖值",...},
        "node_name1": {"被覆盖参数": "覆盖值",...}
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        ppover = json.loads(argv.custom_action_param)

        if not ppover:
            logger.warning("No ppover")
            return CustomAction.RunResult(success=True)

        logger.debug(f"NodeOverride: {ppover}")
        context.override_pipeline(ppover)

        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("ResetCount")
class ResetCount(CustomAction):
    """
    重置计数器。

    参数格式:
    {
        "node_name": String # 目标计数器节点名称，不存在时重置全部节点
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        param = json.loads(argv.custom_action_param)
        if not param:
            Count.reset_count()
            return CustomAction.RunResult(success=True)

        node_name = param.get("node_name", None)
        Count.reset_count(node_name)
        logger.info("#ResetCount#：重置 Node 计数器")
        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("RandomSleep")
class RandomSleep(CustomAction):
    """ """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        param = json.loads(argv.custom_action_param)
        t = random.gauss(2, 0.5)
        if t < 0.5:
            t = 30
        if t < 0.8:
            t = 20
        if t < 1:
            t = 10
        # print("sleep: ", t)
        sleep(t)

        return CustomAction.RunResult(success=True)
