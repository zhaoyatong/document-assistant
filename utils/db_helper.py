import os
import sqlite3
from typing import List, Dict, Optional, Any


class DBHelper:
    # 获取当前文件的目录，然后返回上一级目录，再拼接 db 文件名
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _parent_dir = os.path.dirname(_current_dir)  # 获取上级目录
    _db_path = os.path.join(_parent_dir, "document.db")  # 拼接路径

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(cls._db_path)
        conn.row_factory = sqlite3.Row  # 使返回的行像字典一样可访问
        return conn

    @staticmethod
    def _execute(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        执行SQL语句
        :param conn: 数据库连接
        :param sql: SQL语句
        :param params: 参数元组
        :return: 游标对象
        """
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            conn.rollback()
            raise e

    @classmethod
    def get_all_tables(cls) -> List[str]:
        """获取数据库中所有表名"""
        with cls._get_connection() as conn:
            cursor = cls._execute(conn,
                                  "SELECT name FROM sqlite_master WHERE type='table' and name != 'sqlite_sequence'")
            return [row['name'] for row in cursor.fetchall()]

    @classmethod
    def get_table_columns(cls, table_name: str) -> List[str]:
        """获取表的列名"""
        with cls._get_connection() as conn:
            cursor = cls._execute(conn, f"PRAGMA table_info({table_name})")
            return [row['name'] for row in cursor.fetchall()]

    @classmethod
    def query_all(cls, table_name: str) -> List[Dict[str, Any]]:
        """
        查询表中所有数据
        :param table_name: 表名
        :return: 包含所有行的列表，每行是一个字典
        """
        with cls._get_connection() as conn:
            cursor = cls._execute(conn, f"SELECT * FROM {table_name}")
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def query_one(cls, table_name: str, condition: str = "", params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        查询单条数据
        :param table_name: 表名
        :param condition: WHERE条件语句（不包含WHERE关键字）
        :param params: 条件参数
        :return: 单行数据字典或None
        """
        with cls._get_connection() as conn:
            sql = f"SELECT * FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            sql += " LIMIT 1"

            cursor = cls._execute(conn, sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    @classmethod
    def query_many(cls, table_name: str, condition: str = "", params: tuple = (), limit: int = 100) -> List[
        Dict[str, Any]]:
        """
        查询多条数据
        :param table_name: 表名
        :param condition: WHERE条件语句（不包含WHERE关键字）
        :param params: 条件参数
        :param limit: 返回的最大行数
        :return: 包含行的列表，每行是一个字典
        """
        with cls._get_connection() as conn:
            sql = f"SELECT * FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            sql += f" LIMIT {limit}"

            cursor = cls._execute(conn, sql, params)
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def insert(cls, table_name: str, data: Dict[str, Any]) -> int:
        """
        插入数据
        :param table_name: 表名
        :param data: 要插入的数据字典
        :return: 插入行的ID
        """
        with cls._get_connection() as conn:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            cursor = cls._execute(conn, sql, tuple(data.values()))
            return cursor.lastrowid

    @classmethod
    def update(cls, table_name: str, data: Dict[str, Any], condition: str = "", params: tuple = ()) -> int:
        """
        更新数据
        :param table_name: 表名
        :param data: 要更新的数据字典
        :param condition: WHERE条件语句（不包含WHERE关键字）
        :param params: 条件参数
        :return: 影响的行数
        """
        with cls._get_connection() as conn:
            set_clause = ', '.join([f"{key}=?" for key in data.keys()])
            sql = f"UPDATE {table_name} SET {set_clause}"
            if condition:
                sql += f" WHERE {condition}"

            values = tuple(data.values()) + params
            cursor = cls._execute(conn, sql, values)
            return cursor.rowcount

    @classmethod
    def delete(cls, table_name: str, condition: str = "", params: tuple = ()) -> int:
        """
        删除数据
        :param table_name: 表名
        :param condition: WHERE条件语句（不包含WHERE关键字）
        :param params: 条件参数
        :return: 影响的行数
        """
        with cls._get_connection() as conn:
            sql = f"DELETE FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"

            cursor = cls._execute(conn, sql, params)
            return cursor.rowcount

    @classmethod
    def query_by_sql(cls, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        通过sql查询结果
        :param sql: SQL
        :param params: 条件参数
        :return: 包含行的列表，每行是一个字典
        """
        with cls._get_connection() as conn:
            cursor = cls._execute(conn, sql, params)
            return [dict(row) for row in cursor.fetchall()]
