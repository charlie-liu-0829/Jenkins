import allure


class Allure_util(object):

    @staticmethod
    def set_allure(case_info):
        feature = case_info.get("feature", "未分类")
        story = case_info.get("story", "未分类")
        title = case_info.get("title", "未命名用例")
        allure.dynamic.feature(feature)
        allure.dynamic.story(story)
        allure.dynamic.title(title)
