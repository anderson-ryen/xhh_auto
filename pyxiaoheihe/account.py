'''
# @Author       : Chr_
# @Date         : 2020-07-30 16:29:34
# @LastEditors  : Chr_
# @LastEditTime : 2020-08-01 22:25:28
# @Description  : 账号模块,负责[我]TAB下的内容
'''


from .network import Network
from .static import HEYBOX_VERSION, URLS, BString
from .error import *


class Account(Network):
    '账号模块,负责[我]TAB下的内容'

    def __init__(self, account: dict, hbxcfg: dict, tag: str):
        super().__init__(account, hbxcfg, tag)

    def debug(self):
        super().debug()
        self.get_daily_task()

    def get_heybox_latest_version(self) -> str:
        '''获取小黑盒最新版本号,失败返回False

        返回:
            str: 小黑盒版本号
        '''
        url = URLS.HEYBOX_VERSION_CHECK
        try:
            result = self._get(url=url)
            version = result['version']
            message = result['msg']
            self.logger.debug(f'小黑盒最新版本为[{version}] - [{message}]')
            return(version)
        except (ClientException, KeyError, NameError) as e:
            self.logger.error(f'获取小黑盒最新版本出错[{e}]')
            return(False)

    def get_user_profile(self, userid: int = 0) -> (int, int, int):
        '''获取个人资料,失败返回False

        参数:
            [userid]: 用户id,不填代入自己的id
        返回:
            follow_num:关注数
            fan_num:粉丝数
            awd_num:获赞数
        '''
        url = URLS.GET_USER_PROFILE
        params = {'userid': userid or self._heybox_id}
        try:
            result = self._get(url=url, params=params)

            ad = result['account_detail']
            bi = ad['bbs_info']

            follow = bi['follow_num'] # 关注
            fan = bi['fan_num'] # 粉丝
            like = bi['awd_num'] # 获赞
            level = ad['level_info']['level'] # 等级
            userid = ad['userid'] #用户id
            username = ad['username'] # 用户名

            self.logger.debug(f'昵称:{username} >{userid}< [{level}级]')
            self.logger.debug(f'关注[{follow}] 粉丝[{fan}] 获赞[{like}]')
            return((follow, fan, like))
        except (ClientException, KeyError, NameError) as e:
            self.logger.error(f'[*] 获取用户详情出错 [{e}]')
            return(False)

    def get_unread_count(self) -> (int, int, int, int, int):
        '''获取未读通知计数,失败返回False

        返回:
            like: 新获赞
            comment: 新评论
            follow: 新粉丝
            notify: 新通知
            total: 总计
        '''
        url = URLS.GET_UNREAD_MESSAGE
        params = {'list_type': 2, 'offset': 0}
        try:
            result = self._get(url=url, params=params)
            muu = result['message_unread_num']
            like = muu['award']  # 新获赞
            comment = muu['comment']  # 新评论
            # developer = muu['developer']
            follow = muu['follow']  # 新粉丝
            # friend = muu['friend']  # 大概是私信
            notify = muu['notify']  # 优惠通知
            total = muu['total']  # 总计
            self.logger.debug(f'新获赞[{like}]新评论[{comment}]新粉丝[{follow}]')
            return((like, comment, follow, notify, total))
        except (ClientException, KeyError, NameError) as e:
            self.logger.error(f'[*] 获取任务详情出错 [{e}]')
            return(False)

    def __get_task_json(self) -> dict:
        '''获取任务详情json,出错返回False

        返回:
            dict: json字典
        '''
        url = URLS.GET_TASK_LIST
        result = self._get(url=url)
        return(result)

    def get_daily_task(self) -> (BString, BString, BString, BString):
        '''获取每日任务详情,失败返回False

        返回:
            sign: 签到?
            share_news: 分享新闻?
            share_comment: 分享评论?
            like:点赞?
        '''
        try:
            result = self.__get_task_json()
            tl = result['task_list'][0]['tasks']
            sign = BString(tl[0]['state'] == 'finish')
            share_news = BString(tl[1]['state'] == 'finish')
            share_comment = BString(tl[2]['state'] == 'finish')
            like = BString(tl[3]['state'] == 'finish')

            self.logger.debug(
                f"签到{sign}|分享{share_news}|{share_comment}|点赞{like}")
            return((sign, share_news, share_comment, like))
        except (ClientException) as e:
            self.logger.error(f'[*] 获取任务详情出错 [{e}]')
            return(False)
