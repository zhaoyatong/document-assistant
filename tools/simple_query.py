from datetime import datetime
from typing import List, Dict, Any

from utils.db_helper import DBHelper


class SqliteQueryTool:
    @staticmethod
    def get_all_documents() -> List[Dict[str, Any]]:
        """
        获取所有的文档和其分类

        :return: classification为分类名称，name为文档名称，未查到结果返回[]
        """

        sql = (
            "SELECT classification.name as classification,documents.name FROM documents "
            "INNER JOIN classification "
            "ON documents.classification_id = classification.id"
        )

        db_result = DBHelper.query_by_sql(sql)

        return db_result

    @staticmethod
    def get_documents_by_classification(classification: str) -> List[Dict[str, Any]]:
        """
        根据分类获取所有的文档

        :param classification: 分类名称
        :return:包含所有文档名称的集合
        """

        sql = (
            "SELECT documents.name FROM documents "
            "INNER JOIN classification "
            "ON documents.classification_id = classification.id "
            "WHERE classification.name == ?"
        )

        db_result = DBHelper.query_by_sql(sql, params=(classification,))

        return db_result

    @staticmethod
    def get_all_classification() -> List[Dict[str, Any]]:
        """
        获取所有分类

        :return:包含所有文档名称的集合
        """

        sql = (
            "SELECT classification.name FROM classification "
        )

        db_result = DBHelper.query_by_sql(sql)

        return db_result

    @staticmethod
    def get_documents_by_date(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        根据上传时间获取所有的文档

        :param start_date: 上传时间筛选的开始时间
        :param end_date:上传时间筛选的结束时间
        :return:包含所有文档名称的集合
        """

        sql = (
            "SELECT documents.name FROM documents WHERE upload_time BETWEEN ? AND ?"
        )

        db_result = DBHelper.query_by_sql(sql, params=(start_date, end_date))

        return db_result

    @staticmethod
    def get_documents_by_classification_and_date(classification: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        根据分类和上传时间获取所有的文档

        :param classification: 分类名称
        :param start_date: 上传时间筛选的开始时间
        :param end_date:上传时间筛选的结束时间
        :return:包含所有文档名称的集合
        """

        sql = (
            "SELECT documents.name FROM documents "
            "INNER JOIN classification "
            "ON documents.classification_id = classification.id "
            "WHERE classification.name == ? AND upload_time BETWEEN ? AND ?"
        )

        db_result = DBHelper.query_by_sql(sql, params=(classification, start_date, end_date))

        return db_result
