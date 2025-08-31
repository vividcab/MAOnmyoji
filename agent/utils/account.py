import pandas as pd

from .logger import logger

csv_path = "user_data/account_info.csv"


def find_role_info(rolename):
    """
    根据角色名从CSV文件中查找账号、平台和服务器名信息。

    参数：
        csv_path (str): CSV 文件路径。
        rolename (str): 要查找的角色名。

    返回：
        List[dict]: 每个命中行的信息组成的列表。
                    每个元素是一个 dict，包含 account、platform 和 servername。
    """
    try:
        df = pd.read_csv(csv_path)

        # 检查必要列是否存在
        required_columns = {"account", "platform", "servername", "rolename"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV文件缺少必要列：{required_columns - set(df.columns)}")

        # 查找角色名匹配的行
        matched = df[df["rolename"] == rolename]

        # 将匹配的结果转换为字典列表返回
        result = matched[["account", "platform", "servername"]].to_dict(
            orient="records"
        )
        if not result:
            return []
        else:
            return result[0]

    except FileNotFoundError:
        logger.error(f"文件未找到：{csv_path}")
        return []
    except Exception as e:
        logger.error(f"发生错误：{e}")
        return []


def get_all_rolenames():
    """
    从CSV文件中读取所有角色名，组成一个列表返回。

    返回：
        List[str]: 所有rolename列的值组成的列表。
    """
    try:
        df = pd.read_csv(csv_path)

        if "rolename" not in df.columns:
            raise ValueError("CSV文件中缺少 'rolename' 列")

        # 去除空值并转为列表
        rolenames = df["rolename"].dropna().tolist()
        return rolenames

    except FileNotFoundError:
        logger.error(f"文件未找到：{csv_path}")
        return []
    except Exception as e:
        logger.error(f"发生错误：{e}")
        return []


if __name__ == "__main__":
    print(get_all_rolenames())
